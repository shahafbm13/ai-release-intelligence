"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getToken } from "@/lib/api";

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const isLogin = pathname === "/login";

  if (isLogin) return null;

  function logout() {
    clearToken();
    router.push("/login");
  }

  if (!getToken()) return null;

  return (
    <nav className="nav">
      <Link href="/runs" className="nav-brand">
        Release Intelligence
      </Link>
      <div className="nav-links">
        <Link href="/runs">CI Runs</Link>
        <Link href="/metrics">Metrics</Link>
        <Link href="/admin/replay">Demo Replay</Link>
      </div>
      <div className="nav-actions">
        <button type="button" className="btn btn-secondary" onClick={logout}>
          Log out
        </button>
      </div>
    </nav>
  );
}
