/**
 * Client-side filter panel for narrowing visible scored results.
 */

import type { ReactElement } from "react";
import type { RiskLabel } from "../../types/search";

type FilterState = {
  risk: RiskLabel | "ALL";
  country: string;
  dateFrom: string;
  dateTo: string;
};

type FilterSidebarProps = {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
};

const RISK_OPTIONS: Array<RiskLabel | "ALL"> = ["ALL", "HIGH", "MEDIUM", "LOW", "MINIMAL"];

export default function FilterSidebar({ filters, onChange }: FilterSidebarProps): ReactElement {
  return (
    <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-panel">
      <h3 className="text-sm font-semibold uppercase tracking-widest text-primary">Live Filters</h3>
      <div className="mt-4 space-y-4">
        <label className="block text-sm text-text-secondary">
          Risk Label
          <select
            value={filters.risk}
            onChange={(event) => onChange({ ...filters, risk: event.target.value as FilterState["risk"] })}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
          >
            {RISK_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm text-text-secondary">
          Country Code
          <input
            type="text"
            value={filters.country}
            onChange={(event) => onChange({ ...filters, country: event.target.value.toUpperCase() })}
            placeholder="EP, US, WO..."
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
          />
        </label>

        <label className="block text-sm text-text-secondary">
          Publication Date From
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(event) => onChange({ ...filters, dateFrom: event.target.value })}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
          />
        </label>

        <label className="block text-sm text-text-secondary">
          Publication Date To
          <input
            type="date"
            value={filters.dateTo}
            onChange={(event) => onChange({ ...filters, dateTo: event.target.value })}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
          />
        </label>
      </div>
    </aside>
  );
}
