import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AISummarySection } from "../AISummarySection";

describe("AISummarySection", () => {
  it("renders nothing when no summary and no error", () => {
    const { container } = render(<AISummarySection summary={null} loading={false} />);
    expect(container.firstChild).toBeNull();
  });

  it("shows loading spinner when loading", () => {
    render(<AISummarySection summary={null} loading={true} />);
    expect(screen.getByText("Generando resumen ejecutivo con AI...")).toBeInTheDocument();
  });

  it("shows error message when error", () => {
    render(<AISummarySection summary={null} loading={false} error={true} />);
    expect(screen.getByText(/No se pudo generar el resumen ejecutivo AI/)).toBeInTheDocument();
  });

  it("shows summary when available", () => {
    const summary = { resumen: "Todo en orden", recomendacion: "aprobar" };
    render(<AISummarySection summary={summary} loading={false} />);
    expect(screen.getByText("Todo en orden")).toBeInTheDocument();
    expect(screen.getByText(/aprobar/)).toBeInTheDocument();
    expect(screen.getByText("Resumen Ejecutivo AI")).toBeInTheDocument();
  });

  it("prioritizes loading over error", () => {
    render(<AISummarySection summary={null} loading={true} error={true} />);
    expect(screen.getByText("Generando resumen ejecutivo con AI...")).toBeInTheDocument();
    expect(screen.queryByText(/No se pudo/)).not.toBeInTheDocument();
  });
});
