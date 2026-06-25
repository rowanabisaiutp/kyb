import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { DossierCreatePage } from "../../pages/DossierCreatePage";

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DossierCreatePage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("DossierCreatePage", () => {
  it("renders form title", () => {
    renderPage();
    expect(screen.getByText("Nuevo Expediente KYB")).toBeInTheDocument();
  });

  it("renders entity fields", () => {
    renderPage();
    expect(screen.getByLabelText("RFC *")).toBeInTheDocument();
    expect(screen.getByLabelText("Razon Social *")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre Comercial")).toBeInTheDocument();
    expect(screen.getByLabelText("Codigo Postal")).toBeInTheDocument();
    expect(screen.getByLabelText("Domicilio Fiscal")).toBeInTheDocument();
  });

  it("renders representative fields", () => {
    renderPage();
    expect(screen.getByText("Representante Legal")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre Completo")).toBeInTheDocument();
    expect(screen.getByLabelText("Cargo")).toBeInTheDocument();
    expect(screen.getByLabelText("CURP")).toBeInTheDocument();
  });

  it("renders action buttons", () => {
    renderPage();
    expect(screen.getByText("Crear Expediente")).toBeInTheDocument();
    expect(screen.getByText("Cancelar")).toBeInTheDocument();
  });

  it("has required fields", () => {
    renderPage();
    const rfcInput = screen.getByLabelText("RFC *");
    expect(rfcInput).toBeRequired();
    const razonInput = screen.getByLabelText("Razon Social *");
    expect(razonInput).toBeRequired();
  });
});
