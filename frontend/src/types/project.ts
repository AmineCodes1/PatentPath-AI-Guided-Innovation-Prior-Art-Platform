/**
 * Project and dashboard related frontend types.
 */

export type ProjectStatus = "ACTIVE" | "ARCHIVED" | "REPORT_READY";

export type InnovationProject = {
  id: string;
  user_id: string;
  title: string;
  problem_statement: string;
  domain_ipc_class: string | null;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
  sessions_count: number;
};

export type ProjectCreatePayload = {
  title: string;
  problem_statement: string;
  domain_ipc_class?: string;
};

export type ProjectUpdatePayload = Partial<{
  title: string;
  problem_statement: string;
  status: ProjectStatus;
  domain_ipc_class: string;
}>;

export type SearchSessionStatus = "PENDING" | "PROCESSING" | "COMPLETE" | "FAILED";

export type ProjectSessionSummary = {
  id: string;
  query_text: string;
  cql_generated: string;
  result_count: number;
  status: SearchSessionStatus;
  executed_at: string;
};

export type TimelineEventType = "SEARCH" | "ANALYSIS" | "REPORT";

export type ProjectTimelineEvent = {
  event_type: TimelineEventType;
  timestamp: string;
  title: string;
  summary: string;
  session_id: string | null;
};

export type ProjectRiskTrendPoint = {
  session_date: string;
  overall_risk: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  avg_composite_score: number;
};

export type ProjectNote = {
  id: string;
  project_id: string;
  title: string;
  content: string;
  linked_session_id: string | null;
  created_at: string;
};

export type ProjectNoteCreatePayload = {
  title: string;
  content: string;
  linked_session_id?: string;
};

export type RecentSearch = {
  id: string;
  project_id: string;
  query_text: string;
  result_count: number;
  status: SearchSessionStatus;
  executed_at: string;
};
