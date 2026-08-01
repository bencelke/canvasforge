import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PreviewCanvas } from "./PreviewCanvas";
import type { PreviewScreen } from "../../types/studio";

const screenData: PreviewScreen = {
  key: "scr",
  name: "Screen",
  unsupportedSections: [],
  diagnostics: [],
  root: {
    id: "1",
    name: "root",
    type: "screen",
    sourcePath: "$",
    children: [
      {
        id: "u1",
        name: "unsupported:gallery",
        type: "unsupported-placeholder",
        sourcePath: "$",
        children: [],
        text: "Unsupported",
        styles: {},
        layout: {},
        accessibility: { label: "Unsupported" },
        maturity: "unsupported",
        diagnostics: [],
      },
    ],
    styles: { flexDirection: "column" },
    layout: {},
    accessibility: { label: "root" },
    maturity: "candidate",
    diagnostics: [],
  },
};

describe("PreviewCanvas", () => {
  it("switches preview modes and shows unsupported placeholder", async () => {
    const user = userEvent.setup();
    const onMode = vi.fn();
    render(
      <PreviewCanvas
        screen={screenData}
        mode="desktop"
        width={1440}
        selectedId={null}
        disclaimer="Local Preview — Power Apps Studio validation required"
        onSelect={vi.fn()}
        onModeChange={onMode}
      />,
    );
    expect(screen.getByTestId("preview-node-unsupported-placeholder")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "mobile" }));
    expect(onMode).toHaveBeenCalledWith("mobile");
  });
});
