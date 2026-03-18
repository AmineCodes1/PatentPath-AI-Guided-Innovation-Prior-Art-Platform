/**
 * Global footer for academic PatentPath deployments.
 */

import type { ReactElement } from "react";

export default function Footer(): ReactElement {
  return (
    <footer className="border-t border-slate-200 bg-white/85 px-6 py-4">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 text-xs text-text-secondary">
        <p>PatentPath - ENSA Kenitra Innovation Challenge 2025-2026</p>
        <p className="font-semibold text-risk-medium">⚠ Not legal advice. For academic purposes only.</p>
      </div>
    </footer>
  );
}
