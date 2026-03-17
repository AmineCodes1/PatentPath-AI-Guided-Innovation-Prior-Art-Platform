/**
 * Patent result card for ranked similarity outputs.
 */

import type { ReactElement } from "react";
import type { ScoredResult } from "../../types/search";

const RISK_STYLES: Record<ScoredResult["risk_label"], string> = {
  HIGH: "bg-risk-high/15 text-risk-high",
  MEDIUM: "bg-risk-medium/15 text-risk-medium",
  LOW: "bg-risk-low/15 text-risk-low",
  MINIMAL: "bg-risk-minimal/15 text-risk-minimal",
};

type PatentResultCardProps = {
  result: ScoredResult;
  onExpand: (result: ScoredResult) => void;
};

function toPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export default function PatentResultCard({ result, onExpand }: PatentResultCardProps): ReactElement {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-accent">Rank #{result.rank}</p>
          <a
            href={result.patent.espacenet_url}
            target="_blank"
            rel="noreferrer"
            className="mt-1 block text-lg font-semibold text-primary hover:text-accent"
          >
            {result.patent.title}
          </a>
          <p className="mt-1 text-xs text-text-secondary">
            {result.patent.publication_number} • {new Date(result.patent.publication_date).toLocaleDateString()}
          </p>
          <p className="mt-1 text-xs text-text-secondary">
            {result.patent.applicants.length > 0 ? result.patent.applicants.join(", ") : "No applicant data"}
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-text-primary">{toPercent(result.composite_score)}</p>
          <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${RISK_STYLES[result.risk_label]}`}>
            {result.risk_label}
          </span>
        </div>
      </div>

      <div className="mt-4 grid gap-2 text-xs text-text-secondary">
        <div>
          <div className="mb-1 flex justify-between">
            <span>BM25 (30%)</span>
            <span>{toPercent(result.bm25_score)}</span>
          </div>
          <progress className="h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-slate-200 [&::-webkit-progress-value]:bg-primary" max={100} value={Math.min(100, Math.max(0, result.bm25_score * 100))} />
        </div>
        <div>
          <div className="mb-1 flex justify-between">
            <span>TF-IDF (50%)</span>
            <span>{toPercent(result.tfidf_cosine)}</span>
          </div>
          <progress className="h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-slate-200 [&::-webkit-progress-value]:bg-accent" max={100} value={Math.min(100, Math.max(0, result.tfidf_cosine * 100))} />
        </div>
        <div>
          <div className="mb-1 flex justify-between">
            <span>Semantic (20%)</span>
            <span>{toPercent(result.semantic_cosine)}</span>
          </div>
          <progress className="h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-slate-200 [&::-webkit-progress-value]:bg-blue-300" max={100} value={Math.min(100, Math.max(0, result.semantic_cosine * 100))} />
        </div>
      </div>

      <button
        type="button"
        onClick={() => onExpand(result)}
        className="mt-4 rounded-lg border border-primary px-3 py-2 text-sm font-medium text-primary transition hover:bg-primary hover:text-white"
      >
        Expand details
      </button>
    </article>
  );
}
