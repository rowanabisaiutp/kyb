import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApprovalActions } from "../ApprovalActions";
import type { Dossier } from "../../../../types";

function makeDossier(overrides: Partial<Dossier> = {}): Dossier {
  return {
    id: "test-id",
    entity_id: "entity-id",
    status: "in_review",
    current_risk_score: 10,
    current_risk_classification: "safe",
    approved_by: null,
    approved_at: null,
    notes: null,
    created_at: "2026-01-01",
    updated_at: "2026-01-01",
    entity: null,
    ...overrides,
  } as Dossier;
}

describe("ApprovalActions", () => {
  const noop = vi.fn();

  it("shows approve and reject buttons for in_review dossier", () => {
    render(<ApprovalActions dossier={makeDossier()} onApprove={noop} onReject={noop} isPending={false} error={null} />);
    expect(screen.getByText("Aprobar Expediente")).toBeInTheDocument();
    expect(screen.getByText("Rechazar Expediente")).toBeInTheDocument();
  });

  it("disables approve button for high_risk", () => {
    render(<ApprovalActions
      dossier={makeDossier({ current_risk_classification: "high_risk" })}
      onApprove={noop} onReject={noop} isPending={false} error={null}
    />);
    expect(screen.getByText("Aprobar Expediente")).toBeDisabled();
    expect(screen.getByText(/riesgo alto/)).toBeInTheDocument();
  });

  it("shows approved state", () => {
    render(<ApprovalActions
      dossier={makeDossier({ status: "approved", approved_by: "Admin" })}
      onApprove={noop} onReject={noop} isPending={false} error={null}
    />);
    expect(screen.getByText("Expediente Aprobado")).toBeInTheDocument();
    expect(screen.getByText("Por: Admin")).toBeInTheDocument();
  });

  it("shows rejected state", () => {
    render(<ApprovalActions
      dossier={makeDossier({ status: "rejected" })}
      onApprove={noop} onReject={noop} isPending={false} error={null}
    />);
    expect(screen.getByText("Expediente Rechazado")).toBeInTheDocument();
  });

  it("shows error message", () => {
    render(<ApprovalActions
      dossier={makeDossier()}
      onApprove={noop} onReject={noop} isPending={false} error="Algo salio mal"
    />);
    expect(screen.getByText("Algo salio mal")).toBeInTheDocument();
  });

  it("shows no error when null", () => {
    render(<ApprovalActions
      dossier={makeDossier()}
      onApprove={noop} onReject={noop} isPending={false} error={null}
    />);
    expect(screen.queryByText("Algo salio mal")).not.toBeInTheDocument();
  });
});
