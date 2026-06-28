"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getToken } from "@/lib/api";

type CIRun = {
  id: string;
  repository_id: string;
  workflow_name: string;
  branch: string;
  commit_sha: string;
  conclusion: string;
  processing_status: string;
  failure_count: number;
  ingested_at: string;
};

type PaginatedRuns = {
  items: CIRun[];
  total: number;
  page: number;
  page_size: number;
};

export default function RunsPage() {
  const router = useRouter();
  const [runs, setRuns] = useState<CIRun[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("failure");

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    setLoading(true);
    const query = filter ? `?conclusion=${filter}&page_size=50` : "?page_size=50";
    apiFetch<PaginatedRuns>(`/api/v1/ci-runs${query}`)
      .then((data) => setRuns(data.items))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load runs"))
      .finally(() => setLoading(false));
  }, [router, filter]);

  return (
    <>
      <h1>CI Runs</h1>
      <p className="muted">Filter failed runs for triage workflow (US-003).</p>
      <div className="card">
        <label htmlFor="filter">Conclusion</label>
        <select id="filter" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="failure">failure</option>
          <option value="">all</option>
        </select>
      </div>
      {error ? <div className="error">{error}</div> : null}
      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Branch</th>
                <th>Workflow</th>
                <th>Conclusion</th>
                <th>Status</th>
                <th>Failures</th>
                <th>Ingested</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id}>
                  <td>
                    <Link href={`/runs/${run.id}`}>{run.branch}</Link>
                  </td>
                  <td>{run.workflow_name}</td>
                  <td>
                    <span className={`badge badge-${run.conclusion}`}>{run.conclusion}</span>
                  </td>
                  <td>{run.processing_status}</td>
                  <td>{run.failure_count}</td>
                  <td>{new Date(run.ingested_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {runs.length === 0 ? <p className="muted">No runs found. Try Demo Replay as admin.</p> : null}
        </div>
      )}
    </>
  );
}
