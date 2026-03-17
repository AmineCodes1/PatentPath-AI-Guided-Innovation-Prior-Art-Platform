/**
 * Main guided search workflow page with query generation and result review.
 */

import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import type { ReactElement } from "react";
import TopNav from "../components/layout/TopNav";
import FilterSidebar from "../components/search/FilterSidebar";
import PatentResultCard from "../components/search/PatentResultCard";
import apiClient from "../api/client";
import type {
  ExecuteSearchResponse,
  RiskLabel,
  ScoredResult,
  SearchFilters,
  SearchPreviewResponse,
  SearchResultsResponse,
} from "../types/search";
import { useProjectStore } from "../store/projectStore";

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
  const [resultFilters, setResultFilters] = useState<ResultFilters>({
    risk: "ALL",
    country: "",
    dateFrom: "",
    dateTo: "",
  });

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
    const intervalId = window.setInterval(() => {
      current += 1;
      setLoadingPhase(Math.min(current, PHASE_MESSAGES.length - 1));
      if (current >= PHASE_MESSAGES.length - 1) {
        window.clearInterval(intervalId);
      }
    }, 1200);
  };

  const handleExecute = async (): Promise<void> => {
    if (!activeProjectId || !cqlText.trim()) {
      return;
    }

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
      const resultsResponse = await apiClient.get<SearchResultsResponse>(
        `/search/session/${targetSessionId}/results`,
      );

      setResults(resultsResponse.data.results.sort((a, b) => b.composite_score - a.composite_score));
      setSelectedResult(resultsResponse.data.results[0] ?? null);
    } catch {
      setResults([]);
    } finally {
      setIsExecuting(false);
    }
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
          {!collapsedSidebar ? (
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
          ) : null}
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
            <h2 className="text-lg font-semibold text-text-primary">Step 2 — Review & Refine Query</h2>
            <textarea
              value={cqlText}
              onChange={(event) => setCqlText(event.target.value)}
              className="mt-3 h-24 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 font-mono text-sm text-text-primary outline-none focus:border-accent"
              placeholder='(ti="keyword" OR ab="keyword")'
            />

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <label className="text-sm text-text-secondary">
                Date from
                <input
                  type="date"
                  value={filters.date_from ?? ""}
                  onChange={(event) => setFilters((state) => ({ ...state, date_from: event.target.value }))}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                />
              </label>
              <label className="text-sm text-text-secondary">
                Date to
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
                IPC Classes
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
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-text-primary outline-none focus:border-accent"
                />
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
                Legal status
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
            <h2 className="text-lg font-semibold text-text-primary">Step 3 — Prior Art Results</h2>
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
                  <p className="rounded-lg bg-surface p-4 text-sm text-text-secondary">
                    No results yet. Execute the search to see ranked patents.
                  </p>
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
            <p className="mt-2 rounded-lg bg-accent/10 p-3 text-sm text-primary">
              GapAnalysisPanel placeholder: detailed AI novelty gap analysis will be mounted here in Task 4.
            </p>
          </article>
        </section>

        <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-panel">
          <h2 className="text-sm font-semibold uppercase tracking-widest text-primary">Patent Detail</h2>
          {selectedResult ? (
            <div className="mt-3 space-y-2 text-sm">
              <p className="font-semibold text-text-primary">{selectedResult.patent.title}</p>
              <p className="text-text-secondary">{selectedResult.patent.publication_number}</p>
              <p className="text-text-secondary">{selectedResult.patent.abstract}</p>
              <a
                href={selectedResult.patent.espacenet_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex rounded-lg border border-primary px-3 py-1.5 text-xs font-semibold text-primary transition hover:bg-primary hover:text-white"
              >
                Open in Espacenet
              </a>
            </div>
          ) : (
            <p className="mt-3 text-sm text-text-secondary">Select a result to preview details.</p>
          )}
        </aside>
      </main>
    </div>
  );
}
