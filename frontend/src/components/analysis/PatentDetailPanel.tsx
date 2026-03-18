/**
 * Selected patent detail panel rendered in the search sidebar.
 */

import { useEffect, useState } from "react";
import type { ReactElement } from "react";
import apiClient from "../../api/client";
import PatentFamilyView from "../patents/PatentFamilyView";
import type { ScoredResult } from "../../types/search";

type PatentDetailPanelProps = {
  selectedResult: ScoredResult | null;
};

type PatentDetail = {
  publication_number: string;
  title: string;
  abstract: string;
  claims?: string | null;
  applicants: string[];
  inventors: string[];
  ipc_classes: string[];
  cpc_classes: string[];
  publication_date: string;
  priority_date?: string | null;
  legal_status?: string | null;
  espacenet_url: string;
};

function fallbackDetail(result: ScoredResult): PatentDetail {
  return {
    publication_number: result.patent.publication_number,
    title: result.patent.title,
    abstract: result.patent.abstract,
    claims: null,
    applicants: result.patent.applicants,
    inventors: [],
    ipc_classes: [],
    cpc_classes: [],
    publication_date: result.patent.publication_date,
    priority_date: null,
    legal_status: result.patent.legal_status,
    espacenet_url: result.patent.espacenet_url,
  };
}

export default function PatentDetailPanel({ selectedResult }: Readonly<PatentDetailPanelProps>): ReactElement {
  const [detail, setDetail] = useState<PatentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!selectedResult) {
      setDetail(null);
      return;
    }

    let cancelled = false;

    const loadDetail = async (): Promise<void> => {
      setIsLoading(true);
      try {
        const response = await apiClient.get<PatentDetail>(`/patents/${selectedResult.patent.publication_number}`);
        if (!cancelled) {
          setDetail(response.data);
        }
      } catch {
        if (!cancelled) {
          setDetail(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadDetail();

    return () => {
      cancelled = true;
    };
  }, [selectedResult]);

  const activeDetail = detail ?? (selectedResult ? fallbackDetail(selectedResult) : null);

  return (
    <div>
      <h2 className="text-sm font-semibold uppercase tracking-widest text-primary">Patent Detail</h2>
      {activeDetail ? (
        <div className="mt-3 space-y-3 text-sm">
          <p className="font-semibold text-text-primary">{activeDetail.title}</p>
          <p className="text-text-secondary">{activeDetail.publication_number}</p>
          <p className="text-xs text-text-secondary">
            Publication: {new Date(activeDetail.publication_date).toLocaleDateString()}
            {activeDetail.priority_date ? ` | Priority: ${new Date(activeDetail.priority_date).toLocaleDateString()}` : ""}
          </p>

          <p className="text-xs text-text-secondary">
            Applicants: {activeDetail.applicants.length ? activeDetail.applicants.join(", ") : "Not available"}
          </p>
          <p className="text-xs text-text-secondary">
            Inventors: {activeDetail.inventors.length ? activeDetail.inventors.join(", ") : "Not available"}
          </p>

          {activeDetail.ipc_classes.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {activeDetail.ipc_classes.map((code) => (
                <span key={`ipc-${code}`} className="rounded-full bg-accent/20 px-2 py-0.5 text-[11px] font-semibold text-primary">
                  IPC {code}
                </span>
              ))}
            </div>
          ) : null}

          {activeDetail.cpc_classes.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {activeDetail.cpc_classes.map((code) => (
                <span key={`cpc-${code}`} className="rounded-full bg-primary/15 px-2 py-0.5 text-[11px] font-semibold text-primary">
                  CPC {code}
                </span>
              ))}
            </div>
          ) : null}

          <p className="text-text-secondary">{activeDetail.abstract}</p>

          {activeDetail.claims ? (
            <p className="text-xs leading-5 text-text-secondary">{activeDetail.claims.slice(0, 900)}</p>
          ) : null}

          <p className="text-xs font-semibold text-text-secondary">
            Legal status: {activeDetail.legal_status ?? "Unknown"}
          </p>

          <a
            href={activeDetail.espacenet_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex rounded-lg border border-primary px-3 py-1.5 text-xs font-semibold text-primary transition hover:bg-primary hover:text-white"
          >
            Open in Espacenet
          </a>

          <PatentFamilyView publicationNumber={activeDetail.publication_number} />

          {isLoading ? <p className="text-xs text-text-secondary">Refreshing full patent metadata...</p> : null}
        </div>
      ) : (
        <p className="mt-3 text-sm text-text-secondary">Select a result to preview details.</p>
      )}
    </div>
  );
}
