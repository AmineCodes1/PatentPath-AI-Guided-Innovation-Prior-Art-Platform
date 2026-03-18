/**
 * Panel used to generate and download patent preparation PDF reports.
 */

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";
import LegalDisclaimer from "../common/LegalDisclaimer";
import { useReportStore } from "../../store/reportStore";

const REPORT_CHECKLIST = [
  "Problem Statement",
  "Top-5 Prior Art Table",
  "Gap Analysis",
  "Innovation Suggestions",
  "Feasibility Assessment",
  "Draft Claims Outline",
  "Recommended Next Steps",
  "Patent Appendix",
];

const LOADING_MESSAGES = [
  "Compiling prior art data...",
  "Formatting gap analysis...",
  "Generating PDF...",
];

type ReportGeneratorPanelProps = {
  projectId: string;
  sessionId: string;
  sessionDate?: string;
  enabled: boolean;
};

function formatFileSize(bytes: number | null): string {
  if (bytes === null) {
    return "Unknown";
  }
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function ReportGeneratorPanel({
  projectId,
  sessionId,
  sessionDate,
  enabled,
}: Readonly<ReportGeneratorPanelProps>): ReactElement {
  const activeReportJobs = useReportStore((state) => state.activeReportJobs);
  const completedReports = useReportStore((state) => state.completedReports);
  const createAndTrackReport = useReportStore((state) => state.createAndTrackReport);
  const downloadCompletedReport = useReportStore((state) => state.downloadCompletedReport);

  const latestCompleted = useMemo(
    () => completedReports.find((item) => item.project_id === projectId && item.session_id === sessionId),
    [completedReports, projectId, sessionId],
  );

  const jobForSession = useMemo(
    () => Object.values(activeReportJobs).find((item) => item.project_id === projectId && item.session_id === sessionId),
    [activeReportJobs, projectId, sessionId],
  );

  const isProcessing = jobForSession?.status === "PENDING" || jobForSession?.status === "PROCESSING";
  const isReady = jobForSession?.status === "READY" || Boolean(latestCompleted);
  const hasFailure = jobForSession?.status === "FAILED";

  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);

  useEffect(() => {
    if (!isProcessing) {
      setLoadingMessageIndex(0);
      return;
    }

    const intervalId = globalThis.setInterval(() => {
      setLoadingMessageIndex((index) => (index + 1) % LOADING_MESSAGES.length);
    }, 1600);

    return () => {
      globalThis.clearInterval(intervalId);
    };
  }, [isProcessing]);

  const handleGenerate = async (): Promise<void> => {
    await createAndTrackReport(projectId, sessionId, sessionDate);
  };

  const handleDownload = async (): Promise<void> => {
    if (!latestCompleted) {
      return;
    }
    await downloadCompletedReport(latestCompleted.job_id);
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
      <h3 className="text-xl font-bold text-text-primary">Generate Patent Preparation Report</h3>

      <LegalDisclaimer className="mt-3" />

      {enabled ? null : (
        <p className="mt-4 rounded-lg bg-surface px-4 py-3 text-sm text-text-secondary">
          Complete gap analysis to enable report generation.
        </p>
      )}

      {enabled && !isProcessing && !isReady ? (
        <>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {REPORT_CHECKLIST.map((item) => (
              <p key={item} className="rounded-lg bg-surface px-3 py-2 text-sm text-text-primary">
                ✓ {item}
              </p>
            ))}
          </div>

          <button
            type="button"
            onClick={() => void handleGenerate()}
            className="mt-5 inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 text-base font-semibold text-white transition hover:bg-blue-900"
          >
            Generate Report
          </button>
        </>
      ) : null}

      {enabled && isProcessing ? (
        <div className="mt-5 rounded-xl border border-primary/20 bg-primary/5 p-4">
          <div className="flex items-center gap-3">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-primary/30 border-t-primary" />
            <p className="text-sm font-medium text-primary">{LOADING_MESSAGES[loadingMessageIndex]}</p>
          </div>
        </div>
      ) : null}

      {enabled && isReady ? (
        <div className="mt-5 rounded-xl border border-risk-low/30 bg-risk-low/10 p-4">
          <p className="text-sm font-semibold text-risk-low">✓ Your Patent Preparation Report is Ready</p>
          <p className="mt-2 text-xs text-text-secondary">
            File size: {formatFileSize(latestCompleted?.file_size_bytes ?? null)}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void handleDownload()}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900"
            >
              Download PDF
            </button>
            <button
              type="button"
              onClick={() => void handleGenerate()}
              className="rounded-lg border border-primary/30 bg-white px-4 py-2 text-sm font-semibold text-primary transition hover:bg-primary/5"
            >
              Generate New Version
            </button>
          </div>
        </div>
      ) : null}

      {enabled && hasFailure ? (
        <p className="mt-4 rounded-lg border border-risk-high/30 bg-risk-high/10 px-4 py-3 text-sm text-risk-high">
          Report generation failed. Please try again.
        </p>
      ) : null}
    </section>
  );
}
