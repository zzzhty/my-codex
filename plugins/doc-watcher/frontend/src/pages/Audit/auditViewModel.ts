import type {
  AuditFinding,
  AuditReportListResponse,
  AuditReportSummary,
  AuditRepoStatus,
  AuditRunListResponse,
  AuditRunRecord,
  AuditStatusResponse,
} from "../../types/audit";
import { findingSeverityText, formatDate } from "./auditViewUtils";

export type MetricTone = "neutral" | "amber" | "green" | "rose";

export interface AuditFindingItem {
  repo: AuditRepoStatus;
  finding: AuditFinding;
  index: number;
}

export interface AuditMetricView {
  label: string;
  value: number;
  detail: string;
  tone: MetricTone;
}

export interface AuditDashboardViewModel {
  subtitle: string;
  repos: AuditRepoStatus[];
  dueRepos: AuditRepoStatus[];
  errorRepos: AuditRepoStatus[];
  findings: AuditFindingItem[];
  findingPreview: AuditFindingItem[];
  latestReport: AuditReportSummary | null;
  latestRun: AuditRunRecord | null;
  recentReports: AuditReportSummary[];
  recentRuns: AuditRunRecord[];
  busy: boolean;
  metrics: {
    configuredRepos: AuditMetricView;
    dueRepos: AuditMetricView;
    openFindings: AuditMetricView;
    reports: AuditMetricView;
  };
}

export function buildAuditDashboardViewModel({
  status,
  reports,
  runs,
  busy,
}: {
  status: AuditStatusResponse | undefined;
  reports: AuditReportListResponse | undefined;
  runs: AuditRunListResponse | undefined;
  busy: boolean;
}): AuditDashboardViewModel {
  const repos = status?.repos ?? [];
  const dueRepos = repos.filter((repo) => repo.due);
  const errorRepos = repos.filter((repo) => repo.status === "error");
  const findings = repos.flatMap((repo) =>
    repo.findings.map((finding, index) => ({ repo, finding, index })),
  );
  const latestReport = status?.reports.latest ?? null;
  const latestRun = runs?.runs[0] ?? null;
  const findingPreview = findings.slice(0, 12);
  const recentReports = (reports?.reports ?? []).slice(0, 5);
  const recentRuns = (runs?.runs ?? []).slice(0, 5);

  return {
    subtitle: status?.config.path || "No audit config loaded",
    repos,
    dueRepos,
    errorRepos,
    findings,
    findingPreview,
    latestReport,
    latestRun,
    recentReports,
    recentRuns,
    busy,
    metrics: {
      configuredRepos: {
        label: "Configured Repos",
        value: status?.config.repo_count ?? 0,
        detail: status?.config.exists ? "config loaded" : "config missing",
        tone: "neutral",
      },
      dueRepos: {
        label: "Due Repos",
        value: dueRepos.length,
        detail: `${errorRepos.length} repo errors`,
        tone: dueRepos.length ? "amber" : "green",
      },
      openFindings: {
        label: "Open Findings",
        value: findings.length,
        detail: findingSeverityText(findings.map((item) => item.finding)),
        tone: findings.length ? "rose" : "green",
      },
      reports: {
        label: "Reports",
        value: status?.reports.count ?? 0,
        detail: latestReport ? formatDate(latestReport.modified_at) : "no reports",
        tone: "neutral",
      },
    },
  };
}
