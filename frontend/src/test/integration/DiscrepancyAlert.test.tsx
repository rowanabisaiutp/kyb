import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DiscrepancyAlert, SeverityBadge } from "../../components/reconciliation/DiscrepancyAlert";

describe("DiscrepancyAlert", () => {
  it("renders nothing when no discrepancies", () => {
    const { container } = render(<DiscrepancyAlert discrepancies={0} hasCritical={false} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders warning for discrepancies", () => {
    render(<DiscrepancyAlert discrepancies={2} hasCritical={false} />);
    expect(screen.getByText(/2 discrepancias encontradas/)).toBeInTheDocument();
  });

  it("renders critical message", () => {
    render(<DiscrepancyAlert discrepancies={1} hasCritical={true} />);
    expect(screen.getByText(/criticas/)).toBeInTheDocument();
  });

  it("handles singular", () => {
    render(<DiscrepancyAlert discrepancies={1} hasCritical={false} />);
    expect(screen.getByText(/1 discrepancia encontrada/)).toBeInTheDocument();
  });
});

describe("SeverityBadge", () => {
  it("shows Coincide when null", () => {
    render(<SeverityBadge severity={null} />);
    expect(screen.getByText("Coincide")).toBeInTheDocument();
  });

  it("shows critical", () => {
    render(<SeverityBadge severity="critical" />);
    expect(screen.getByText("critical")).toBeInTheDocument();
  });

  it("shows warning", () => {
    render(<SeverityBadge severity="warning" />);
    expect(screen.getByText("warning")).toBeInTheDocument();
  });
});
