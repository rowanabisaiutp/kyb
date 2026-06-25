import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { Sidebar } from "../../components/layout/Sidebar";

function renderSidebar(route = "/") {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Sidebar />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Sidebar", () => {
  it("renders logo", () => {
    renderSidebar();
    expect(screen.getByText("KYB Platform")).toBeInTheDocument();
  });

  it("renders navigation items", () => {
    renderSidebar();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Expedientes")).toBeInTheDocument();
  });

  it("highlights active route for dashboard", () => {
    renderSidebar("/");
    const dashboardLink = screen.getByText("Dashboard").closest("a");
    expect(dashboardLink?.className).toContain("text-primary");
  });

  it("highlights active route for dossiers", () => {
    renderSidebar("/dossiers");
    const dossiersLink = screen.getByText("Expedientes").closest("a");
    expect(dossiersLink?.className).toContain("text-primary");
  });
});
