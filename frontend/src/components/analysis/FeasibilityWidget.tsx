/**
 * Compact feasibility visualization with sub-score bars and composite percentage.
 */

import type { ReactElement } from "react";
import type { FeasibilityComplete } from "../../types/analysis";

type FeasibilityWidgetProps = {
  feasibility: FeasibilityComplete | null;
  isLoading: boolean;
};

function toPercentFromFive(value: number | null): number {
  if (typeof value !== "number") {
    return 0;
  }
  return Math.max(0, Math.min(100, value * 20));
}

function scoreLabel(value: number | null): string {
  if (typeof value !== "number") {
    return "Pending";
  }
  return `${value.toFixed(1)} / 5`;
}

export default function FeasibilityWidget({ feasibility, isLoading }: FeasibilityWidgetProps): ReactElement {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-surface p-4">
        <p className="text-sm font-medium text-primary">Computing feasibility metrics...</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-surface p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-primary">Feasibility Index</h3>
        <p className="text-lg font-bold text-text-primary">
          {feasibility ? `${Math.round(feasibility.composite_percentage)}%` : "--"}
        </p>
      </div>

      <div className="mt-3 space-y-3 text-xs text-text-secondary">
        <div>
          <div className="mb-1 flex items-center justify-between">
            <span>Technical readiness</span>
            <span>{scoreLabel(feasibility?.technical_readiness ?? null)}</span>
          </div>
          <progress className="h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-slate-200 [&::-webkit-progress-value]:bg-primary" max={100} value={toPercentFromFive(feasibility?.technical_readiness ?? null)} />
        </div>

        <div>
          <div className="mb-1 flex items-center justify-between">
            <span>Domain specificity</span>
            <span>{scoreLabel(feasibility?.domain_specificity ?? null)}</span>
          </div>
          <progress className="h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-slate-200 [&::-webkit-progress-value]:bg-accent" max={100} value={toPercentFromFive(feasibility?.domain_specificity ?? null)} />
        </div>

        <div>
          <div className="mb-1 flex items-center justify-between">
            <span>Claim potential</span>
            <span>{scoreLabel(feasibility?.claim_potential ?? null)}</span>
          </div>
          <progress className="h-2 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-slate-200 [&::-webkit-progress-value]:bg-blue-300" max={100} value={toPercentFromFive(feasibility?.claim_potential ?? null)} />
        </div>
      </div>
    </div>
  );
}
