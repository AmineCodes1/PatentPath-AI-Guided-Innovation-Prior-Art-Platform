"""Espacenet OPS connector with retry, quota handling, XML parsing, and Redis caching."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from xml.etree import ElementTree as ET

import epo_ops

from app.core.config import get_settings
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)

OPS_NS = {
    "ops": "http://ops.epo.org",
    "exchange-documents": "http://www.epo.org/exchange",
}

TOKEN_KEY = "ops:oauth:token"
TOKEN_TTL_SECONDS = 50 * 60
BIBLIO_TTL_SECONDS = 14 * 24 * 60 * 60
LEGAL_STATUS_TTL_SECONDS = 24 * 60 * 60

THROTTLE_HEADER_KEYS = (
    "x-throttling-control",
    "x-throttling-control-header",
    "x-ops-throttle-status",
)


class OPSConnectionError(Exception):
    """Raised when communication with OPS API fails."""


class OPSParseError(Exception):
    """Raised when OPS XML or payload cannot be parsed reliably."""


class OPSQuotaExceededError(Exception):
    """Raised when OPS indicates quota has been exhausted (Black status)."""


@dataclass(slots=True)
class RawPatentData:
    """Minimal publication reference extracted from search XML."""

    publication_ref: str
    country_code: str | None = None
    doc_number: str | None = None
    kind_code: str | None = None


class OpsConnector:
    """Wrapper over python-epo-ops-client with async execution and resilient handling."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Any | None = None

    @staticmethod
    def _cache_key(endpoint: str, pub_ref: str) -> str:
        return f"ops:{endpoint}:{pub_ref}"

    @staticmethod
    def _normalize_headers(headers: Any) -> dict[str, str]:
        if not headers:
            return {}
        if isinstance(headers, dict):
            return {str(key).lower(): str(value) for key, value in headers.items()}
        try:
            return {str(key).lower(): str(value) for key, value in dict(headers).items()}
        except Exception:
            return {}

    @staticmethod
    def _get_header(headers: dict[str, str], key: str) -> str | None:
        return headers.get(key.lower())

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client

        if not self._settings.epo_consumer_key or not self._settings.epo_consumer_secret:
            raise OPSConnectionError("EPO OPS credentials are not configured")

        try:
            client = epo_ops.Client(
                key=self._settings.epo_consumer_key,
                secret=self._settings.epo_consumer_secret,
            )

            middlewares_module = getattr(epo_ops, "middlewares", None)
            dogpile_cls = getattr(middlewares_module, "Dogpile", None) if middlewares_module else None
            if dogpile_cls:
                cache_backend = "dogpile.cache.redis"
                cache_arguments = {
                    "host": "redis",
                    "port": 6379,
                    "db": 2,
                    "redis_expiration_time": BIBLIO_TTL_SECONDS,
                }
                try:
                    client.middlewares.append(
                        dogpile_cls(
                            cache_backend=cache_backend,
                            cache_arguments=cache_arguments,
                        )
                    )
                except Exception as middleware_error:  # pragma: no cover - environment-specific
                    logger.warning("Could not attach OPS Dogpile middleware: %s", middleware_error)

            self._client = client
            return self._client
        except Exception as exc:
            raise OPSConnectionError(f"Unable to initialize OPS client: {exc}") from exc

    async def _persist_token_from_client(self, client: Any) -> None:
        token_data = getattr(client, "access_token", None) or getattr(client, "token", None)
        if not token_data:
            return

        if isinstance(token_data, str):
            payload = {"access_token": token_data, "expires_in": TOKEN_TTL_SECONDS}
        elif isinstance(token_data, dict):
            payload = {
                "access_token": token_data.get("access_token", ""),
                "expires_in": int(token_data.get("expires_in") or TOKEN_TTL_SECONDS),
                "token_type": token_data.get("token_type", "Bearer"),
            }
        else:
            return

        ttl = max(60, int(payload.get("expires_in") or TOKEN_TTL_SECONDS))
        await redis_client.set(TOKEN_KEY, json.dumps(payload), ex=ttl)

    async def _restore_token_to_client(self, client: Any) -> None:
        cached = await redis_client.get(TOKEN_KEY)
        if not cached:
            return

        try:
            payload = json.loads(cached)
            access_token = payload.get("access_token")
            if not access_token:
                return
            if hasattr(client, "access_token"):
                client.access_token = payload
            elif hasattr(client, "token"):
                client.token = payload
        except Exception:
            logger.debug("Failed to restore OPS token from Redis", exc_info=True)

    @staticmethod
    def _extract_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        return str(value)

    def _normalize_response(self, raw_response: Any) -> tuple[str, dict[str, str], int | None]:
        headers: dict[str, str] = {}
        status_code: int | None = None

        if isinstance(raw_response, tuple) and len(raw_response) == 2:
            response_obj, body = raw_response
            headers = self._normalize_headers(getattr(response_obj, "headers", None))
            status_code = getattr(response_obj, "status_code", None)
            return self._extract_text(body), headers, status_code

        if hasattr(raw_response, "status_code"):
            headers = self._normalize_headers(getattr(raw_response, "headers", None))
            status_code = getattr(raw_response, "status_code", None)
            body = getattr(raw_response, "text", None)
            if body is None:
                body = getattr(raw_response, "content", "")
            return self._extract_text(body), headers, status_code

        response_obj = getattr(raw_response, "response", None)
        if response_obj is not None:
            headers = self._normalize_headers(getattr(response_obj, "headers", None))
            status_code = getattr(response_obj, "status_code", None)

        text_body = getattr(raw_response, "text", None)
        if text_body is None:
            text_body = getattr(raw_response, "content", raw_response)
        return self._extract_text(text_body), headers, status_code

    @staticmethod
    def _read_quota_headers(headers: dict[str, str]) -> dict[str, str | None]:
        return {
            "individual_per_hour": headers.get("x-individualquota-perhour-used"),
            "registered_per_week": headers.get("x-registeredquota-perweek-used"),
        }

    @staticmethod
    def _read_throttle_status(headers: dict[str, str]) -> str:
        merged = " ".join(headers.get(key, "") for key in THROTTLE_HEADER_KEYS).lower()
        if "black" in merged:
            return "BLACK"
        if "red" in merged:
            return "RED"
        if "yellow" in merged:
            return "YELLOW"
        return "GREEN"

    async def _call_ops_method(self, method_name: str, **kwargs: Any) -> tuple[str, dict[str, str], int | None]:
        client = self._ensure_client()
        await self._restore_token_to_client(client)

        method = getattr(client, method_name, None)
        if method is None:
            raise OPSConnectionError(f"OPS client does not expose method '{method_name}'")

        raw_response = await asyncio.to_thread(method, **kwargs)
        await self._persist_token_from_client(client)
        return self._normalize_response(raw_response)

    async def _request_with_retry(self, method_name: str, **kwargs: Any) -> tuple[str, dict[str, str], int | None]:
        backoff_schedule = [2, 4, 8]

        for attempt in range(len(backoff_schedule) + 1):
            try:
                payload, headers, status_code = await self._call_ops_method(method_name, **kwargs)

                quota = self._read_quota_headers(headers)
                if quota["individual_per_hour"] or quota["registered_per_week"]:
                    logger.info(
                        "OPS quota usage: individual/hour=%s, registered/week=%s",
                        quota["individual_per_hour"],
                        quota["registered_per_week"],
                    )

                throttle = self._read_throttle_status(headers)
                if throttle == "BLACK":
                    raise OPSQuotaExceededError("OPS quota exceeded (Black throttle status)")

                if status_code == 401:
                    await redis_client.delete(TOKEN_KEY)
                    self._client = None
                    if attempt < len(backoff_schedule):
                        await asyncio.sleep(backoff_schedule[attempt])
                        continue
                    raise OPSConnectionError("OPS authentication failed after token refresh attempts")

                if throttle in {"YELLOW", "RED"} and attempt < len(backoff_schedule):
                    await asyncio.sleep(backoff_schedule[attempt])
                    continue

                return payload, headers, status_code
            except OPSQuotaExceededError:
                raise
            except Exception as exc:
                if attempt < len(backoff_schedule):
                    await asyncio.sleep(backoff_schedule[attempt])
                    continue
                raise OPSConnectionError(f"OPS request failed for {method_name}: {exc}") from exc

        raise OPSConnectionError(f"OPS request exhausted retries for {method_name}")

    @staticmethod
    def _parse_xml(xml_text: str) -> ET.Element:
        try:
            return ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise OPSParseError(f"Failed to parse OPS XML payload: {exc}") from exc

    @staticmethod
    def _extract_texts(root: ET.Element, xpath: str) -> list[str]:
        results: list[str] = []
        for element in root.findall(xpath, OPS_NS):
            text = (element.text or "").strip()
            if text:
                results.append(text)
        return results

    @staticmethod
    def _normalize_pub_ref(country: str | None, doc_number: str | None, kind: str | None) -> str:
        parts = [part for part in (country, doc_number, kind) if part]
        return "".join(parts)

    async def search_patents(self, cql: str, start: int = 0, rows: int = 100) -> list[RawPatentData]:
        """Run a CQL search on OPS and return normalized publication references."""
        payload, _, _ = await self._request_with_retry(
            "published_data_search",
            cql=cql,
            range_begin=max(1, start + 1),
            range_end=max(1, start + rows),
        )

        root = self._parse_xml(payload)
        results: list[RawPatentData] = []

        exchange_docs = root.findall(
            ".//exchange-documents:exchange-document",
            OPS_NS,
        )
        for doc in exchange_docs:
            country = doc.get("country")
            doc_number = doc.get("doc-number")
            kind = doc.get("kind")
            publication_ref = self._normalize_pub_ref(country, doc_number, kind)
            if publication_ref:
                results.append(
                    RawPatentData(
                        publication_ref=publication_ref,
                        country_code=country,
                        doc_number=doc_number,
                        kind_code=kind,
                    )
                )

        if results:
            return results

        doc_ids = root.findall(
            ".//exchange-documents:publication-reference/exchange-documents:document-id",
            OPS_NS,
        )
        for doc_id in doc_ids:
            country = doc_id.findtext("exchange-documents:country", default="", namespaces=OPS_NS) or None
            doc_number = doc_id.findtext("exchange-documents:doc-number", default="", namespaces=OPS_NS) or None
            kind = doc_id.findtext("exchange-documents:kind", default="", namespaces=OPS_NS) or None
            publication_ref = self._normalize_pub_ref(country, doc_number, kind)
            if publication_ref:
                results.append(
                    RawPatentData(
                        publication_ref=publication_ref,
                        country_code=country,
                        doc_number=doc_number,
                        kind_code=kind,
                    )
                )

        return results

    async def fetch_bibliographic(self, pub_ref: str) -> dict[str, Any]:
        """Fetch bibliographic metadata for a publication reference with 14-day Redis cache."""
        cache_key = self._cache_key("biblio", pub_ref)
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        payload, _, _ = await self._request_with_retry(
            "published_data",
            reference_type="publication",
            input=pub_ref,
            endpoint="biblio",
        )

        root = self._parse_xml(payload)
        title = ""
        title_nodes = root.findall(".//exchange-documents:invention-title", OPS_NS)
        for title_node in title_nodes:
            language = (title_node.get("lang") or "").lower()
            node_text = (title_node.text or "").strip()
            if not node_text:
                continue
            if language == "en":
                title = node_text
                break
            if not title:
                title = node_text

        applicants = self._extract_texts(root, ".//exchange-documents:applicants//exchange-documents:name")
        inventors = self._extract_texts(root, ".//exchange-documents:inventors//exchange-documents:name")

        ipc_classes = [
            value.replace(" ", "")
            for value in self._extract_texts(
                root,
                ".//exchange-documents:classification-ipc//exchange-documents:text",
            )
        ]
        cpc_classes = [
            value.replace(" ", "")
            for value in self._extract_texts(
                root,
                ".//exchange-documents:patent-classifications//exchange-documents:classification-symbol",
            )
        ]

        publication_date = None
        pub_date_nodes = root.findall(
            ".//exchange-documents:publication-reference//exchange-documents:date",
            OPS_NS,
        )
        if pub_date_nodes:
            publication_date = (pub_date_nodes[0].text or "").strip()

        priority_date = None
        priority_nodes = root.findall(
            ".//exchange-documents:priority-claim//exchange-documents:date",
            OPS_NS,
        )
        if priority_nodes:
            priority_date = (priority_nodes[0].text or "").strip()

        parsed = {
            "publication_number": pub_ref,
            "title": title,
            "applicants": applicants,
            "inventors": inventors,
            "ipc_classes": ipc_classes,
            "cpc_classes": cpc_classes,
            "publication_date": publication_date,
            "priority_date": priority_date,
        }

        await redis_client.set(cache_key, json.dumps(parsed), ex=BIBLIO_TTL_SECONDS)
        return parsed

    async def fetch_abstract(self, pub_ref: str) -> str | None:
        """Fetch abstract text for a publication reference."""
        payload, _, _ = await self._request_with_retry(
            "published_data",
            reference_type="publication",
            input=pub_ref,
            endpoint="abstract",
        )

        root = self._parse_xml(payload)
        paragraphs = self._extract_texts(root, ".//exchange-documents:abstract//exchange-documents:p")
        if not paragraphs:
            paragraphs = self._extract_texts(root, ".//abstract//p")
        return "\n".join(paragraphs).strip() or None

    async def fetch_claims(self, pub_ref: str) -> str | None:
        """Fetch claims text for a publication reference."""
        payload, _, _ = await self._request_with_retry(
            "published_data",
            reference_type="publication",
            input=pub_ref,
            endpoint="claims",
        )

        root = self._parse_xml(payload)
        claim_parts = self._extract_texts(root, ".//exchange-documents:claims//exchange-documents:claim-text")
        if not claim_parts:
            claim_parts = self._extract_texts(root, ".//claims//claim-text")
        return "\n".join(claim_parts).strip() or None

    async def fetch_legal_status(self, pub_ref: str) -> str:
        """Fetch and normalize legal status with 24-hour Redis cache."""
        cache_key = self._cache_key("legal", pub_ref)
        cached = await redis_client.get(cache_key)
        if cached:
            return str(cached)

        payload, _, _ = await self._request_with_retry(
            "legal",
            endpoint="publication",
            input=pub_ref,
        )

        root = self._parse_xml(payload)
        status_text_candidates = self._extract_texts(root, ".//ops:legal-status")
        if not status_text_candidates:
            status_text_candidates = self._extract_texts(root, ".//legal-status")

        raw_status = " ".join(status_text_candidates).lower()
        normalized = "Unknown"
        if re.search(r"active|in force|granted", raw_status):
            normalized = "Active"
        elif re.search(r"lapse|lapsed|withdrawn", raw_status):
            normalized = "Lapsed"
        elif re.search(r"expired|ceased|terminated", raw_status):
            normalized = "Expired"

        await redis_client.set(cache_key, normalized, ex=LEGAL_STATUS_TTL_SECONDS)
        return normalized

    async def fetch_family(self, pub_ref: str) -> list[str]:
        """Fetch INPADOC family publication numbers for a reference."""
        payload, _, _ = await self._request_with_retry(
            "family",
            endpoint="publication",
            input=pub_ref,
            constituents="inpadoc",
        )

        root = self._parse_xml(payload)
        family_refs: list[str] = []

        family_docs = root.findall(
            ".//exchange-documents:exchange-document",
            OPS_NS,
        )
        for doc in family_docs:
            ref = self._normalize_pub_ref(doc.get("country"), doc.get("doc-number"), doc.get("kind"))
            if ref and ref not in family_refs:
                family_refs.append(ref)

        if family_refs:
            return family_refs

        for doc_id in root.findall(
            ".//exchange-documents:publication-reference/exchange-documents:document-id",
            OPS_NS,
        ):
            ref = self._normalize_pub_ref(
                doc_id.findtext("exchange-documents:country", default="", namespaces=OPS_NS) or None,
                doc_id.findtext("exchange-documents:doc-number", default="", namespaces=OPS_NS) or None,
                doc_id.findtext("exchange-documents:kind", default="", namespaces=OPS_NS) or None,
            )
            if ref and ref not in family_refs:
                family_refs.append(ref)

        return family_refs


ops_connector = OpsConnector()
