/**
 * Reusable empty state card for first-time and no-data screens.
 */

import type { ReactElement } from "react";

type EmptyStateProps = {
  title: string;
  subtitle: string;
  steps?: string[];
  actionLabel?: string;
  onAction?: () => void;
};

export default function EmptyState({
  title,
  subtitle,
  steps = [],
  actionLabel,
  onAction,
}: EmptyStateProps): ReactElement {
  return (
    <div className="rounded-2xl border border-dashed border-accent/50 bg-white p-6 shadow-panel">
      <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
      <p className="mt-2 text-sm text-text-secondary">{subtitle}</p>
      {steps.length > 0 ? (
        <ol className="mt-4 grid gap-2 text-sm text-text-primary sm:grid-cols-3">
          {steps.map((step, index) => (
            <li key={step} className="rounded-lg bg-surface px-3 py-2">
              <span className="mr-1 font-semibold text-primary">{index + 1}.</span>
              {step}
            </li>
          ))}
        </ol>
      ) : null}
      {actionLabel && onAction ? (
        <button
          type="button"
          onClick={onAction}
          className="mt-5 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900"
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
