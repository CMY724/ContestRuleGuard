import type { ReviewReport } from "./types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(BASE + path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function runReview(
  projectId: string,
  facts?: Record<string, unknown>,
): Promise<ReviewReport> {
  return request<ReviewReport>(
    `/projects/${projectId}/review`,
    { method: "POST", body: JSON.stringify(facts || {}) },
  );
}
