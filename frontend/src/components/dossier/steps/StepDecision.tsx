import axios from "axios";
import { CheckCircle, FileText, Search, Shield, Sparkles, XCircle } from "lucide-react";
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
import { Button } from "../../ui/Button";

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

  useEffect(() => {
    let cancelled = false;
    setSummaryLoading(true);
    getDossierSummary(dossier.id)
      .then((s) => { if (!cancelled) setSummary(s); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setSummaryLoading(false); });
    return () => { cancelled = true; };
  }, [dossier.id]);

  const isHighRisk = dossier.current_risk_classification === "high_risk";
  const isDecided = dossier.status === "approved" || dossier.status === "rejected";
  const fiscalMatches = fiscalChecks?.filter((c) => c.found).length ?? 0;
  const discrepancies = reconciliation?.filter((r) => !r.match).length ?? 0;

  async function handleApprove() {
    setError(null);
    try {
      await updateStatus.mutateAsync({ status: "in_review" });
      await updateStatus.mutateAsync({ status: "approved", approved_by: "Compliance Officer" });
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail ?? "Error al aprobar");
      }
    }
  }

  async function handleReject() {
    setError(null);
    try {
      await updateStatus.mutateAsync({ status: "in_review" });
      await updateStatus.mutateAsync({ status: "rejected", notes: "Rechazado tras evaluacion" });
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail ?? "Error al rechazar");
      }
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Decision Final</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Resumen del expediente y decision de aprobacion.
      </p>

      {summaryLoading ? (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-purple-700">Generando resumen ejecutivo con AI...</p>
          </div>
        </div>
      ) : summary ? (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-semibold text-purple-700">Resumen Ejecutivo AI</span>
          </div>
          <p className="text-sm text-text">{summary.resumen}</p>
          <p className="text-xs text-purple-600 mt-2 font-medium">
            Recomendacion AI: {summary.recomendacion}
          </p>
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-4 mb-8">
        <SummaryCard icon={FileText} label="Documentos" value={`${checklist?.total_present ?? 0}/${checklist?.total_required ?? 5} cargados`}
          ok={(checklist?.total_present ?? 0) >= (checklist?.total_required ?? 5)} />
        <SummaryCard icon={Search} label="Listas SAT" value={fiscalMatches === 0 ? "RFC limpio" : `${fiscalMatches} hallazgos`}
          ok={fiscalMatches === 0} />
        <SummaryCard icon={Shield} label="Conciliacion" value={discrepancies === 0 ? "Sin discrepancias" : `${discrepancies} discrepancias`}
          ok={discrepancies === 0} />
        <SummaryCard icon={Shield} label="Riesgo"
          value={assessment ? `${assessment.total_score} pts — ${assessment.classification}` : "Sin calcular"}
          ok={assessment?.classification === "safe"} />
      </div>

      {isDecided ? (
        <div className={`p-4 rounded-lg text-center ${dossier.status === "approved" ? "bg-safe-bg" : "bg-danger-bg"}`}>
          <p className={`text-lg font-semibold ${dossier.status === "approved" ? "text-safe" : "text-danger"}`}>
            {dossier.status === "approved" ? "Expediente Aprobado" : "Expediente Rechazado"}
          </p>
          {dossier.approved_by && <p className="text-sm text-text-secondary mt-1">Por: {dossier.approved_by}</p>}
        </div>
      ) : (
        <>
          {isHighRisk && (
            <div className="bg-danger-bg border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-danger font-medium">
                Este expediente tiene riesgo alto y no puede ser aprobado.
              </p>
            </div>
          )}

          <div className="flex gap-4">
            <Button onClick={handleApprove} disabled={isHighRisk} loading={updateStatus.isPending} size="lg">
              Aprobar Expediente
            </Button>
            <Button variant="danger" onClick={handleReject} loading={updateStatus.isPending} size="lg">
              Rechazar Expediente
            </Button>
          </div>

          {error && <p className="text-sm text-danger mt-3">{error}</p>}
        </>
      )}

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

function SummaryCard({ label, value, ok }: { icon: typeof FileText; label: string; value: string; ok: boolean }) {
  return (
    <div className={`p-4 rounded-lg border ${ok ? "border-green-200 bg-green-50" : "border-yellow-200 bg-yellow-50"}`}>
      <div className="flex items-center gap-2 mb-1">
        {ok ? <CheckCircle className="w-4 h-4 text-safe" /> : <XCircle className="w-4 h-4 text-warning" />}
        <span className="text-sm font-medium text-text">{label}</span>
      </div>
      <p className="text-sm text-text-secondary">{value}</p>
    </div>
  );
}
