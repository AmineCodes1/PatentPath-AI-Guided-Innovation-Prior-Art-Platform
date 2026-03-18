/**
 * Reusable legal disclaimer banner for computational patent analysis outputs.
 */

import type { ReactElement } from "react";

type LegalDisclaimerProps = {
  className?: string;
};

export default function LegalDisclaimer({ className = "" }: LegalDisclaimerProps): ReactElement {
  return (
    <div className={`rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900 ${className}`.trim()}>
      <p>
        ⚠ This report is a computational tool, not legal advice. It does not constitute a patentability opinion.
      </p>
      <p className="mt-1">
        Always consult a qualified patent attorney or patent agent before filing any patent application.
      </p>
    </div>
  );
}
