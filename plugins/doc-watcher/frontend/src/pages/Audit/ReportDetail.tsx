import { Copy, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Link, useParams } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { useAuditReport } from "../../hooks/useAudit";
import { formatDate } from "./auditViewUtils";

export default function ReportDetail() {
  const { reportId } = useParams<{ reportId: string }>();
  const decodedId = reportId ? decodeURIComponent(reportId) : undefined;
  const reportQuery = useAuditReport(decodedId);
  const report = reportQuery.data;

  if (reportQuery.isLoading) {
    return <div className="h-80 animate-pulse rounded-lg bg-gray-100" />;
  }

  if (reportQuery.error || !report) {
    return <DetailError message={(reportQuery.error as Error)?.message || "Report not found."} />;
  }

  const prompt = [
    "Use DocWatcher doc-alignment implementation mode.",
    `Report: ${report.path}`,
    `Config: ${report.config_path || "not recorded"}`,
    "Scope: inspect the report findings, update only the affected documentation after explicit review, and run the relevant validation commands.",
    "Do not modify target repositories unless this implementation request is explicitly accepted.",
  ].join("\n");

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <Link to="/audit" className="text-sm font-medium text-emerald-700 hover:text-emerald-800">
            Audit Cockpit
          </Link>
          <h1 className="mt-2 break-words text-2xl font-semibold text-gray-950">{report.title}</h1>
          <p className="mt-1 break-words font-mono text-xs text-gray-500">{report.id}</p>
        </div>
        <button
          type="button"
          onClick={() => navigator.clipboard.writeText(prompt)}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-gray-200 bg-white px-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <Copy size={16} />
          Copy Prompt
        </button>
      </div>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Meta label="Generated" value={report.generated_at || "not recorded"} />
        <Meta label="Modified" value={formatDate(report.modified_at)} />
        <Meta label="Audited" value={String(report.audited_repos ?? 0)} />
        <Meta label="Failed" value={String(report.failed_repos ?? 0)} />
      </section>

      <section className="rounded-lg border border-gray-200 bg-white">
        <div className="flex items-center gap-2 border-b border-gray-100 px-5 py-3">
          <FileText size={18} className="text-gray-500" />
          <h2 className="text-sm font-semibold text-gray-900">Report Markdown</h2>
        </div>
        <div className="prose prose-sm max-w-none overflow-auto p-5">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{report.content}</ReactMarkdown>
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-gray-900">Codex Implementation Prompt</h2>
        <textarea
          readOnly
          value={prompt}
          className="mt-3 min-h-36 w-full resize-y rounded-md border border-gray-200 bg-gray-50 p-3 font-mono text-xs text-gray-700"
        />
      </section>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-xs font-medium uppercase tracking-normal text-gray-500">{label}</p>
      <p className="mt-2 break-words text-sm font-medium text-gray-900">{value}</p>
    </div>
  );
}

function DetailError({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
      {message}
    </div>
  );
}
