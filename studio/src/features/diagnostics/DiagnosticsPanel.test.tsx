import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DiagnosticsPanel } from "./DiagnosticsPanel";

describe("DiagnosticsPanel", () => {
  it("lists diagnostics and package success state", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <DiagnosticsPanel
        diagnostics={[
          {
            code: "CF001",
            message: "Sample warning",
            severity: "warning",
            path: "$.screens[0]",
          },
        ]}
        packageResult={{
          buildId: "build1",
          outputName: "Hello.cforge.zip",
          packageContentChecksum: "abcdef0123456789",
          sizeBytes: 1200,
          maturity: "Candidate-StudioUnvalidated",
          verified: true,
          securityStatus: "pass",
          members: ["canvasforge-project.json"],
          warnings: [],
        }}
        onSelectPath={onSelect}
      />,
    );
    expect(screen.getByTestId("package-result")).toHaveTextContent("verified=true");
    expect(screen.getByTestId("diagnostics-panel")).toHaveTextContent("CF001");
    await user.click(screen.getByRole("button", { name: /CF001/ }));
    expect(onSelect).toHaveBeenCalledWith("$.screens[0]");
  });
});
