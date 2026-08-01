import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ScreenTree } from "./ScreenTree";
import type { PreviewNode } from "../../types/studio";

const root: PreviewNode = {
  id: "screen/root",
  name: "scrDashboard",
  type: "screen",
  sourcePath: "$",
  children: [
    {
      id: "text/1",
      name: "lblTitle",
      type: "text",
      sourcePath: "$.screens[0]",
      children: [],
      text: "Hello",
      styles: {},
      layout: {},
      accessibility: { label: "Hello" },
      maturity: "candidate",
      diagnostics: [],
    },
  ],
  styles: {},
  layout: {},
  accessibility: { label: "Dashboard" },
  maturity: "candidate",
  diagnostics: [],
};

describe("ScreenTree", () => {
  it("selects nodes via click and keyboard", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(<ScreenTree root={root} selectedId={null} onSelect={onSelect} />);
    await user.click(screen.getByRole("button", { name: "lblTitle" }));
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: "text/1" }));
    const rootButton = screen.getByRole("button", { name: "scrDashboard" });
    rootButton.focus();
    await user.keyboard("{Enter}");
    expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: "screen/root" }));
  });
});
