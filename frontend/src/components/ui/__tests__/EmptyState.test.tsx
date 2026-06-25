import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyState } from "../EmptyState";

describe("EmptyState", () => {
  it("renders title", () => {
    render(<EmptyState title="No data" />);
    expect(screen.getByText("No data")).toBeInTheDocument();
  });

  it("renders description", () => {
    render(<EmptyState title="Empty" description="Nothing here" />);
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  it("renders action", () => {
    render(<EmptyState title="Empty" action={<button>Add</button>} />);
    expect(screen.getByText("Add")).toBeInTheDocument();
  });
});
