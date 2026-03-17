/**
 * Selected patent detail panel rendered in the search sidebar.
 */

import type { ReactElement } from "react";
import type { ScoredResult } from "../../types/search";

type PatentDetailPanelProps = {
  selectedResult: ScoredResult | null;
};

export default function PatentDetailPanel({ selectedResult }: PatentDetailPanelProps): ReactElement {
  return (
    <div>
      <h2 className="text-sm font-semibold uppercase tracking-widest text-primary">Patent Detail</h2>
      {selectedResult ? (
        <div className="mt-3 space-y-2 text-sm">
          <p className="font-semibold text-text-primary">{selectedResult.patent.title}</p>
          <p className="text-text-secondary">{selectedResult.patent.publication_number}</p>
          <p className="text-text-secondary">{selectedResult.patent.abstract}</p>
          <a
            href={selectedResult.patent.espacenet_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex rounded-lg border border-primary px-3 py-1.5 text-xs font-semibold text-primary transition hover:bg-primary hover:text-white"
          >
            Open in Espacenet
          </a>
        </div>
      ) : (
        <p className="mt-3 text-sm text-text-secondary">Select a result to preview details.</p>
      )}
    </div>
  );
}
