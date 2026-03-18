/**
 * Types used by report generation APIs and UI state.
 */

export type ReportJobStatus = "PENDING" | "PROCESSING" | "READY" | "FAILED";

export type GenerateReportRequest = {
  project_id: string;
  session_id: string;
};

export type GenerateReportResponse = {
  job_id: string;
  status: "PENDING";
};

export type ReportStatusResponse = {
  job_id: string;
  status: ReportJobStatus;
  download_url?: string;
};

export type ActiveReportJob = {
  job_id: string;
  project_id: string;
  session_id: string;
  status: ReportJobStatus;
  updated_at: string;
  error: string | null;
};

export type CompletedReport = {
  job_id: string;
  project_id: string;
  session_id: string;
  session_date: string;
  generated_at: string;
  viewed_at: string | null;
  file_size_bytes: number | null;
};
