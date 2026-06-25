import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtractionStatus } from "../ExtractionStatus";

describe("ExtractionStatus", () => {
  it("shows Pendiente for pending", () => {
    render(<ExtractionStatus status="pending" />);
    expect(screen.getByText("Pendiente")).toBeInTheDocument();
  });

  it("shows Procesando for processing", () => {
    render(<ExtractionStatus status="processing" />);
    expect(screen.getByText("Procesando...")).toBeInTheDocument();
  });

  it("shows Extraido for completed", () => {
    render(<ExtractionStatus status="completed" />);
    expect(screen.getByText("Extraido")).toBeInTheDocument();
  });

  it("shows message for failed", () => {
    render(<ExtractionStatus status="failed" />);
    expect(screen.getByText("Extraccion no disponible")).toBeInTheDocument();
  });
});
