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

  it("renders RFC and Razon Social fields", () => {
    renderPage();
    expect(screen.getByLabelText("RFC de la Persona Moral")).toBeInTheDocument();
    expect(screen.getByLabelText("Razon Social")).toBeInTheDocument();
  });

  it("renders create button", () => {
    renderPage();
    expect(screen.getByText("Crear Expediente")).toBeInTheDocument();
  });

  it("renders back link", () => {
    renderPage();
    expect(screen.getByText("Volver a expedientes")).toBeInTheDocument();
  });

  it("has required fields", () => {
    renderPage();
    const rfcInput = screen.getByLabelText("RFC de la Persona Moral");
    expect(rfcInput).toBeRequired();
    const razonInput = screen.getByLabelText("Razon Social");
    expect(razonInput).toBeRequired();
  });
});
