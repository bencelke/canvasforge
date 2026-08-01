import type {
  Capabilities,
  Diagnostic,
  PackageResult,
  ProjectSummary,
  ScreenDetail,
} from "../types/studio";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const data = (await response.json()) as T & {
    error?: string;
    diagnostics?: Diagnostic[];
  };
  if (!response.ok) {
    const message = data.error ?? `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

export const api = {
  health: () =>
    request<{
      status: string;
      canvasforgeVersion: string;
      studioApiVersion: string;
      offlineMode: boolean;
      currentProject: string | null;
    }>("/api/v1/health"),
  capabilities: () => request<Capabilities>("/api/v1/studio/capabilities"),
  openProject: (manifestPath: string, allowPartial = true) =>
    request<ProjectSummary>("/api/v1/projects/open", {
      method: "POST",
      body: JSON.stringify({ manifestPath, allowPartial }),
    }),
  currentProject: () => request<ProjectSummary>("/api/v1/projects/current"),
  screen: (screenKey: string) =>
    request<ScreenDetail>(`/api/v1/projects/current/screens/${encodeURIComponent(screenKey)}`),
  validate: () =>
    request<{ diagnostics: Diagnostic[]; summary: ProjectSummary }>(
      "/api/v1/projects/current/validate",
      { method: "POST", body: "{}" },
    ),
  package: (includeMockData = false) =>
    request<PackageResult>("/api/v1/projects/current/package", {
      method: "POST",
      body: JSON.stringify({ includeMockData, overwrite: true, allowPartial: true }),
    }),
  builds: () => request<{ builds: PackageResult[] }>("/api/v1/projects/current/builds"),
};
