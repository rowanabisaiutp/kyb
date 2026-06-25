import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { NotFoundPage } from "../../pages/NotFoundPage";

function renderPage() {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("NotFoundPage", () => {
  it("renders not found message", () => {
    renderPage();
    expect(screen.getByText("Pagina no encontrada")).toBeInTheDocument();
  });

  it("renders description", () => {
    renderPage();
    expect(screen.getByText("La pagina que buscas no existe.")).toBeInTheDocument();
  });

  it("renders link to dashboard", () => {
    renderPage();
    expect(screen.getByText("Ir al Dashboard")).toBeInTheDocument();
  });
});
