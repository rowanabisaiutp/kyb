import axios from "axios";
import { useEffect, useState } from "react";
import { getDossierSummary, type DossierSummary } from "../../../api/ai";
import type { Dossier } from "../../../types";
import { useUpdateDossierStatus } from "../../../hooks/useDossier";
import { useDocumentChecklist } from "../../../hooks/useDocuments";
import { useFiscalChecks } from "../../../hooks/useFiscalCheck";
import { useReconciliation } from "../../../hooks/useReconciliation";
import { useLatestRiskAssessment } from "../../../hooks/useRiskAssessment";
import { useDossierAuditLog } from "../../../hooks/useAuditLog";
import { AuditTimeline } from "../../audit/AuditTimeline";
import { FadeIn } from "../../ui/FadeIn";
import { AISummarySection } from "./AISummarySection";
import { ApprovalActions } from "./ApprovalActions";
import { SummaryCard } from "./SummaryCard";

interface Props {
  dossier: Dossier;
}

export function StepDecision({ dossier }: Props) {
  const updateStatus = useUpdateDossierStatus(dossier.id);
  const { data: checklist } = useDocumentChecklist(dossier.id);
  const { data: fiscalChecks } = useFiscalChecks(dossier.id);
  const { data: reconciliation } = useReconciliation(dossier.id);
  const { data: assessment } = useLatestRiskAssessment(dossier.id);
  const { data: auditEntries, isLoading: auditLoading } = useDossierAuditLog(dossier.id);
  const [error, setError] = useState<string | null>(null);
  const [showAudit, setShowAudit] = useState(false);
  const [summary, setSummary] = useState<DossierSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setSummaryLoading(true);
    setSummaryError(false);
    getDossierSummary(dossier.id)
      .then((s) => { if (!cancelled) setSummary(s); })
      .catch(() => { if (!cancelled) setSummaryError(true); })
      .finally(() => { if (!cancelled) setSummaryLoading(false); });
    return () => { cancelled = true; };
  }, [dossier.id]);

  const fiscalMatches = fiscalChecks?.filter((c) => c.found).length ?? 0;
  const discrepancies = reconciliation?.filter((r) => !r.match).length ?? 0;

  async function handleStatusChange(targetStatus: "in_review" | "approved" | "rejected" | "needs_update", extra?: Record<string, string>) {
    setError(null);
    try {
      const status = dossier.status;
      if (status === "draft" || status === "needs_update") {
        await updateStatus.mutateAsync({ status: "in_review" });
      }
      await updateStatus.mutateAsync({ status: targetStatus, ...extra });
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail ?? `Error al cambiar estado`);
      } else {
        setError("Error de conexion. Intenta de nuevo.");
      }
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Decision Final</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Resumen del expediente y decision de aprobacion.
      </p>

      <AISummarySection summary={summary} loading={summaryLoading} error={summaryError} />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <FadeIn delay={0}><SummaryCard label="Documentos" value={`${checklist?.total_present ?? 0}/${checklist?.total_required ?? 5} cargados`}
          ok={(checklist?.total_present ?? 0) >= (checklist?.total_required ?? 5)} /></FadeIn>
        <FadeIn delay={80}><SummaryCard label="Listas SAT" value={fiscalMatches === 0 ? "RFC limpio" : `${fiscalMatches} hallazgos`}
          ok={fiscalMatches === 0} /></FadeIn>
        <FadeIn delay={160}><SummaryCard label="Conciliacion" value={discrepancies === 0 ? "Sin discrepancias" : `${discrepancies} discrepancias`}
          ok={discrepancies === 0} /></FadeIn>
        <FadeIn delay={240}><SummaryCard label="Riesgo"
          value={assessment ? `${assessment.total_score} pts — ${assessment.classification}` : "Sin calcular"}
          ok={assessment?.classification === "safe"} /></FadeIn>
      </div>

      <ApprovalActions
        dossier={dossier}
        onApprove={() => handleStatusChange("approved", { approved_by: "Compliance Officer" })}
        onReject={() => handleStatusChange("rejected", { notes: "Rechazado tras evaluacion" })}
        isPending={updateStatus.isPending}
        error={error}
      />

      <div className="mt-8">
        <button type="button" onClick={() => setShowAudit(!showAudit)}
          className="text-sm text-primary font-medium cursor-pointer hover:underline">
          {showAudit ? "Ocultar" : "Ver"} registro de auditoria
        </button>
        {showAudit && (
          <div className="mt-4">
            <AuditTimeline entries={auditEntries} isLoading={auditLoading} />
          </div>
        )}
      </div>
    </div>
  );
}
