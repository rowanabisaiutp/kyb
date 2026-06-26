import type { Dossier } from "../../../types";
import { Button } from "../../ui/Button";

interface ApprovalActionsProps {
  dossier: Dossier;
  onApprove: () => void;
  onReject: () => void;
  isPending: boolean;
  error: string | null;
}

export function ApprovalActions({ dossier, onApprove, onReject, isPending, error }: ApprovalActionsProps) {
  const isHighRisk = dossier.current_risk_classification === "high_risk";
  const isDecided = dossier.status === "approved" || dossier.status === "rejected";

  if (isDecided) {
    return (
      <div className={`p-4 rounded-lg text-center ${dossier.status === "approved" ? "bg-safe-bg" : "bg-danger-bg"}`}>
        <p className={`text-lg font-semibold ${dossier.status === "approved" ? "text-safe" : "text-danger"}`}>
          {dossier.status === "approved" ? "Expediente Aprobado" : "Expediente Rechazado"}
        </p>
        {dossier.approved_by && <p className="text-sm text-text-secondary mt-1">Por: {dossier.approved_by}</p>}
      </div>
    );
  }

  return (
    <>
      {isHighRisk && (
        <div className="bg-danger-bg border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-danger font-medium">
            Este expediente tiene riesgo alto y no puede ser aprobado.
          </p>
        </div>
      )}

      <div className="flex gap-4">
        <Button onClick={onApprove} disabled={isHighRisk} loading={isPending} size="lg">
          Aprobar Expediente
        </Button>
        <Button variant="danger" onClick={onReject} loading={isPending} size="lg">
          Rechazar Expediente
        </Button>
      </div>

      {error && <p className="text-sm text-danger mt-3">{error}</p>}
    </>
  );
}
