import { useState } from "react";
import type { PreviewMode, PreviewScreen } from "../../types/studio";
import { PreviewNodeView } from "./PreviewNodeView";
import type { PreviewNode } from "../../types/studio";

type Props = {
  screen: PreviewScreen | null;
  mode: PreviewMode;
  width: number;
  selectedId: string | null;
  disclaimer: string;
  onSelect: (node: PreviewNode) => void;
  onModeChange: (mode: PreviewMode) => void;
};

export function PreviewCanvas({
  screen,
  mode,
  width,
  selectedId,
  disclaimer,
  onSelect,
  onModeChange,
}: Props) {
  const [fit, setFit] = useState(false);
  const [customWidth, setCustomWidth] = useState<string>("");
  const parsedCustom = Number.parseInt(customWidth, 10);
  const effectiveWidth =
    Number.isFinite(parsedCustom) && parsedCustom > 0 ? parsedCustom : width;
  const frameWidth = fit ? "100%" : effectiveWidth;

  return (
    <section className="preview-wrap" aria-label="Local preview">
      <p className="disclaimer" data-testid="preview-disclaimer">
        {disclaimer}
      </p>
      <div className="preview-toolbar" role="toolbar" aria-label="Preview mode">
        {(["desktop", "tablet", "mobile"] as PreviewMode[]).map((item) => (
          <button
            key={item}
            type="button"
            className={`btn ${mode === item ? "active" : ""}`}
            onClick={() => onModeChange(item)}
          >
            {item}
          </button>
        ))}
        <button
          type="button"
          className={`btn ${fit ? "active" : ""}`}
          aria-pressed={fit}
          onClick={() => setFit((value) => !value)}
        >
          Fit to panel
        </button>
        <label className="muted">
          Custom{" "}
          <input
            aria-label="Custom preview width"
            type="number"
            min={280}
            max={1920}
            value={customWidth}
            placeholder={String(width)}
            onChange={(event) => setCustomWidth(event.target.value)}
            style={{ width: 72 }}
          />
        </label>
        <span className="muted">
          width {fit ? "fit" : effectiveWidth}px (advisory)
        </span>
      </div>
      <div className="preview-stage">
        {screen ? (
          <div
            className="preview-frame"
            style={{ width: frameWidth, maxWidth: "100%" }}
            data-testid="preview-frame"
          >
            <PreviewNodeView node={screen.root} selectedId={selectedId} onSelect={onSelect} />
          </div>
        ) : (
          <p className="muted">Open a project to preview.</p>
        )}
      </div>
    </section>
  );
}
