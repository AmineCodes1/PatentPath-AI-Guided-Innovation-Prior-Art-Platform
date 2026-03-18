/**
 * In-app documentation page for workflow, algorithm, architecture, and usage guidance.
 */

import type { ReactElement } from "react";
import Footer from "../components/layout/Footer";
import TopNav from "../components/layout/TopNav";

const RISK_ROWS = [
  {
    range: "0.80 - 1.00",
    label: "HIGH",
    meaning: "Strong overlap with prior art; filing strategy needs substantial differentiation.",
    color: "text-risk-high",
  },
  {
    range: "0.55 - 0.79",
    label: "MEDIUM",
    meaning: "Partial overlap; promising with focused claim narrowing and technical novelty.",
    color: "text-risk-medium",
  },
  {
    range: "0.30 - 0.54",
    label: "LOW",
    meaning: "Limited overlap; invention may have room for defensible novelty claims.",
    color: "text-risk-low",
  },
  {
    range: "0.00 - 0.29",
    label: "MINIMAL",
    meaning: "Very low overlap; likely novel direction, still requires legal validation.",
    color: "text-risk-minimal",
  },
] as const;

export default function DocsPage(): ReactElement {
  const swaggerUrl =
    globalThis.location.port === "5173"
      ? `${globalThis.location.protocol}//${globalThis.location.hostname}:8000/docs`
      : "/docs";

  return (
    <div className="min-h-screen bg-surface">
      <TopNav />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <section className="rounded-2xl border border-blue-100 bg-white p-7 shadow-panel">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">PatentPath Documentation</p>
          <h1 className="mt-2 text-3xl font-bold text-text-primary">How PatentPath Works</h1>
          <p className="mt-3 max-w-4xl text-sm text-text-secondary">
            PatentPath guides your invention idea from problem framing to prior-art analysis, novelty risk estimation,
            and report generation in one workflow.
          </p>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-primary">1. Frame Your Invention</p>
              <p className="mt-2 text-sm text-text-secondary">
                Write a precise problem statement, refine IPC filters, and review generated CQL before execution.
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-primary">2. Analyze Prior Art</p>
              <p className="mt-2 text-sm text-text-secondary">
                Query OPS, score patents with BM25 plus TF-IDF plus semantic embeddings, and inspect ranked results.
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-primary">3. Act on Insights</p>
              <p className="mt-2 text-sm text-text-secondary">
                Interpret gap analysis, evaluate feasibility, then generate a structured patent preparation PDF.
              </p>
            </div>
          </div>

          <figure className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white p-3">
            <img
              src="/diagrams/main_workflow.svg"
              alt="PatentPath end-to-end workflow diagram"
              className="h-auto w-full"
              loading="lazy"
            />
          </figure>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-7 shadow-panel">
          <h2 className="text-2xl font-bold text-text-primary">NLP Scoring Algorithm</h2>
          <p className="mt-3 text-sm text-text-secondary">
            Similarity score (SS) blends three complementary views of relevance. PatentPath weights the components as:
            BM25 lexical relevance (30%), TF-IDF claim similarity (50%), and semantic embedding alignment (20%).
          </p>
          <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-text-primary">
            SS = 0.30 x BM25_norm + 0.50 x TF-IDF_cosine + 0.20 x Semantic_cosine
          </div>
          <figure className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white p-3">
            <img
              src="/diagrams/nlp_pipeline.svg"
              alt="NLP scoring pipeline diagram with parallel tracks"
              className="h-auto w-full"
              loading="lazy"
            />
          </figure>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-7 shadow-panel">
          <h2 className="text-2xl font-bold text-text-primary">Understanding Your Risk Score</h2>
          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-text-secondary">
                  <th className="px-3 py-2 font-semibold">SS Range</th>
                  <th className="px-3 py-2 font-semibold">Risk Label</th>
                  <th className="px-3 py-2 font-semibold">Interpretation</th>
                </tr>
              </thead>
              <tbody>
                {RISK_ROWS.map((row) => (
                  <tr key={row.label} className="border-b border-slate-100">
                    <td className="px-3 py-2 font-medium text-text-primary">{row.range}</td>
                    <td className={`px-3 py-2 font-semibold ${row.color}`}>{row.label}</td>
                    <td className="px-3 py-2 text-text-secondary">{row.meaning}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-7 shadow-panel">
          <h2 className="text-2xl font-bold text-text-primary">System Architecture</h2>
          <p className="mt-3 text-sm text-text-secondary">
            Data flows between the React client, FastAPI services, OPS retrieval, Claude analysis, and asynchronous NLP
            workers over authenticated JSON APIs and queued processing.
          </p>
          <figure className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white p-3">
            <img
              src="/diagrams/data_flow.svg"
              alt="System architecture and data-flow diagram"
              className="h-auto w-full"
              loading="lazy"
            />
          </figure>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-2">
          <article className="rounded-2xl border border-slate-200 bg-white p-7 shadow-panel">
            <h2 className="text-2xl font-bold text-text-primary">API Documentation</h2>
            <p className="mt-3 text-sm text-text-secondary">
              Explore live backend schemas, request bodies, and response contracts through the FastAPI Swagger UI.
            </p>
            <a
              href={swaggerUrl}
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-900"
            >
              Open Swagger UI
            </a>
          </article>

          <article className="rounded-2xl border border-amber-300 bg-amber-50 p-7 shadow-panel">
            <h2 className="text-2xl font-bold text-amber-900">Legal Notice</h2>
            <p className="mt-3 text-sm leading-6 text-amber-900">
              PatentPath provides computational prior-art support and innovation guidance. Outputs, risk labels,
              feasibility indicators, and generated reports are informational only and do not constitute legal advice,
              patentability opinion, freedom-to-operate clearance, or representation before any patent office. Always
              consult a qualified patent attorney or registered patent agent before filing or acting on results.
            </p>
          </article>
        </section>
      </main>
      <Footer />
    </div>
  );
}
