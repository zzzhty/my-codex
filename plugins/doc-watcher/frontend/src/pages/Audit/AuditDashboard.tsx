import {
  AlertTriangle,
  CheckCircle2,
  CircleDot,
  FileSearch,
  Play,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  useAuditReports,
  useAuditRuns,
  useAuditStatus,
  useRunCommitCounter,
  useRunGenerateReport,
  useRunRepoAudit,
} from "../../hooks/useAudit";
import type { AuditRepoStatus, AuditRunRecord } from "../../types/audit";
import { buildAuditDashboardViewModel } from "./auditViewModel";
import { findingKey, formatDate } from "./auditViewUtils";

export default function AuditDashboard() {
  const statusQuery = useAuditStatus();
  const reportsQuery = useAuditReports();
  const runsQuery = useAuditRuns();
  const runCommitCounter = useRunCommitCounter();
  const runGenerateReport = useRunGenerateReport();
  const runRepoAudit = useRunRepoAudit();

  const status = statusQuery.data;
  const view = buildAuditDashboardViewModel({
    status,
    reports: reportsQuery.data,
    runs: runsQuery.data,
    busy: runCommitCounter.isPending || runGenerateReport.isPending || runRepoAudit.isPending,
  });
  const {
    busy,
    findingPreview,
    findings,
    latestReport,
    latestRun,
    metrics,
    recentReports,
    recentRuns,
    repos,
  } = view;

  if (statusQuery.isLoading) {
    return <Skeleton />;
  }

  if (statusQuery.error) {
    return (
      <PageShell
        title="Audit Cockpit"
        subtitle="Backend audit state is unavailable."
        action={null}
      >
        <ErrorPanel message={(statusQuery.error as Error).message} />
      </PageShell>
    );
  }

  return (
    <PageShell
      title="Audit Cockpit"
      subtitle={view.subtitle}
      action={
        <div className="flex flex-wrap items-center gap-2">
          <ActionButton
            icon={<RefreshCw size={16} />}
            label="Commit Status"
            onClick={() => runCommitCounter.mutate()}
            disabled={busy}
          />
          <ActionButton
            icon={<Play size={16} />}
            label="Full Scan"
            onClick={() => runGenerateReport.mutate({ mode: "all", print_report: false })}
            disabled={busy}
          />
          <ActionButton
            icon={<CircleDot size={16} />}
            label="Due Scan"
            onClick={() =>
              runGenerateReport.mutate({
                mode: "commit-dependent",
                mark_audited: true,
                digest: true,
              })
            }
            disabled={busy}
            primary
          />
        </div>
      }
    >
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric {...metrics.configuredRepos} />
        <Metric {...metrics.dueRepos} />
        <Metric {...metrics.openFindings} />
        <Metric {...metrics.reports} />
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          <Panel
            title="Repository Backlog"
            action={<span className="text-xs text-gray-500">{repos.length} configured</span>}
          >
            <div className="divide-y divide-gray-100">
              {repos.length ? (
                repos.map((repo) => (
                  <RepoRow
                    key={repo.name}
                    repo={repo}
                    onAudit={() => runRepoAudit.mutate(repo.name)}
                    disabled={busy}
                  />
                ))
              ) : (
                <EmptyRow label="No configured repositories." />
              )}
            </div>
          </Panel>

          <Panel
            title="Finding Backlog"
            action={<span className="text-xs text-gray-500">{findings.length} open</span>}
          >
            <div className="divide-y divide-gray-100">
              {findings.length ? (
                findingPreview.map(({ repo, finding, index }) => (
                  <Link
                    key={`${repo.name}-${findingKey(finding, index)}`}
                    to={`/audit/repos/${encodeURIComponent(repo.name)}/findings/${encodeURIComponent(
                      findingKey(finding, index),
                    )}`}
                    className="block px-5 py-4 hover:bg-gray-50"
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <SeverityBadge severity={finding.severity} />
                          <span className="text-sm font-medium text-gray-900">{finding.title}</span>
                        </div>
                        <p className="mt-1 break-words text-sm text-gray-600">{finding.evidence}</p>
                      </div>
                      <span className="shrink-0 text-xs font-medium text-gray-500">{repo.name}</span>
                    </div>
                  </Link>
                ))
              ) : (
                <EmptyRow label="No state-backed findings." />
              )}
            </div>
          </Panel>
        </div>

        <aside className="space-y-6">
          <Panel title="Latest Report" action={null}>
            {latestReport ? (
              <div className="space-y-4 p-5">
                <div>
                  <Link
                    to={`/audit/reports/${encodeURIComponent(latestReport.id)}`}
                    className="break-words text-sm font-semibold text-gray-900 hover:text-emerald-700"
                  >
                    {latestReport.title}
                  </Link>
                  <p className="mt-1 text-xs text-gray-500">{latestReport.id}</p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <MiniStat label="Audited" value={latestReport.audited_repos ?? 0} />
                  <MiniStat label="Skipped" value={latestReport.skipped_repos ?? 0} />
                  <MiniStat label="Failed" value={latestReport.failed_repos ?? 0} />
                </div>
              </div>
            ) : (
              <EmptyRow label="No report has been generated." />
            )}
          </Panel>

          <Panel title="Recent Reports" action={null}>
            <div className="divide-y divide-gray-100">
              {recentReports.map((report) => (
                <Link
                  key={report.id}
                  to={`/audit/reports/${encodeURIComponent(report.id)}`}
                  className="block px-5 py-3 hover:bg-gray-50"
                >
                  <p className="break-words text-sm font-medium text-gray-900">{report.id}</p>
                  <p className="mt-1 text-xs text-gray-500">{formatDate(report.modified_at)}</p>
                </Link>
              ))}
              {!recentReports.length && <EmptyRow label="No reports found." />}
            </div>
          </Panel>

          <Panel title="Recent Runs" action={null}>
            <div className="divide-y divide-gray-100">
              {recentRuns.map((run) => (
                <RunRow key={run.id} run={run} />
              ))}
              {!recentRuns.length && <EmptyRow label="No command runs recorded." />}
            </div>
          </Panel>

          {latestRun?.failure_breakpoint && <ErrorPanel message={latestRun.failure_breakpoint} />}
        </aside>
      </section>
    </PageShell>
  );
}

function PageShell({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle: string;
  action: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h1 className="text-2xl font-semibold text-gray-950">{title}</h1>
          <p className="mt-1 break-words font-mono text-xs text-gray-500">{subtitle}</p>
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

function Panel({
  title,
  action,
  children,
}: {
  title: string;
  action: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <div className="flex min-h-12 items-center justify-between gap-3 border-b border-gray-100 px-5">
        <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function Metric({
  label,
  value,
  detail,
  tone,
}: {
  label: string;
  value: number;
  detail: string;
  tone: "neutral" | "green" | "amber" | "rose";
}) {
  const toneClass = {
    neutral: "text-gray-950",
    green: "text-emerald-700",
    amber: "text-amber-700",
    rose: "text-rose-700",
  }[tone];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      <p className="text-xs font-medium uppercase tracking-normal text-gray-500">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${toneClass}`}>{value}</p>
      <p className="mt-1 truncate text-sm text-gray-500">{detail}</p>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-gray-100 bg-gray-50 p-2">
      <p className="text-lg font-semibold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}

function RepoRow({
  repo,
  onAudit,
  disabled,
}: {
  repo: AuditRepoStatus;
  onAudit: () => void;
  disabled: boolean;
}) {
  const stateLabel = repo.status === "error" ? "error" : repo.due ? "due" : "current";
  return (
    <div className="px-5 py-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={stateLabel} />
            <h3 className="text-sm font-semibold text-gray-900">{repo.name}</h3>
            {repo.config_changed && <span className="text-xs text-amber-700">config changed</span>}
          </div>
          <p className="mt-1 break-words font-mono text-xs text-gray-500">{repo.path || repo.configured_path}</p>
          {repo.error && <p className="mt-2 break-words text-sm text-rose-700">{repo.error}</p>}
          <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-600">
            <Pill label={`commits ${repo.commits_since_audit ?? "n/a"}`} />
            <Pill label={`threshold ${repo.commit_threshold}`} />
            <Pill label={`docs ${repo.docs.length}`} />
            <Pill label={`findings ${repo.findings.length}`} />
            {repo.head && <Pill label={`head ${repo.head.slice(0, 12)}`} />}
          </div>
        </div>
        <button
          type="button"
          onClick={onAudit}
          disabled={disabled || repo.status === "error"}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-gray-200 px-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <FileSearch size={16} />
          Audit Repo
        </button>
      </div>
    </div>
  );
}

function RunRow({ run }: { run: AuditRunRecord }) {
  return (
    <div className="px-5 py-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-gray-900">{run.kind.replaceAll("_", " ")}</p>
          <p className="mt-1 break-words font-mono text-xs text-gray-500">{run.id}</p>
        </div>
        {run.success ? (
          <CheckCircle2 className="shrink-0 text-emerald-600" size={18} />
        ) : (
          <XCircle className="shrink-0 text-rose-600" size={18} />
        )}
      </div>
      <p className="mt-2 text-xs text-gray-500">
        {formatDate(run.completed_at)} · {run.duration_ms}ms
      </p>
    </div>
  );
}

function ActionButton({
  icon,
  label,
  onClick,
  disabled,
  primary = false,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled: boolean;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex h-9 items-center justify-center gap-2 rounded-md px-3 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50 ${
        primary
          ? "bg-emerald-700 text-white hover:bg-emerald-800"
          : "border border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function StatusBadge({ status }: { status: "current" | "due" | "error" }) {
  const classes = {
    current: "bg-emerald-50 text-emerald-700 border-emerald-200",
    due: "bg-amber-50 text-amber-700 border-amber-200",
    error: "bg-rose-50 text-rose-700 border-rose-200",
  }[status];
  return <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${classes}`}>{status}</span>;
}

function SeverityBadge({ severity }: { severity: string }) {
  const normalized = severity.toLowerCase();
  const classes = normalized.includes("high")
    ? "bg-rose-50 text-rose-700 border-rose-200"
    : normalized.includes("medium")
      ? "bg-amber-50 text-amber-700 border-amber-200"
      : "bg-gray-50 text-gray-700 border-gray-200";
  return <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${classes}`}>{severity}</span>;
}

function Pill({ label }: { label: string }) {
  return <span className="rounded-md bg-gray-100 px-2 py-1">{label}</span>;
}

function EmptyRow({ label }: { label: string }) {
  return <p className="px-5 py-6 text-sm text-gray-500">{label}</p>;
}

function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="flex gap-3 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
      <AlertTriangle className="mt-0.5 shrink-0" size={18} />
      <p className="break-words">{message}</p>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="space-y-6">
      <div className="h-10 w-72 animate-pulse rounded bg-gray-200" />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[0, 1, 2, 3].map((item) => (
          <div key={item} className="h-32 animate-pulse rounded-lg bg-gray-100" />
        ))}
      </div>
      <div className="h-96 animate-pulse rounded-lg bg-gray-100" />
    </div>
  );
}
