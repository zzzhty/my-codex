import type { AuditFinding } from "../../types/audit";

export function findingKey(finding: AuditFinding, index: number) {
  return finding.fingerprint || `${index}-${finding.title}`;
}

export function findingSeverityText(findings: AuditFinding[]) {
  if (!findings.length) return "none";
  const high = findings.filter((item) => item.severity.toLowerCase().includes("high")).length;
  const medium = findings.filter((item) => item.severity.toLowerCase().includes("medium")).length;
  const low = findings.length - high - medium;
  return `${high} high · ${medium} medium · ${low} low`;
}

export function formatDate(value: string | null | undefined) {
  if (!value) return "not recorded";
  return new Date(value).toLocaleString();
}
