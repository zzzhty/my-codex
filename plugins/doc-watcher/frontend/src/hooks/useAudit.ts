import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getAuditRepo,
  getAuditReport,
  getAuditRun,
  getAuditStatus,
  listAuditReports,
  listAuditRuns,
  runCommitCounter,
  runGenerateReport,
  runRepoAudit,
} from "../api/audit";
import type { GenerateReportRunRequest } from "../types/audit";

const auditKeys = {
  status: ["audit", "status"] as const,
  reports: ["audit", "reports"] as const,
  runs: ["audit", "runs"] as const,
  repo: (repoName: string) => ["audit", "repos", repoName] as const,
  report: (reportId: string) => ["audit", "reports", reportId] as const,
  run: (runId: string) => ["audit", "runs", runId] as const,
};

export function useAuditStatus() {
  return useQuery({
    queryKey: auditKeys.status,
    queryFn: getAuditStatus,
  });
}

export function useAuditReports() {
  return useQuery({
    queryKey: auditKeys.reports,
    queryFn: listAuditReports,
  });
}

export function useAuditReport(reportId: string | undefined) {
  return useQuery({
    queryKey: auditKeys.report(reportId || ""),
    queryFn: () => getAuditReport(reportId as string),
    enabled: !!reportId,
  });
}

export function useAuditRepo(repoName: string | undefined) {
  return useQuery({
    queryKey: auditKeys.repo(repoName || ""),
    queryFn: () => getAuditRepo(repoName as string),
    enabled: !!repoName,
  });
}

export function useAuditRuns() {
  return useQuery({
    queryKey: auditKeys.runs,
    queryFn: listAuditRuns,
  });
}

export function useAuditRun(runId: string | undefined) {
  return useQuery({
    queryKey: auditKeys.run(runId || ""),
    queryFn: () => getAuditRun(runId as string),
    enabled: !!runId,
  });
}

export function useRunCommitCounter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: runCommitCounter,
    onSuccess: () => invalidateAudit(queryClient),
  });
}

export function useRunGenerateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GenerateReportRunRequest) => runGenerateReport(data),
    onSuccess: () => invalidateAudit(queryClient),
  });
}

export function useRunRepoAudit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (repoName: string) => runRepoAudit(repoName),
    onSuccess: (_result, repoName) => {
      invalidateAudit(queryClient);
      queryClient.invalidateQueries({ queryKey: auditKeys.repo(repoName) });
    },
  });
}

function invalidateAudit(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ["audit"] });
}
