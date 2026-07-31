import type { CompilationResult, ContestRule } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || 
equest failed with status );
  }
  return response.json() as Promise<T>;
}

export function listRules(projectId: string): Promise<ContestRule[]> {
  return request<ContestRule[]>(/api/projects//rules);
}

export function updateRuleStatus(
  projectId: string,
  ruleId: string,
  status: string,
): Promise<ContestRule> {
  return request<ContestRule>(
    /api/projects//rules/,
    { method: "PATCH", body: JSON.stringify({ status }) },
  );
}

export function compileRule(
  projectId: string,
  ruleId: string,
  facts?: Record<string, unknown>,
): Promise<CompilationResult> {
  return request<CompilationResult>(
    /api/projects//rules/:compile,
    { method: "POST", body: JSON.stringify(facts || {}) },
  );
}

export function getRuleGraph(projectId: string): Promise<{ nodes: unknown[]; edges: unknown[] }> {
  return request(/api/projects//rule-graph);
}
