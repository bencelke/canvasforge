export type Diagnostic = {
  code: string;
  message: string;
  path?: string;
  severity?: "error" | "warning" | "info";
  hint?: string;
};

export type PreviewStyle = {
  fill?: string | null;
  color?: string | null;
  fontSize?: number | null;
  fontWeight?: string | null;
  padding?: string | null;
  gap?: number | null;
  width?: string | null;
  height?: string | null;
  border?: string | null;
  borderRadius?: number | null;
  flexDirection?: "row" | "column" | null;
  alignItems?: string | null;
  justifyContent?: string | null;
};

export type PreviewNode = {
  id: string;
  name: string;
  type: string;
  sourcePath: string;
  children: PreviewNode[];
  text?: string | null;
  styles: PreviewStyle;
  layout: Record<string, unknown>;
  accessibility: Record<string, string>;
  bindingSummary?: string | null;
  maturity: string;
  expectedControl?: string | null;
  diagnostics: Diagnostic[];
};

export type PreviewScreen = {
  key: string;
  name: string;
  title?: string | null;
  root: PreviewNode;
  unsupportedSections: string[];
  diagnostics: Diagnostic[];
};

export type ProjectSummary = {
  projectKey: string;
  projectName: string;
  projectVersion: string;
  manifestVersion: string;
  manifestName: string;
  startScreen: string;
  screens: Array<{ key: string; name: string; title?: string | null; sectionCount: number }>;
  dataSources: Array<Record<string, unknown>>;
  permissions: Array<Record<string, unknown>>;
  breakpoints: { mobile: number; tablet: number; desktop: number };
  validationState: string;
  diagnostics: Diagnostic[];
  unsupportedSections: string[];
  maturity: string;
  offline: boolean;
};

export type ScreenDetail = {
  key: string;
  name: string;
  title?: string | null;
  preview: PreviewScreen;
  controlTree: unknown;
  unsupportedSections: string[];
  diagnostics: Diagnostic[];
  disclaimer: string;
};

export type PackageResult = {
  buildId: string;
  outputName: string;
  packageContentChecksum: string;
  sizeBytes: number;
  maturity: string;
  verified: boolean;
  securityStatus: string;
  members: string[];
  warnings: string[];
};

export type Capabilities = {
  supportedPreviewTypes: string[];
  unsupportedPreviewTypes: string[];
  canvasControlMaturity: string;
  deploymentTargets: string[];
  featureFlags: Record<string, boolean>;
  demoProjects: Array<{ label: string; manifestPath: string }>;
};

export type PreviewMode = "desktop" | "tablet" | "mobile" | "custom";
