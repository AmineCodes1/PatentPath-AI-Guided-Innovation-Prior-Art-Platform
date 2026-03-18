/**
 * Full-page loading overlay with animated PatentPath mark and custom message.
 */

import type { ReactElement } from "react";

type LoadingOverlayProps = {
  message: string;
};

export default function LoadingOverlay({ message }: Readonly<LoadingOverlayProps>): ReactElement {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 backdrop-blur-[2px]">
      <div className="w-[320px] rounded-2xl border border-white/40 bg-white/95 p-6 text-center shadow-panel">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-primary text-2xl font-extrabold text-white animate-pulse">
          P
        </div>
        <p className="mt-4 text-sm font-semibold uppercase tracking-widest text-accent">PatentPath</p>
        <p className="mt-2 text-sm text-text-primary">{message}</p>
      </div>
    </div>
  );
}
