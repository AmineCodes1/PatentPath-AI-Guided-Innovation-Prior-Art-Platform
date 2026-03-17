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

export type RecentSearch = {
  id: string;
  project_id: string;
  query_text: string;
  result_count: number;
  status: "PENDING" | "PROCESSING" | "COMPLETE" | "FAILED";
  executed_at: string;
};
