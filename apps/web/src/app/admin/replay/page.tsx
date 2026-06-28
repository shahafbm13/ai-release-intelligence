"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, getToken } from "@/lib/api";

const FIXTURES = [
  "failed_run.json",
  "timeout_run.json",
  "auth_failure.json",
  "infra_outage.json",
  "flaky_retry.json",
  "network_failure.json",
];

export default function AdminReplayPage() {
  const router = useRouter();
  const [fixture, setFixture] = useState(FIXTURES[0]);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (typeof window !== "undefined" && !getToken()) {
    router.push("/login");
  }

  async function replay() {
    setError(null);
    setStatus(null);
    try {
      const data = await apiFetch<{ ci_run_id: string; status: string }>(
        `/api/v1/admin/seed/replay?fixture_name=${encodeURIComponent(fixture)}`,
        { method: "POST" }
      );
      setStatus(`Replay ${data.status}. CI run ${data.ci_run_id}. Worker will process if running.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Replay failed (admin role required)");
    }
  }

  return (
    <>
      <h1>Demo replay (US-010)</h1>
      <p className="muted">Admin only. Replays contract fixtures through the ingest pipeline.</p>
      <div className="card">
        <label htmlFor="fixture">Fixture</label>
        <select id="fixture" value={fixture} onChange={(e) => setFixture(e.target.value)}>
          {FIXTURES.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
        <button type="button" className="btn" onClick={replay}>
          Replay fixture
        </button>
        {error ? <div className="error">{error}</div> : null}
        {status ? <p className="muted">{status}</p> : null}
        <p className="muted">Use admin@demo.example.com / demo-pass-3 for admin access.</p>
      </div>
    </>
  );
}
