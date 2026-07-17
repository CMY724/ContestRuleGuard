import type { Project, ProjectCreate } from "./types";


async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error(`request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function listProjects(): Promise<Project[]> {
  return request<Project[]>("/api/projects");
}

export function createProject(payload: ProjectCreate): Promise<Project> {
  return request<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
