/**
 * Utilities for exporting scored search results as downloadable CSV files.
 */

import type { ScoredResult } from "../types/search";

function escapeCsvField(value: string): string {
  if (value.includes(",") || value.includes("\n") || value.includes("\"")) {
    return `"${value.replaceAll("\"", '""')}"`;
  }
  return value;
}

export function exportResultsToCSV(results: ScoredResult[], filename: string): void {
  const header = [
    "Rank",
    "Publication Number",
    "Title",
    "Composite Score",
    "Risk Label",
    "Espacenet URL",
  ];

  const rows = results.map((result) => [
    String(result.rank),
    result.patent.publication_number,
    result.patent.title,
    result.composite_score.toFixed(4),
    result.risk_label,
    result.patent.espacenet_url,
  ]);

  const csv = [header, ...rows]
    .map((row) => row.map((field) => escapeCsvField(field)).join(","))
    .join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
