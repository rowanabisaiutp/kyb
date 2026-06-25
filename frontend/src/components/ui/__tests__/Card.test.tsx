import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Card, CardTitle } from "../Card";

describe("Card", () => {
  it("renders children", () => {
    render(<Card>Content</Card>);
    expect(screen.getByText("Content")).toBeInTheDocument();
  });

  it("applies padding by default", () => {
    const { container } = render(<Card>Test</Card>);
    expect(container.firstChild).toHaveClass("p-6");
  });

  it("removes padding when false", () => {
    const { container } = render(<Card padding={false}>Test</Card>);
    expect(container.firstChild).not.toHaveClass("p-6");
  });
});

describe("CardTitle", () => {
  it("renders title text", () => {
    render(<CardTitle>My Title</CardTitle>);
    expect(screen.getByText("My Title")).toBeInTheDocument();
  });
});
