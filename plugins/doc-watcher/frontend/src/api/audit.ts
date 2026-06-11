import type {
  AuditReportDetail,
  AuditReportListResponse,
  AuditRepoListResponse,
  AuditRepoStatus,
  AuditRunListResponse,
  AuditRunRecord,
  AuditStatusResponse,
  GenerateReportRunRequest,
} from "../types/audit";
import { get, post } from "./client";

export async function getAuditStatus(): Promise<AuditStatusResponse> {
  return get<AuditStatusResponse>("/audit/status");
}

export async function listAuditRepos(): Promise<AuditRepoListResponse> {
  return get<AuditRepoListResponse>("/audit/repos");
}

export async function getAuditRepo(repoName: string): Promise<AuditRepoStatus> {
  return get<AuditRepoStatus>(`/audit/repos/${encodeURIComponent(repoName)}`);
}

export async function listAuditReports(): Promise<AuditReportListResponse> {
  return get<AuditReportListResponse>("/audit/reports");
}

export async function getAuditReport(reportId: string): Promise<AuditReportDetail> {
  return get<AuditReportDetail>(`/audit/reports/${encodeURIComponent(reportId)}`);
}

export async function listAuditRuns(): Promise<AuditRunListResponse> {
  return get<AuditRunListResponse>("/audit/runs");
}

export async function getAuditRun(runId: string): Promise<AuditRunRecord> {
  return get<AuditRunRecord>(`/audit/runs/${encodeURIComponent(runId)}`);
}

export async function runCommitCounter(): Promise<AuditRunRecord> {
  return post<AuditRunRecord>("/audit/runs/commit-counter", {});
}

export async function runGenerateReport(data: GenerateReportRunRequest): Promise<AuditRunRecord> {
  return post<AuditRunRecord>("/audit/runs/generate-report", data);
}

export async function runRepoAudit(repoName: string): Promise<AuditRunRecord> {
  return post<AuditRunRecord>(`/audit/repos/${encodeURIComponent(repoName)}/runs/audit`, {});
}
