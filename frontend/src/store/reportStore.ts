/**
 * Zustand store for report generation jobs and completed report history.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  downloadReport,
  fetchReportBlob,
  generateReport,
  pollReportStatus,
} from "../api/reports";
import type {
  ActiveReportJob,
  CompletedReport,
  ReportJobStatus,
} from "../types/report";

type ReportStoreState = {
  activeReportJobs: Record<string, ActiveReportJob>;
  completedReports: CompletedReport[];
  createAndTrackReport: (projectId: string, sessionId: string, sessionDate?: string) => Promise<string>;
  updateJobStatus: (jobId: string, status: ReportJobStatus, error?: string | null) => void;
  setReportFileSize: (jobId: string, fileSizeBytes: number) => void;
  markReportViewed: (jobId: string) => void;
  downloadCompletedReport: (jobId: string) => Promise<number>;
  getReportsForProject: (projectId: string) => CompletedReport[];
};

function nowIso(): string {
  return new Date().toISOString();
}

export const useReportStore = create<ReportStoreState>()(
  persist(
    (set, get) => ({
      activeReportJobs: {},
      completedReports: [],
      createAndTrackReport: async (projectId, sessionId, sessionDate) => {
        const generated = await generateReport(projectId, sessionId);
        const jobId = generated.job_id;

        set((state) => ({
          activeReportJobs: {
            ...state.activeReportJobs,
            [jobId]: {
              job_id: jobId,
              project_id: projectId,
              session_id: sessionId,
              status: "PENDING",
              updated_at: nowIso(),
              error: null,
            },
          },
        }));

        const finalStatus = await pollReportStatus(jobId, (payload) => {
          get().updateJobStatus(jobId, payload.status);
        });

        if (finalStatus.status === "FAILED") {
          get().updateJobStatus(jobId, "FAILED", "Report generation failed.");
          return jobId;
        }

        const reportBlob = await fetchReportBlob(jobId);

        set((state) => {
          const existingIndex = state.completedReports.findIndex((item) => item.job_id === jobId);
          const entry: CompletedReport = {
            job_id: jobId,
            project_id: projectId,
            session_id: sessionId,
            session_date: sessionDate ?? nowIso(),
            generated_at: nowIso(),
            viewed_at: null,
            file_size_bytes: reportBlob.size,
          };

          const completedReports = [...state.completedReports];
          if (existingIndex >= 0) {
            completedReports[existingIndex] = entry;
          } else {
            completedReports.unshift(entry);
          }

          const activeReportJobs = { ...state.activeReportJobs };
          activeReportJobs[jobId] = {
            ...(activeReportJobs[jobId] ?? {
              job_id: jobId,
              project_id: projectId,
              session_id: sessionId,
              error: null,
            }),
            status: "READY",
            updated_at: nowIso(),
          } as ActiveReportJob;

          return {
            completedReports,
            activeReportJobs,
          };
        });

        return jobId;
      },
      updateJobStatus: (jobId, status, error = null) => {
        set((state) => {
          const current = state.activeReportJobs[jobId];
          if (!current) {
            return state;
          }
          return {
            activeReportJobs: {
              ...state.activeReportJobs,
              [jobId]: {
                ...current,
                status,
                error,
                updated_at: nowIso(),
              },
            },
          };
        });
      },
      setReportFileSize: (jobId, fileSizeBytes) => {
        set((state) => ({
          completedReports: state.completedReports.map((item) => (
            item.job_id === jobId
              ? { ...item, file_size_bytes: fileSizeBytes }
              : item
          )),
        }));
      },
      markReportViewed: (jobId) => {
        set((state) => ({
          completedReports: state.completedReports.map((item) => (
            item.job_id === jobId
              ? { ...item, viewed_at: nowIso() }
              : item
          )),
        }));
      },
      downloadCompletedReport: async (jobId) => {
        const bytes = await downloadReport(jobId);
        get().setReportFileSize(jobId, bytes);
        get().markReportViewed(jobId);
        return bytes;
      },
      getReportsForProject: (projectId) => get().completedReports.filter((item) => item.project_id === projectId),
    }),
    {
      name: "patentpath-report-store",
      partialize: (state) => ({
        activeReportJobs: state.activeReportJobs,
        completedReports: state.completedReports,
      }),
    },
  ),
);
