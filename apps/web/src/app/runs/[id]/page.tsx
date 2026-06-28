"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch, getToken } from "@/lib/api";

type CIRun = {
  id: string;
  branch: string;
  commit_sha: string;
  conclusion: string;
  processing_status: string;
  failure_count: number;
  status_url: string | null;
};

type Failure = {
  id: string;
  test_name: string;
  error_type: string;
  error_message: string;
  classification: { category: string; summary: string } | null;
};

type Assessment = {
  risk_level: string;
  score: number;
  recommendation: string;
  explanation: string;
  factors: { name: string; contribution: number; detail: string }[];
  missing_info: string[];
};

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [run, setRun] = useState<CIRun | null>(null);
  const [failures, setFailures] = useState<Failure[]>([]);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    const id = params.id;
    Promise.all([
      apiFetch<CIRun>(`/api/v1/ci-runs/${id}`),
      apiFetch<{ items: Failure[] }>(`/api/v1/failures?ci_run_id=${id}&page_size=50`),
      apiFetch<Assessment>(`/api/v1/ci-runs/${id}/assessment`).catch(() => null),
    ])
      .then(([runData, failureData, assessmentData]) => {
        setRun(runData);
        setFailures(failureData.items);
        setAssessment(assessmentData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load run"));
  }, [params.id, router]);

  if (error) return <div className="error">{error}</div>;
  if (!run) return <p className="muted">Loading run…</p>;

  return (
    <>
      <p className="muted">
        <Link href="/runs">← CI Runs</Link>
      </p>
      <h1>Run: {run.branch}</h1>
      <p className="muted">
        {run.commit_sha.slice(0, 7)} · {run.conclusion} · {run.processing_status}
      </p>

      {run.processing_status === "pending" ? (
        <div className="card">
          <p className="muted">
            Processing this run — classifications and release assessment will appear shortly.
            If this stays pending, run <code>python -m api.process_pending</code> or start the Celery worker.
          </p>
        </div>
      ) : assessment ? (
        <div className="card">
          <h2>Release risk (US-007)</h2>
          <p>
            <span className={`badge badge-${assessment.risk_level}`}>{assessment.risk_level}</span>{" "}
            Score {assessment.score}/100 · Recommendation: <strong>{assessment.recommendation}</strong>
          </p>
          <p>{assessment.explanation}</p>
          <h3>Factors</h3>
          <ul>
            {assessment.factors.map((factor) => (
              <li key={factor.name}>
                {factor.name}: +{factor.contribution} — {factor.detail}
              </li>
            ))}
          </ul>
          {assessment.missing_info.length > 0 ? (
            <>
              <h3>Missing info</h3>
              <ul>
                {assessment.missing_info.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      ) : (
        <div className="card">
          <p className="muted">Release assessment not available yet.</p>
        </div>
      )}

      <div className="card">
        <h2>Failures ({failures.length})</h2>
        <table>
          <thead>
            <tr>
              <th>Test</th>
              <th>Error</th>
              <th>Classification</th>
            </tr>
          </thead>
          <tbody>
            {failures.map((failure) => (
              <tr key={failure.id}>
                <td>
                  <Link href={`/failures/${failure.id}`}>{failure.test_name}</Link>
                </td>
                <td>{failure.error_type}</td>
                <td>{failure.classification?.category ?? "pending"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
