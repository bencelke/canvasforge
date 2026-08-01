import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api/client";
import { DiagnosticsPanel } from "./features/diagnostics/DiagnosticsPanel";
import { Inspector } from "./features/preview/Inspector";
import { PreviewCanvas } from "./features/preview/PreviewCanvas";
import { ScreenTree } from "./features/screen-tree/ScreenTree";
import type {
  Capabilities,
  Diagnostic,
  PackageResult,
  PreviewMode,
  PreviewNode,
  ProjectSummary,
  ScreenDetail,
} from "./types/studio";

function widthFor(
  mode: PreviewMode,
  breakpoints: ProjectSummary["breakpoints"] | null,
): number {
  if (!breakpoints) {
    return mode === "mobile" ? 390 : mode === "tablet" ? 900 : 1440;
  }
  if (mode === "mobile") return Math.min(390, breakpoints.mobile);
  if (mode === "tablet") return Math.min(900, breakpoints.tablet);
  return Math.min(1440, breakpoints.desktop);
}

export default function App() {
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null);
  const [project, setProject] = useState<ProjectSummary | null>(null);
  const [screen, setScreen] = useState<ScreenDetail | null>(null);
  const [selected, setSelected] = useState<PreviewNode | null>(null);
  const [mode, setMode] = useState<PreviewMode>("desktop");
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [packageResult, setPackageResult] = useState<PackageResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState<string>("");

  const loadScreen = useCallback(async (key: string) => {
    const detail = await api.screen(key);
    setScreen(detail);
    setSelected(detail.preview.root);
  }, []);

  const openProject = useCallback(
    async (manifestPath: string) => {
      setError(null);
      setPackageResult(null);
      const summary = await api.openProject(manifestPath, true);
      setProject(summary);
      setDiagnostics(summary.diagnostics);
      await loadScreen(summary.startScreen);
    },
    [loadScreen],
  );

  useEffect(() => {
    void (async () => {
      try {
        const [health, caps] = await Promise.all([api.health(), api.capabilities()]);
        setVersion(health.canvasforgeVersion);
        setCapabilities(caps);
        if (health.currentProject) {
          const summary = await api.currentProject();
          setProject(summary);
          setDiagnostics(summary.diagnostics);
          await loadScreen(summary.startScreen);
        } else if (caps.demoProjects[0]) {
          await openProject(caps.demoProjects[0].manifestPath);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to initialize Studio");
      }
    })();
  }, [loadScreen, openProject]);

  const width = useMemo(
    () => widthFor(mode, project?.breakpoints ?? null),
    [mode, project],
  );

  return (
    <div className="app-shell" data-testid="app-shell">
      <header className="topbar">
        <div className="brand">CanvasForge Studio</div>
        <span className="badge" data-testid="offline-indicator">
          Offline
        </span>
        <span className="badge warn">Local Preview</span>
        {project ? <span className="muted">{project.projectName}</span> : null}
        <div className="topbar-actions">
          <select
            aria-label="Demo projects"
            data-testid="project-select"
            defaultValue=""
            onChange={(event) => {
              const value = event.target.value;
              if (value) {
                void openProject(value).catch((err: unknown) => {
                  setError(err instanceof Error ? err.message : "Open failed");
                });
              }
            }}
          >
            <option value="">Open demo project…</option>
            {(capabilities?.demoProjects ?? []).map((demo) => (
              <option key={demo.manifestPath} value={demo.manifestPath}>
                {demo.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="btn"
            disabled={!project}
            onClick={() => {
              void api
                .validate()
                .then((result) => {
                  setDiagnostics(result.diagnostics);
                  setProject(result.summary);
                })
                .catch((err: unknown) => {
                  setError(err instanceof Error ? err.message : "Validate failed");
                });
            }}
          >
            Validate
          </button>
          <button
            type="button"
            className="btn primary"
            data-testid="build-kit"
            disabled={!project}
            onClick={() => {
              void api
                .package(false)
                .then((result) => {
                  setPackageResult(result);
                })
                .catch((err: unknown) => {
                  setError(err instanceof Error ? err.message : "Package failed");
                });
            }}
          >
            Build Kit
          </button>
          <span className="muted">v{version || "…"}</span>
        </div>
      </header>

      {error ? (
        <div className="error-banner" data-testid="error-banner">
          {error}
        </div>
      ) : null}

      <div className="main-grid">
        <aside className="panel sidebar" data-testid="project-nav">
          <h2>Project</h2>
          {(project?.screens ?? []).map((item) => (
            <button
              key={item.key}
              type="button"
              className={`tree-item ${screen?.key === item.key ? "active" : ""}`}
              onClick={() => {
                void loadScreen(item.key).catch((err: unknown) => {
                  setError(err instanceof Error ? err.message : "Screen load failed");
                });
              }}
            >
              {item.name}
            </button>
          ))}
          <ScreenTree
            root={screen?.preview.root ?? null}
            selectedId={selected?.id ?? null}
            onSelect={setSelected}
          />
          <h2>Data sources</h2>
          <p className="muted">
            {(project?.dataSources.length ?? 0) === 0
              ? "None declared"
              : `${project?.dataSources.length} declared`}
          </p>
          <h2>Permissions</h2>
          <p className="muted">
            {(project?.permissions.length ?? 0) === 0
              ? "None declared"
              : project?.permissions.map((p) => String(p.key)).join(", ")}
          </p>
        </aside>

        <PreviewCanvas
          screen={screen?.preview ?? null}
          mode={mode}
          width={width}
          selectedId={selected?.id ?? null}
          disclaimer={
            screen?.disclaimer ?? "Local Preview — Power Apps Studio validation required"
          }
          onSelect={setSelected}
          onModeChange={setMode}
        />

        <Inspector node={selected} />
      </div>

      <DiagnosticsPanel
        diagnostics={diagnostics}
        packageResult={packageResult}
        onSelectPath={() => {
          /* Phase 4: path jump best-effort via screen already loaded */
        }}
      />
    </div>
  );
}
