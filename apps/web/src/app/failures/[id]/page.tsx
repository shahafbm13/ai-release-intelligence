"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch, getToken } from "@/lib/api";

type Failure = {
  id: string;
  ci_run_id: string;
  test_name: string;
  suite_name: string;
  error_type: string;
  error_message: string;
  stack_trace: string;
  log_excerpt: string;
  classification: {
    id: string;
    category: string;
    summary: string;
    likely_cause: string;
    suggested_action: string;
    confidence: number;
    provider: string;
    evidence_refs: string[];
  } | null;
};

type SimilarItem = {
  failure_id: string;
  test_name: string;
  match_method: string;
  score: number;
  matched_at: string;
  classification_summary: string | null;
};

export default function FailureDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [failure, setFailure] = useState<Failure | null>(null);
  const [similar, setSimilar] = useState<SimilarItem[]>([]);
  const [similarMessage, setSimilarMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedbackNote, setFeedbackNote] = useState("");
  const [correctedCategory, setCorrectedCategory] = useState("test_defect");
  const [feedbackStatus, setFeedbackStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    const id = params.id;
    Promise.all([
      apiFetch<Failure>(`/api/v1/failures/${id}`),
      apiFetch<{ items: SimilarItem[]; message: string | null }>(`/api/v1/failures/${id}/similar`),
    ])
      .then(([failureData, similarData]) => {
        setFailure(failureData);
        setSimilar(similarData.items);
        setSimilarMessage(similarData.message);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load failure"));
  }, [params.id, router]);

  async function submitFeedback(action: "accept" | "correct") {
    if (!failure) return;
    setFeedbackStatus(null);
    try {
      await apiFetch(`/api/v1/failures/${failure.id}/feedback`, {
        method: "POST",
        body: JSON.stringify({
          action,
          corrected_category: action === "correct" ? correctedCategory : null,
          note: feedbackNote,
          resolved: false,
        }),
      });
      setFeedbackStatus(`Feedback submitted (${action}).`);
    } catch (err) {
      setFeedbackStatus(err instanceof Error ? err.message : "Feedback failed");
    }
  }

  if (error) return <div className="error">{error}</div>;
  if (!failure) return <p className="muted">Loading failure…</p>;

  return (
    <>
      <p className="muted">
        <Link href={`/runs/${failure.ci_run_id}`}>← Back to run</Link>
      </p>
      <h1>{failure.test_name}</h1>
      <p className="muted">{failure.suite_name}</p>

      <div className="grid-2">
        <div className="card">
          <h2>Failure details (US-004)</h2>
          <p>
            <strong>{failure.error_type}</strong>: {failure.error_message}
          </p>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.85rem" }}>{failure.stack_trace}</pre>
          <p className="muted">{failure.log_excerpt}</p>
        </div>

        <div className="card">
          <h2>Classification</h2>
          {failure.classification ? (
            <>
              <p>
                <strong>{failure.classification.category}</strong> ({failure.classification.provider}) ·
                confidence {(failure.classification.confidence * 100).toFixed(0)}%
              </p>
              <p>{failure.classification.summary}</p>
              <p className="muted">{failure.classification.likely_cause}</p>
              <p>{failure.classification.suggested_action}</p>
            </>
          ) : (
            <p className="muted">Classification pending.</p>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Similar failures (US-006)</h2>
        {similar.length === 0 ? (
          <p className="muted">{similarMessage ?? "No similar failures found."}</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Test</th>
                <th>Method</th>
                <th>Score</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              {similar.map((item) => (
                <tr key={item.failure_id}>
                  <td>
                    <Link href={`/failures/${item.failure_id}`}>{item.test_name}</Link>
                  </td>
                  <td>{item.match_method}</td>
                  <td>{item.score.toFixed(2)}</td>
                  <td>{item.classification_summary}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>Feedback (US-008)</h2>
        <label htmlFor="note">Note</label>
        <textarea
          id="note"
          rows={3}
          value={feedbackNote}
          onChange={(e) => setFeedbackNote(e.target.value)}
        />
        <label htmlFor="category">Corrected category (for corrections)</label>
        <select
          id="category"
          value={correctedCategory}
          onChange={(e) => setCorrectedCategory(e.target.value)}
        >
          <option value="test_defect">test_defect</option>
          <option value="product_defect">product_defect</option>
          <option value="environment_issue">environment_issue</option>
          <option value="infrastructure_issue">infrastructure_issue</option>
          <option value="timeout">timeout</option>
        </select>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button type="button" className="btn" onClick={() => submitFeedback("accept")}>
            Accept classification
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => submitFeedback("correct")}>
            Submit correction
          </button>
        </div>
        {feedbackStatus ? <p className="muted">{feedbackStatus}</p> : null}
      </div>
    </>
  );
}
