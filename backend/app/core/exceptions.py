"""Custom exception hierarchy and error metadata for PatentPath services."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PatentPathBaseError(Exception):
    """Base application exception with structured API error metadata."""

    message: str
    error_code: str = "PATENTPATH_ERROR"
    status_code: int = 500
    retry_after_seconds: int | None = None

    def __str__(self) -> str:
        return self.message


class OPSConnectionError(PatentPathBaseError):
    """Raised when communication with EPO OPS fails."""

    def __init__(self, message: str = "Unable to reach EPO OPS service") -> None:
        super().__init__(
            message=message,
            error_code="OPS_CONNECTION_ERROR",
            status_code=502,
        )


class OPSParseError(PatentPathBaseError):
    """Raised when OPS payload parsing fails."""

    def __init__(self, message: str = "Failed to parse OPS response payload") -> None:
        super().__init__(
            message=message,
            error_code="OPS_PARSE_ERROR",
            status_code=502,
        )


class OPSQuotaExceededError(PatentPathBaseError):
    """Raised when OPS quota has been exhausted."""

    def __init__(
        self,
        message: str = "OPS quota exceeded",
        *,
        retry_after_seconds: int | None = 3600,
    ) -> None:
        super().__init__(
            message=message,
            error_code="OPS_QUOTA_EXCEEDED",
            status_code=429,
            retry_after_seconds=retry_after_seconds,
        )


class NLPProcessingError(PatentPathBaseError):
    """Raised when NLP scoring cannot complete correctly."""

    def __init__(self, message: str = "NLP scoring pipeline failed") -> None:
        super().__init__(
            message=message,
            error_code="NLP_PROCESSING_ERROR",
            status_code=500,
        )


class GapAnalysisError(PatentPathBaseError):
    """Base error for gap analysis service failures."""

    def __init__(self, message: str = "Gap analysis failed") -> None:
        super().__init__(
            message=message,
            error_code="GAP_ANALYSIS_ERROR",
            status_code=500,
        )


class ClaudeAPIError(GapAnalysisError):
    """Raised when Anthropic API calls fail."""

    def __init__(self, message: str = "Claude API request failed") -> None:
        super().__init__(message=message)
        self.error_code = "CLAUDE_API_ERROR"
        self.status_code = 502


class ParseError(GapAnalysisError):
    """Raised when gap analysis output cannot be parsed."""

    def __init__(self, message: str = "Unable to parse gap analysis payload") -> None:
        super().__init__(message=message)
        self.error_code = "GAP_ANALYSIS_PARSE_ERROR"
        self.status_code = 500


class ReportGenerationError(PatentPathBaseError):
    """Raised when report generation fails."""

    def __init__(self, message: str = "Failed to generate report") -> None:
        super().__init__(
            message=message,
            error_code="REPORT_GENERATION_ERROR",
            status_code=500,
        )


class ProjectNotFoundError(PatentPathBaseError):
    """Raised when project lookup fails."""

    def __init__(self, message: str = "Project not found") -> None:
        super().__init__(
            message=message,
            error_code="PROJECT_NOT_FOUND",
            status_code=404,
        )


class SearchSessionNotFoundError(PatentPathBaseError):
    """Raised when search session lookup fails."""

    def __init__(self, message: str = "Search session not found") -> None:
        super().__init__(
            message=message,
            error_code="SEARCH_SESSION_NOT_FOUND",
            status_code=404,
        )
