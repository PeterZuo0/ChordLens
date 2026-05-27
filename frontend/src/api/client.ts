import type { AnalysisSummary, HealthResponse, ProjectListResponse, ProjectSummary } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    let message = `Request failed with ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function getHealth() {
  return request<HealthResponse>("/health");
}

export function listProjects() {
  return request<ProjectListResponse>("/api/projects");
}

export function createAudioProject(title: string) {
  return request<ProjectSummary>("/api/audio/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title })
  });
}

export function getAudioProjectAnalysis(projectId: string) {
  return request<AnalysisSummary>(`/api/audio/projects/${projectId}/analysis`);
}

export function uploadAudioFile(file: File) {
  const body = new FormData();
  body.append("file", file);
  return request<ProjectSummary>("/api/audio/uploads", {
    method: "POST",
    body
  });
}
