/**
 * Report generation API helpers with status polling and PDF download utility.
 */

import apiClient from "./client";
import type {
  GenerateReportResponse,
  ReportStatusResponse,
} from "../types/report";

export async function generateReport(
  projectId: string,
  sessionId: string,
): Promise<GenerateReportResponse> {
  const response = await apiClient.post<GenerateReportResponse>("/reports/generate", {
    project_id: projectId,
    session_id: sessionId,
  });
  return response.data;
}

export async function getReportStatus(jobId: string): Promise<ReportStatusResponse> {
  const response = await apiClient.get<ReportStatusResponse>(`/reports/status/${jobId}`);
  return response.data;
}

export async function pollReportStatus(
  jobId: string,
  onUpdate?: (payload: ReportStatusResponse) => void,
  intervalMs = 2000,
  maxAttempts = 120,
): Promise<ReportStatusResponse> {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const payload = await getReportStatus(jobId);
    onUpdate?.(payload);

    if (payload.status === "READY" || payload.status === "FAILED") {
      return payload;
    }

    await new Promise<void>((resolve) => {
      globalThis.setTimeout(resolve, intervalMs);
    });
  }

  throw new Error("Report generation timed out.");
}

export async function fetchReportBlob(jobId: string): Promise<Blob> {
  const response = await apiClient.get<Blob>(`/reports/download/${jobId}`, {
    responseType: "blob",
  });
  return response.data;
}

export async function downloadReport(jobId: string): Promise<number> {
  const blob = await fetchReportBlob(jobId);
  const blobUrl = globalThis.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = blobUrl;
  anchor.download = `patent_preparation_report_${jobId}.pdf`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  globalThis.URL.revokeObjectURL(blobUrl);
  return blob.size;
}
