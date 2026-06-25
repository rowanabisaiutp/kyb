import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "../StatusBadge";

describe("StatusBadge", () => {
  it("renders draft label", () => {
    render(<StatusBadge status="draft" />);
    expect(screen.getByText("Borrador")).toBeInTheDocument();
  });

  it("renders approved label", () => {
    render(<StatusBadge status="approved" />);
    expect(screen.getByText("Aprobado")).toBeInTheDocument();
  });

  it("renders high_risk label", () => {
    render(<StatusBadge status="high_risk" />);
    expect(screen.getByText("Alto Riesgo")).toBeInTheDocument();
  });

  it("renders review_required label", () => {
    render(<StatusBadge status="review_required" />);
    expect(screen.getByText("Requiere Revision")).toBeInTheDocument();
  });
});
