export interface AuditFinding {
  fingerprint: string;
  severity: string;
  title: string;
  evidence: string;
}

export interface AuditReportSummary {
  id: string;
  path: string;
  title: string;
  modified_at: string;
  size_bytes: number;
  generated_at: string | null;
  config_path: string | null;
  audited_repos: number | null;
  skipped_repos: number | null;
  failed_repos: number | null;
  repo_sections: string[];
}

export interface AuditReportDetail extends AuditReportSummary {
  content: string;
}

export interface AuditRepoState {
  path?: string;
  last_audited_revision?: string;
  config_hash?: string;
  updated_at?: string;
  findings?: AuditFinding[];
}

export interface AuditRepoStatus {
  name: string;
  configured_path: string;
  docs: string[];
  source_of_truth: string[];
  watch_terms: string[];
  recent_limit: number;
  commit_threshold: number;
  state: AuditRepoState;
  findings: AuditFinding[];
  config_hash: string;
  last_config_hash: string | null;
  status: "ok" | "error" | string;
  error?: string;
  path?: string;
  head?: string;
  last_audited_revision?: string | null;
  config_changed?: boolean;
  commits_since_audit?: number;
  due?: boolean;
}

export interface AuditStatusResponse {
  config: {
    path: string;
    exists: boolean;
    repo_count: number;
  };
  state: {
    dir: string;
    path: string;
    exists: boolean;
    repo_count: number;
  };
  reports: {
    dir: string;
    exists: boolean;
    count: number;
    latest: AuditReportSummary | null;
  };
  repos: AuditRepoStatus[];
  last_run: AuditReportSummary | null;
}

export interface AuditRepoListResponse {
  repos: AuditRepoStatus[];
  total: number;
}

export interface AuditReportListResponse {
  reports: AuditReportSummary[];
  total: number;
  reports_dir: string;
  reports_dir_exists: boolean;
}

export interface AuditRunRecord {
  id: string;
  kind: "commit_counter" | "generate_report" | "audit_repo" | string;
  lock_key: string;
  command: string[];
  cwd: string;
  config_path: string;
  state_dir: string;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  exit_code: number;
  success: boolean;
  stdout: string;
  stdout_truncated: boolean;
  stderr: string;
  stderr_truncated: boolean;
  report_path: string | null;
  audit_path: string | null;
  updated_state_path: string | null;
  failure_breakpoint: string | null;
}

export interface AuditRunListResponse {
  runs: AuditRunRecord[];
  total: number;
  runs_dir: string;
  runs_dir_exists: boolean;
}

export interface GenerateReportRunRequest {
  mode?: "all" | "commit-dependent";
  mark_audited?: boolean;
  digest?: boolean;
  print_report?: boolean;
}
