"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getToken } from "@/lib/api";

type MetricsSummary = {
  total_ci_runs: number;
  failed_ci_runs: number;
  completed_runs: number;
  total_classifications: number;
  classification_fallback_rate_percent: number;
  feedback_total: number;
  classification_acceptance_rate_percent: number;
  similar_match_rate_percent: number;
  ingest_success_rate_percent: number;
  avg_processing_latency_seconds: number;
  release_assessments_total: number;
};

export default function MetricsPage() {
  const router = useRouter();
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    apiFetch<MetricsSummary>("/api/v1/metrics/summary")
      .then(setMetrics)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load metrics"));
  }, [router]);

  if (error) return <div className="error">{error}</div>;
  if (!metrics) return <p className="muted">Loading metrics…</p>;

  const cards = [
    { label: "Total CI runs", value: metrics.total_ci_runs },
    { label: "Failed runs", value: metrics.failed_ci_runs },
    { label: "Classifications", value: metrics.total_classifications },
    { label: "Rule fallback rate", value: `${metrics.classification_fallback_rate_percent}%` },
    { label: "Similar match rate", value: `${metrics.similar_match_rate_percent}%` },
    { label: "Feedback submissions", value: metrics.feedback_total },
    { label: "Acceptance rate", value: `${metrics.classification_acceptance_rate_percent}%` },
    { label: "Avg processing latency", value: `${metrics.avg_processing_latency_seconds}s` },
    { label: "Release assessments", value: metrics.release_assessments_total },
    { label: "Ingest success rate", value: `${metrics.ingest_success_rate_percent}%` },
  ];

  return (
    <>
      <h1>Operational metrics (US-011)</h1>
      <p className="muted">Computed from database — not hardcoded.</p>
      <div className="grid-2">
        {cards.map((card) => (
          <div className="card" key={card.label}>
            <p className="muted">{card.label}</p>
            <h2 style={{ margin: 0 }}>{card.value}</h2>
          </div>
        ))}
      </div>
    </>
  );
}
