/**
 * Main guided search workflow page with query generation and result review.
 */

import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import type { ReactElement } from "react";
import TopNav from "../components/layout/TopNav";
import Footer from "../components/layout/Footer";
import FilterSidebar from "../components/search/FilterSidebar";
import IPCBrowserModal from "../components/search/IPCBrowserModal";
import PatentResultCard from "../components/search/PatentResultCard";
import GapAnalysisPanel from "../components/analysis/GapAnalysisPanel";
import FeasibilityWidget from "../components/analysis/FeasibilityWidget";
import PatentDetailPanel from "../components/analysis/PatentDetailPanel";
import ErrorBanner from "../components/common/ErrorBanner";
import EmptyState from "../components/common/EmptyState";
import LegalDisclaimer from "../components/common/LegalDisclaimer";
import LoadingOverlay from "../components/common/LoadingOverlay";
import ReportGeneratorPanel from "../components/report/ReportGeneratorPanel";
import apiClient from "../api/client";
import { exportResultsToCSV } from "../utils/exportUtils";
import type {
  ExecuteSearchResponse,
  RiskLabel,
  ScoredResult,
  SearchFilters,
  SearchPreviewResponse,
  SearchResultsResponse,
} from "../types/search";
import { useProjectStore } from "../store/projectStore";
import { useAnalysisStore } from "../store/analysisStore";

type ResultFilters = {
  risk: RiskLabel | "ALL";
  country: string;
  dateFrom: string;
  dateTo: string;
};

const COUNTRIES = ["EP", "WO", "US", "JP", "CN", "KR", "DE", "FR", "GB"];

const PHASE_MESSAGES = [
  "Building query...",
  "Querying Espacenet...",
  "Scoring results...",
  "Generating gap analysis...",
];

type ExecuteErrorInfo = {
  errorCode?: string;
  message: string;
  retryAfterSeconds?: number;
};

function parseExecuteError(error: unknown): ExecuteErrorInfo {
  const maybeResponse = (error as { response?: { data?: unknown } })?.response;
  const maybeData = maybeResponse?.data as {
    detail?: string;
    message?: string;
    error_code?: string;
    retry_after_seconds?: number;
  } | undefined;

  return {
    errorCode: maybeData?.error_code,
    message: maybeData?.message || maybeData?.detail || "Search execution failed. Please try again.",
    retryAfterSeconds: maybeData?.retry_after_seconds,
  };
}

function emptySearchFilters(): SearchFilters {
  return {
    country_codes: [],
    ipc_classes: [],
    applicant: "",
    legal_status: "",
  };
}

export default function SearchPage(): ReactElement {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [searchParams] = useSearchParams();
  const projects = useProjectStore((state) => state.projects);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);
  const setCurrentProject = useProjectStore((state) => state.setCurrentProject);

  const [activeProjectId, setActiveProjectId] = useState<string>(projects[0]?.id ?? "");
  const [collapsedSidebar, setCollapsedSidebar] = useState(false);

  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [queryText, setQueryText] = useState("");
  const [preview, setPreview] = useState<SearchPreviewResponse | null>(null);
  const [cqlText, setCqlText] = useState("");
  const [filters, setFilters] = useState<SearchFilters>(emptySearchFilters());
  const [loadingPhase, setLoadingPhase] = useState(0);
  const [isExecuting, setIsExecuting] = useState(false);
  const [results, setResults] = useState<ScoredResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<ScoredResult | null>(null);
  const [searchSessionId, setSearchSessionId] = useState<string>(sessionId ?? "");
  const [ipcModalOpen, setIpcModalOpen] = useState(false);
  const [executeError, setExecuteError] = useState<ExecuteErrorInfo | null>(null);
  const [resultFilters, setResultFilters] = useState<ResultFilters>({
    risk: "ALL",
    country: "",
    dateFrom: "",
    dateTo: "",
  });

  const analysisStatus = useAnalysisStore((state) => state.status);
  const analysisError = useAnalysisStore((state) => state.error);
  const analysisSessionId = useAnalysisStore((state) => state.sessionId);
  const gapAnalysis = useAnalysisStore((state) => state.gapAnalysis);
  const feasibility = useAnalysisStore((state) => state.feasibility);
  const runGapAnalysisForSession = useAnalysisStore((state) => state.runGapAnalysisForSession);
  const resetAnalysis = useAnalysisStore((state) => state.resetAnalysis);

  useEffect(() => {
    void fetchProjects();
  }, [fetchProjects]);

  useEffect(() => {
    if (!activeProjectId && projects.length > 0) {
      const firstProject = projects[0];
      if (firstProject) {
        setActiveProjectId(firstProject.id);
        setCurrentProject(firstProject);
      }
    }
  }, [activeProjectId, projects, setCurrentProject]);

  useEffect(() => {
    if (sessionId) {
      setSearchSessionId(sessionId);
    }
  }, [sessionId]);

  useEffect(() => {
    if (searchParams.get("rerun") !== "1") {
      return;
    }

    const rawPayload = globalThis.sessionStorage.getItem("patentpath-rerun-session");
    if (!rawPayload) {
      return;
    }

    try {
      const payload = JSON.parse(rawPayload) as {
        project_id?: string;
        query_text?: string;
        cql_generated?: string;
      };

      if (payload.project_id) {
        setActiveProjectId(payload.project_id);
      }
      if (payload.query_text) {
        setQueryText(payload.query_text);
      }
      if (payload.cql_generated) {
        setCqlText(payload.cql_generated);
        setStep(2);
      }
    } catch {
      // Ignore malformed rerun payload and continue with default empty form state.
    } finally {
      globalThis.sessionStorage.removeItem("patentpath-rerun-session");
    }
  }, [searchParams]);

  useEffect(() => {
    if (step !== 4 || !searchSessionId) {
      return;
    }

    if (
      analysisSessionId === searchSessionId
      && (analysisStatus === "processing" || analysisStatus === "complete")
    ) {
      return;
    }

    void runGapAnalysisForSession(searchSessionId);
  }, [analysisSessionId, analysisStatus, runGapAnalysisForSession, searchSessionId, step]);

  const canPreview = queryText.trim().length >= 100;

  const filteredResults = useMemo(() => {
    return results.filter((item) => {
      if (resultFilters.risk !== "ALL" && item.risk_label !== resultFilters.risk) {
        return false;
      }
      if (resultFilters.country && !item.patent.publication_number.startsWith(resultFilters.country)) {
        return false;
      }
      if (resultFilters.dateFrom && item.patent.publication_date < resultFilters.dateFrom) {
        return false;
      }
      if (resultFilters.dateTo && item.patent.publication_date > resultFilters.dateTo) {
        return false;
      }
      return true;
    });
  }, [resultFilters, results]);

  const handlePreviewQuery = async (): Promise<void> => {
    if (!canPreview) {
      return;
    }

    const payload = {
      query_text: queryText,
      filters,
    };

    const response = await apiClient.post<SearchPreviewResponse>("/search/preview-query", payload);
    setPreview(response.data);
    setCqlText(response.data.cql_generated);
    setStep(2);
  };

  const simulateLoadingPhases = (): void => {
    setLoadingPhase(0);
    let current = 0;
    const intervalId = globalThis.setInterval(() => {
      current += 1;
      setLoadingPhase(Math.min(current, PHASE_MESSAGES.length - 1));
      if (current >= PHASE_MESSAGES.length - 1) {
        globalThis.clearInterval(intervalId);
      }
    }, 1200);
  };

  const handleExecute = async (): Promise<void> => {
    if (!activeProjectId || queryText.trim().length < 10) {
      return;
    }

    resetAnalysis();
    setExecuteError(null);
    setSearchSessionId("");
    setIsExecuting(true);
    setStep(3);
    simulateLoadingPhases();

    try {
      const executePayload = {
        project_id: activeProjectId,
        query_text: queryText,
        cql_override: cqlText,
        filters,
      };

      const executeResponse = await apiClient.post<ExecuteSearchResponse>(
        "/search/execute",
        executePayload,
      );
      const targetSessionId = executeResponse.data.session_id || sessionId;
      if (!targetSessionId) {
        throw new Error("No session id returned from search execution.");
      }

      setSearchSessionId(targetSessionId);
      const resultsResponse = await apiClient.get<SearchResultsResponse>(
        `/search/session/${targetSessionId}/results`,
      );

      const sortedResults = [...resultsResponse.data.results].sort((a, b) => b.composite_score - a.composite_score);
      setResults(sortedResults);
      setSelectedResult(sortedResults[0] ?? null);
      setStep(4);
    } catch (error: unknown) {
      setResults([]);
      setSelectedResult(null);
      setSearchSessionId("");
      setExecuteError(parseExecuteError(error));
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCopyCql = async (): Promise<void> => {
    if (!cqlText.trim()) {
      return;
    }
    await navigator.clipboard.writeText(cqlText);
  };

  const handleExportResults = async (): Promise<void> => {
    if (searchSessionId) {
      const response = await apiClient.get(`/search/session/${searchSessionId}/results/export`, {
        responseType: "blob",
      });
      const blob = new Blob([response.data], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `patentpath_results_${searchSessionId}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      return;
    }

    exportResultsToCSV(results, `patentpath_results_${Date.now()}.csv`);
  };

  const toggleCountry = (country: string): void => {
    setFilters((current) => {
      const exists = current.country_codes.includes(country);
      const country_codes = exists
        ? current.country_codes.filter((code) => code !== country)
        : [...current.country_codes, country];
      return { ...current, country_codes };
    });
  };

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto grid max-w-[1400px] grid-cols-1 gap-5 px-4 py-6 xl:grid-cols-[260px_minmax(0,1fr)_320px]">
        <aside className={`rounded-2xl border border-slate-200 bg-white p-4 shadow-panel ${collapsedSidebar ? "h-16" : ""}`}>
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-primary">Projects</h2>
            <button
              type="button"
              onClick={() => setCollapsedSidebar((value) => !value)}
              className="text-xs font-medium text-accent"
            >
              {collapsedSidebar ? "Expand" : "Collapse"}
            </button>
          </div>
          {collapsedSidebar ? null : (
            <div className="mt-3 space-y-2">
              {projects.map((project) => (
                <button
                  type="button"
                  key={project.id}
                  onClick={() => {
                    setActiveProjectId(project.id);
                    setCurrentProject(project);
                  }}
                  className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                    activeProjectId === project.id
                      ? "bg-primary text-white"
                      : "bg-surface text-text-primary hover:bg-accent/20"
                  }`}
                >
                  {project.title}
                </button>
              ))}
            </div>
          )}
        </aside>

        <section className="space-y-5">
          <header className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-widest text-accent">Session {sessionId ?? "new"}</p>
            <h1 className="mt-2 text-2xl font-bold text-text-primary">Patent Search Workflow</h1>
            <div className="mt-4 grid gap-2 sm:grid-cols-4">
              {["Describe", "Refine", "Results", "Gap Analysis"].map((label, index) => {
                const indexStep = (index + 1) as 1 | 2 | 3 | 4;
                const active = step >= indexStep;
                return (
                  <div
                    key={label}
                    className={`rounded-lg px-3 py-2 text-sm font-medium ${
                      active ? "bg-primary text-white" : "bg-surface text-text-secondary"
                    }`}
                  >
                    Step {index + 1}: {label}
                  </div>
                );
              })}
            </div>
          </header>

          <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-text-primary">Step 1 — Describe Your Invention</h2>
            <textarea
              value={queryText}
              onChange={(event) => setQueryText(event.target.value)}
              onKeyDown={(event) => {
                if (event.ctrlKey && event.key === "Enter") {
                  event.preventDefault();
                  void handleExecute();
                }
              }}
              className="mt-3 h-36 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-text-primary outline-none focus:border-accent"
              placeholder="Describe your invention with technical details, architecture, and novelty targets..."
            />
            <div className="mt-2 flex items-center justify-between text-xs">
              <span className={queryText.length < 100 ? "text-risk-high" : "text-risk-low"}>
                {queryText.length}/100 minimum characters
              </span>
              <button
                type="button"
                disabled={!canPreview}
                onClick={() => void handlePreviewQuery()}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-60"
              >
                AI Suggest IPC Classes
              </button>
            </div>

            {preview ? (
              <div className="mt-4 flex flex-wrap gap-2">
                {preview.keywords_extracted.map((keyword) => (
                  <span key={keyword} className="rounded-full bg-accent/20 px-3 py-1 text-xs font-medium text-primary">
                    {keyword}
                  </span>
                ))}
                {preview.ipc_suggestions.map((ipc) => (
                  <span key={ipc} className="rounded-full bg-primary/15 px-3 py-1 text-xs font-semibold text-primary">
                    {ipc}
                  </span>
                ))}
              </div>
            ) : null}
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-text-primary">Step 2 — Review & Refine Query</h2>
              <button
                type="button"
                onClick={() => void handleCopyCql()}
                className="rounded-lg border border-primary/40 px-3 py-1.5 text-xs font-semibold text-primary hover:bg-primary hover:text-white"
              >
                Copy CQL
              </button>
            </div>
            <textarea
              value={cqlText}
              onChange={(event) => setCqlText(event.target.value)}
              className="mt-3 h-24 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 font-mono text-sm text-text-primary outline-none focus:border-accent"
              placeholder='(ti="keyword" OR ab="keyword")'
            />

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <label className="text-sm text-text-secondary">
                <span>Date from</span>
                <input
                  type="date"
                  value={filters.date_from ?? ""}
                  onChange={(event) => setFilters((state) => ({ ...state, date_from: event.target.value }))}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                />
              </label>
              <label className="text-sm text-text-secondary">
                <span>Date to</span>
                <input
                  type="date"
                  value={filters.date_to ?? ""}
                  onChange={(event) => setFilters((state) => ({ ...state, date_to: event.target.value }))}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                />
              </label>
              <label className="text-sm text-text-secondary md:col-span-2">
                Country codes
                <div className="mt-2 flex flex-wrap gap-2">
                  {COUNTRIES.map((country) => {
                    const active = filters.country_codes.includes(country);
                    return (
                      <button
                        type="button"
                        key={country}
                        onClick={() => toggleCountry(country)}
                        className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                          active ? "bg-primary text-white" : "bg-surface text-text-primary"
                        }`}
                      >
                        {country}
                      </button>
                    );
                  })}
                </div>
              </label>
              <label className="text-sm text-text-secondary">
                <span>IPC Classes</span>
                <div className="mt-1 flex gap-2">
                  <input
                    type="text"
                    value={filters.ipc_classes.join(",")}
                    onChange={(event) =>
                      setFilters((state) => ({
                        ...state,
                        ipc_classes: event.target.value
                          .split(",")
                          .map((item) => item.trim().toUpperCase())
                          .filter(Boolean),
                      }))
                    }
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                  />
                  <button
                    type="button"
                    onClick={() => setIpcModalOpen(true)}
                    className="rounded-lg border border-primary/35 bg-white px-3 py-2 text-xs font-semibold text-primary hover:bg-primary/5"
                  >
                    Browse IPC/CPC
                  </button>
                </div>
              </label>
              <label className="text-sm text-text-secondary">
                Applicant
                <input
                  type="text"
                  value={filters.applicant ?? ""}
                  onChange={(event) => setFilters((state) => ({ ...state, applicant: event.target.value }))}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                />
              </label>
              <label className="text-sm text-text-secondary md:col-span-2">
                <span>Legal status</span>
                <select
                  value={filters.legal_status ?? ""}
                  onChange={(event) => setFilters((state) => ({ ...state, legal_status: event.target.value }))}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                >
                  <option value="">Any</option>
                  <option value="active">Active</option>
                  <option value="lapsed">Lapsed</option>
                  <option value="expired">Expired</option>
                </select>
              </label>
            </div>

            <button
              type="button"
              onClick={() => void handleExecute()}
              className="mt-4 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-900"
            >
              Execute Search
            </button>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-text-primary">Step 3 — Prior Art Results</h2>
              <button
                type="button"
                disabled={results.length === 0}
                onClick={() => void handleExportResults()}
                className="rounded-lg border border-primary/40 px-3 py-1.5 text-xs font-semibold text-primary disabled:cursor-not-allowed disabled:opacity-50"
              >
                Export Results CSV
              </button>
            </div>

            {executeError ? (
              <div className="mt-3">
                <ErrorBanner
                  errorCode={executeError.errorCode}
                  message={executeError.message}
                  retryAfterSeconds={executeError.retryAfterSeconds}
                  onDismiss={() => setExecuteError(null)}
                />
              </div>
            ) : null}

            {isExecuting ? (
              <div className="mt-3 rounded-xl bg-surface p-4">
                <p className="text-sm font-medium text-primary">{PHASE_MESSAGES[loadingPhase]}</p>
                <div className="mt-3 h-2 rounded-full bg-slate-200">
                  <div className={`h-2 rounded-full bg-primary transition-all duration-500 ${loadingPhase === 0 ? "w-1/4" : ""} ${loadingPhase === 1 ? "w-2/4" : ""} ${loadingPhase === 2 ? "w-3/4" : ""} ${loadingPhase === 3 ? "w-full" : ""}`} />
                </div>
              </div>
            ) : null}

            <div className="mt-4 grid gap-4 lg:grid-cols-[260px_minmax(0,1fr)]">
              <FilterSidebar filters={resultFilters} onChange={setResultFilters} />
              <div className="space-y-3">
                {filteredResults.length === 0 ? (
                  <EmptyState
                    variant="no-results"
                    title="No Results Yet"
                    subtitle="Execute a search to generate ranked prior art results and score breakdowns."
                  />
                ) : (
                  filteredResults.map((result) => (
                    <PatentResultCard key={`${result.patent.publication_number}-${result.rank}`} result={result} onExpand={setSelectedResult} />
                  ))
                )}
              </div>
            </div>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
            <h2 className="text-lg font-semibold text-text-primary">Step 4 — Gap Analysis</h2>
            <LegalDisclaimer className="mt-3" />

            <div className="mt-4 grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
              <FeasibilityWidget
                feasibility={feasibility}
                isLoading={analysisStatus === "triggering" || analysisStatus === "processing"}
              />
              <GapAnalysisPanel
                analysis={gapAnalysis}
                isLoading={analysisStatus === "triggering" || analysisStatus === "processing"}
                error={analysisError}
              />
            </div>

            <div className="mt-5">
              <ReportGeneratorPanel
                projectId={activeProjectId}
                sessionId={searchSessionId}
                enabled={Boolean(
                  activeProjectId
                  && searchSessionId
                  && analysisStatus === "complete"
                  && gapAnalysis,
                )}
              />
            </div>
          </article>
        </section>

        <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-panel">
          <PatentDetailPanel selectedResult={selectedResult} />
        </aside>
      </main>

      <IPCBrowserModal
        isOpen={ipcModalOpen}
        initialSelected={filters.ipc_classes}
        onApply={(codes) => setFilters((state) => ({ ...state, ipc_classes: codes }))}
        onClose={() => setIpcModalOpen(false)}
      />

      {isExecuting ? <LoadingOverlay message={PHASE_MESSAGES[loadingPhase] ?? "Processing search..."} /> : null}
      <Footer />
    </div>
  );
}
