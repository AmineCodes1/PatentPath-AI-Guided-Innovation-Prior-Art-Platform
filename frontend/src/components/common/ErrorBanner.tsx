/**
 * Reusable API error banner with optional retry countdown for quota limits.
 */

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

type ErrorBannerProps = {
  errorCode?: string | null;
  message: string;
  retryAfterSeconds?: number;
  onDismiss?: () => void;
};

function defaultMessageForCode(code?: string | null): string | null {
  if (!code) {
    return null;
  }

  if (code === "OPS_QUOTA_EXCEEDED") {
    return "Espacenet quota is currently exhausted. Please wait and retry.";
  }
  if (code === "OPS_CONNECTION_ERROR") {
    return "Patent search service is temporarily unavailable. Try again shortly.";
  }
  return null;
}

export default function ErrorBanner({
  errorCode,
  message,
  retryAfterSeconds,
  onDismiss,
}: Readonly<ErrorBannerProps>): ReactElement {
  const [remaining, setRemaining] = useState<number>(retryAfterSeconds ?? 0);

  useEffect(() => {
    setRemaining(retryAfterSeconds ?? 0);
  }, [retryAfterSeconds]);

  useEffect(() => {
    if (!remaining || remaining <= 0) {
      return;
    }

    const timer = globalThis.setInterval(() => {
      setRemaining((value) => (value <= 1 ? 0 : value - 1));
    }, 1000);

    return () => globalThis.clearInterval(timer);
  }, [remaining]);

  const helperText = useMemo(() => defaultMessageForCode(errorCode), [errorCode]);

  return (
    <div className="rounded-xl border border-risk-high/30 bg-risk-high/10 px-4 py-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-risk-high">Request Error</p>
          {errorCode ? <p className="mt-1 text-xs font-semibold text-risk-high">Code: {errorCode}</p> : null}
          <p className="mt-1 text-sm text-text-primary">{message}</p>
          {helperText ? <p className="mt-1 text-xs text-text-secondary">{helperText}</p> : null}
          {errorCode === "OPS_QUOTA_EXCEEDED" && remaining > 0 ? (
            <p className="mt-2 text-xs font-semibold text-risk-medium">Retry available in {remaining}s</p>
          ) : null}
        </div>

        {onDismiss ? (
          <button
            type="button"
            onClick={onDismiss}
            className="rounded-md border border-risk-high/40 px-2 py-1 text-xs font-semibold text-risk-high"
          >
            Dismiss
          </button>
        ) : null}
      </div>
    </div>
  );
}
