import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Header } from "../../components/layout/Header";

describe("Header", () => {
  it("renders title", () => {
    render(<Header title="Mi Titulo" />);
    expect(screen.getByText("Mi Titulo")).toBeInTheDocument();
  });

  it("renders description", () => {
    render(<Header title="Titulo" description="Una descripcion" />);
    expect(screen.getByText("Una descripcion")).toBeInTheDocument();
  });

  it("renders action", () => {
    render(<Header title="Titulo" action={<button>Accion</button>} />);
    expect(screen.getByText("Accion")).toBeInTheDocument();
  });

  it("renders without description", () => {
    render(<Header title="Solo titulo" />);
    expect(screen.getByText("Solo titulo")).toBeInTheDocument();
  });
});
