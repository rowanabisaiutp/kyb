import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SuggestedActions } from "../SuggestedActions";

describe("SuggestedActions", () => {
  it("renders actions", () => {
    render(<SuggestedActions actions={["Cargar acta", "Registrar socios"]} />);
    expect(screen.getByText("Cargar acta")).toBeInTheDocument();
    expect(screen.getByText("Registrar socios")).toBeInTheDocument();
  });

  it("renders nothing when empty", () => {
    const { container } = render(<SuggestedActions actions={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("highlights CRITICO actions", () => {
    render(<SuggestedActions actions={["CRITICO: No operar"]} />);
    const el = screen.getByText("CRITICO: No operar");
    expect(el).toHaveClass("text-danger");
  });
});
