import type { Diagnostic, PackageResult } from "../../types/studio";

type Props = {
  diagnostics: Diagnostic[];
  packageResult: PackageResult | null;
  onSelectPath?: (path: string) => void;
};

export function DiagnosticsPanel({ diagnostics, packageResult, onSelectPath }: Props) {
  return (
    <footer className="bottom-drawer" data-testid="diagnostics-panel">
      <strong>Validation / Build</strong>
      {packageResult ? (
        <div className="diag info" data-testid="package-result">
          Kit {packageResult.outputName} · buildId={packageResult.buildId} · verified=
          {String(packageResult.verified)} · sha256=
          {packageResult.packageContentChecksum.slice(0, 12)}… · {packageResult.sizeBytes} bytes ·{" "}
          {packageResult.maturity}
        </div>
      ) : null}
      {diagnostics.length === 0 ? (
        <div className="diag info">No diagnostics.</div>
      ) : (
        diagnostics.map((item, index) => (
          <button
            key={`${item.code}-${index}`}
            type="button"
            className={`diag ${item.severity ?? "info"}`}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              border: 0,
              background: "transparent",
              cursor: "pointer",
            }}
            onClick={() => item.path && onSelectPath?.(item.path)}
          >
            [{item.severity ?? "info"}] {item.code} at {item.path ?? "$"}: {item.message}
          </button>
        ))
      )}
    </footer>
  );
}
