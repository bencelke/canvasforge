import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import App from "./App";
import { api } from "./api/client";
import type { Capabilities, ProjectSummary, ScreenDetail } from "./types/studio";

const summary: ProjectSummary = {
  projectKey: "helloCanvasForge",
  projectName: "Hello CanvasForge",
  projectVersion: "0.1.0",
  manifestVersion: "0.1",
  manifestName: "app.yaml",
  startScreen: "scrDashboard",
  screens: [{ key: "scrDashboard", name: "Dashboard", title: "Dashboard", sectionCount: 3 }],
  dataSources: [],
  permissions: [],
  breakpoints: { mobile: 640, tablet: 1024, desktop: 1440 },
  validationState: "valid",
  diagnostics: [],
  unsupportedSections: [],
  maturity: "Candidate-StudioUnvalidated",
  offline: true,
};

const screenDetail: ScreenDetail = {
  key: "scrDashboard",
  name: "Dashboard",
  title: "Dashboard",
  disclaimer: "Local Preview — Power Apps Studio validation required",
  unsupportedSections: [],
  diagnostics: [],
  controlTree: null,
  preview: {
    key: "scrDashboard",
    name: "Dashboard",
    title: "Dashboard",
    unsupportedSections: [],
    diagnostics: [],
    root: {
      id: "screen/root",
      name: "scrDashboard",
      type: "screen",
      sourcePath: "$.screens[0]",
      children: [
        {
          id: "text/1",
          name: "lblTitle",
          type: "text",
          sourcePath: "$.screens[0].sections[0]",
          children: [],
          text: "Welcome",
          styles: { flexDirection: "column" },
          layout: {},
          accessibility: { label: "Welcome" },
          maturity: "candidate",
          expectedControl: "Text",
          diagnostics: [],
        },
      ],
      text: null,
      styles: { flexDirection: "column", fill: "#fff" },
      layout: {},
      accessibility: { label: "Dashboard" },
      maturity: "candidate",
      expectedControl: "Screen",
      diagnostics: [],
    },
  },
};

const caps: Capabilities = {
  supportedPreviewTypes: ["screen", "text"],
  unsupportedPreviewTypes: [],
  canvasControlMaturity: "documented",
  deploymentTargets: ["code-view"],
  featureFlags: {},
  demoProjects: [{ label: "Hello CanvasForge", manifestPath: "examples/hello-canvasforge/app.yaml" }],
};

vi.mock("./api/client", () => ({
  api: {
    health: vi.fn(async () => ({
      status: "ok",
      canvasforgeVersion: "0.2.0",
      studioApiVersion: "0.1",
      offlineMode: true,
      currentProject: null,
    })),
    capabilities: vi.fn(async () => caps),
    openProject: vi.fn(async () => summary),
    currentProject: vi.fn(async () => summary),
    screen: vi.fn(async () => screenDetail),
    validate: vi.fn(async () => ({ diagnostics: [], summary })),
    package: vi.fn(async () => ({
      buildId: "abc",
      outputName: "Hello.cforge.zip",
      packageContentChecksum: "0".repeat(64),
      sizeBytes: 100,
      maturity: "Candidate-StudioUnvalidated",
      verified: true,
      securityStatus: "pass",
      members: ["canvasforge-project.json"],
      warnings: [],
    })),
    builds: vi.fn(async () => ({ builds: [] })),
  },
}));

describe("CanvasForge Studio shell", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders application shell, offline indicator, and disclaimer", async () => {
    render(<App />);
    expect(await screen.findByTestId("app-shell")).toBeInTheDocument();
    expect(screen.getByTestId("offline-indicator")).toHaveTextContent("Offline");
    expect(await screen.findByTestId("preview-disclaimer")).toHaveTextContent(
      "Local Preview — Power Apps Studio validation required",
    );
    expect(await screen.findByTestId("preview-frame")).toBeInTheDocument();
    expect(screen.getByTestId("project-select")).toBeInTheDocument();
  });

  it("switches preview mode and builds a kit", async () => {
    const user = userEvent.setup();
    render(<App />);
    expect(await screen.findByTestId("preview-frame")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "mobile" }));
    expect(screen.getByText(/width 390px/)).toBeInTheDocument();
    await user.click(screen.getByTestId("build-kit"));
    expect(await screen.findByTestId("package-result")).toHaveTextContent("verified=true");
    expect(api.package).toHaveBeenCalled();
  });

  it("shows API error state", async () => {
    vi.mocked(api.health).mockRejectedValueOnce(new Error("API down"));
    render(<App />);
    expect(await screen.findByTestId("error-banner")).toHaveTextContent("API down");
  });
});