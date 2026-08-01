import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Inspector } from "./Inspector";

describe("Inspector", () => {
  it("updates when a node is provided", () => {
    render(
      <Inspector
        node={{
          id: "n1",
          name: "lblTitle",
          type: "text",
          sourcePath: "$.screens[0]",
          children: [],
          text: "Hello",
          styles: {},
          layout: {},
          accessibility: {},
          maturity: "candidate",
          expectedControl: "Text",
          diagnostics: [],
        }}
      />,
    );
    expect(screen.getByTestId("inspector")).toHaveTextContent("lblTitle");
    expect(screen.getByTestId("inspector")).toHaveTextContent("candidate");
  });
});
