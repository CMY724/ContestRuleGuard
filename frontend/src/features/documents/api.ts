import type { NormalizedDocument } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || 
equest failed with status );
  }
  return response.json() as Promise<T>;
}

export function uploadDocument(
  projectId: string,
  file: File,
  sourceTier: string,
  stage: string,
): Promise<NormalizedDocument> {
  const form = new FormData();
  form.append("file", file);
  form.append("source_tier", sourceTier);
  form.append("stage", stage);
  return request<NormalizedDocument>(
    /api/projects//documents,
    { method: "POST", body: form },
  );
}

export function listDocuments(projectId: string): Promise<NormalizedDocument[]> {
  return request<NormalizedDocument[]>(/api/projects//documents);
}

export function getDocument(
  projectId: string,
  documentId: string,
): Promise<NormalizedDocument> {
  return request<NormalizedDocument>(
    /api/projects//documents/,
  );
}
