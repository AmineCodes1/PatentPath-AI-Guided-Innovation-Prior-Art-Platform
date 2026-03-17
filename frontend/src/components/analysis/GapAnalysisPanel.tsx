/**
 * Full gap analysis display including risks, coverage, gaps, and suggestions.
 */

import type { ReactElement } from "react";
import type { GapAnalysis } from "../../types/analysis";

const RISK_BADGE_STYLES: Record<GapAnalysis["overall_risk"], string> = {
  HIGH: "bg-risk-high/15 text-risk-high",
  MEDIUM: "bg-risk-medium/15 text-risk-medium",
  LOW: "bg-risk-low/15 text-risk-low",
};

type GapAnalysisPanelProps = {
  analysis: GapAnalysis | null;
  isLoading: boolean;
  error: string | null;
};

function AspectList({ title, items, emptyText }: { title: string; items: string[]; emptyText: string }): ReactElement {
  return (
    <div className="rounded-xl border border-slate-200 bg-surface p-4">
      <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-text-secondary">{emptyText}</p>
      ) : (
        <ul className="mt-2 space-y-2 text-sm text-text-primary">
          {items.map((item) => (
            <li key={item} className="rounded-lg bg-white px-3 py-2">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function GapAnalysisPanel({ analysis, isLoading, error }: GapAnalysisPanelProps): ReactElement {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-surface p-4">
        <p className="text-sm font-medium text-primary">AI model is generating novelty gap analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-risk-high/30 bg-risk-high/10 p-4">
        <p className="text-sm font-medium text-risk-high">{error}</p>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="rounded-xl border border-slate-200 bg-surface p-4">
        <p className="text-sm text-text-secondary">Gap analysis will appear once search results are processed.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-surface p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-semibold uppercase tracking-widest text-primary">Overall Novelty Risk</h3>
          <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${RISK_BADGE_STYLES[analysis.overall_risk]}`}>
            {analysis.overall_risk}
          </span>
        </div>
        <p className="mt-3 text-sm leading-6 text-text-secondary">{analysis.narrative_text}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <AspectList title="Covered Aspects" items={analysis.covered_aspects} emptyText="No covered aspects detected." />
        <AspectList title="Gap Aspects" items={analysis.gap_aspects} emptyText="No high-confidence gaps detected." />
      </div>

      <AspectList title="Innovation Suggestions" items={analysis.suggestions} emptyText="No suggestions generated yet." />
    </div>
  );
}
