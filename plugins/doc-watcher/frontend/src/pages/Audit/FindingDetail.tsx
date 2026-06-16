import { Copy } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Link, useParams } from "react-router-dom";
import remarkGfm from "remark-gfm";
import { useAuditRepo } from "../../hooks/useAudit";
import { findingKey } from "./auditViewUtils";

export default function FindingDetail() {
  const { repoName, findingId } = useParams<{ repoName: string; findingId: string }>();
  const decodedRepo = repoName ? decodeURIComponent(repoName) : undefined;
  const decodedFinding = findingId ? decodeURIComponent(findingId) : "";
  const repoQuery = useAuditRepo(decodedRepo);
  const repo = repoQuery.data;
  const finding = repo?.findings.find((item, index) => findingKey(item, index) === decodedFinding);

  if (repoQuery.isLoading) {
    return <div className="h-72 animate-pulse rounded-lg bg-gray-100" />;
  }

  if (repoQuery.error || !repo) {
    return <ErrorBox message={(repoQuery.error as Error)?.message || "Repository not found."} />;
  }

  if (!finding) {
    return <ErrorBox message="Finding not found in current repo state." />;
  }

  const prompt = [
    "Use DocWatcher doc-alignment implementation mode.",
    `Repository: ${repo.name}`,
    `Path: ${repo.path || repo.configured_path}`,
    `Finding: [${finding.severity}] ${finding.title}`,
    `Evidence: ${finding.evidence}`,
    "Scope: inspect the current source of truth, make the smallest documentation alignment change after explicit review, and run relevant validation.",
    "Do not create remote review flows or apply automatic patches.",
  ].join("\n");

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <Link to="/audit" className="text-sm font-medium text-emerald-700 hover:text-emerald-800">
            Audit Cockpit
          </Link>
          <h1 className="mt-2 break-words text-2xl font-semibold text-gray-950">{finding.title}</h1>
          <p className="mt-1 break-words font-mono text-xs text-gray-500">{repo.name}</p>
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

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Meta label="Severity" value={finding.severity} />
        <Meta label="Fingerprint" value={finding.fingerprint || "not recorded"} />
        <Meta label="Repo Status" value={repo.status} />
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-gray-900">Evidence</h2>
        <div className="mt-3 max-w-none overflow-auto text-sm text-gray-700">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{finding.evidence}</ReactMarkdown>
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-gray-900">Codex Implementation Prompt</h2>
        <textarea
          readOnly
          value={prompt}
          className="mt-3 min-h-40 w-full resize-y rounded-md border border-gray-200 bg-gray-50 p-3 font-mono text-xs text-gray-700"
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

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
      {message}
    </div>
  );
}
