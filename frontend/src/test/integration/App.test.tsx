import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AppLayout } from "../../components/layout/AppLayout";
import { DashboardPage } from "../../pages/DashboardPage";
import { DossierCreatePage } from "../../pages/DossierCreatePage";
import { DossierListPage } from "../../pages/DossierListPage";
import { NotFoundPage } from "../../pages/NotFoundPage";

function renderApp(route = "/") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dossiers" element={<DossierListPage />} />
            <Route path="/dossiers/new" element={<DossierCreatePage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("App Routing", () => {
  it("renders dashboard on /", () => {
    renderApp("/");
    expect(screen.getAllByText("Dashboard").length).toBeGreaterThanOrEqual(1);
  });

  it("renders dossier list on /dossiers", () => {
    renderApp("/dossiers");
    expect(screen.getByText("Expedientes KYB")).toBeInTheDocument();
  });

  it("renders create page on /dossiers/new", () => {
    renderApp("/dossiers/new");
    expect(screen.getByText("Nuevo Expediente KYB")).toBeInTheDocument();
  });

  it("renders not found on unknown route", () => {
    renderApp("/unknown-page");
    expect(screen.getByText("Pagina no encontrada")).toBeInTheDocument();
  });
});
