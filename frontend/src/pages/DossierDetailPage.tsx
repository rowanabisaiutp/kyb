import axios from "axios";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { AuditTimeline } from "../components/audit/AuditTimeline";
import { DocumentCard } from "../components/documents/DocumentCard";
import { DocumentUploadZone } from "../components/documents/DocumentUploadZone";
import { DocumentChecklist } from "../components/dossier/DocumentChecklist";
import { DossierStatusTimeline } from "../components/dossier/DossierStatusTimeline";
import { FiscalCheckResults } from "../components/fiscal/FiscalCheckResults";
import { Header } from "../components/layout/Header";
import { ReconciliationTable } from "../components/reconciliation/ReconciliationTable";
import { RiskFactorList } from "../components/risk/RiskFactorList";
import { RiskScoreGauge } from "../components/risk/RiskScoreGauge";
import { SuggestedActions } from "../components/risk/SuggestedActions";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useDossier, useUpdateDossierStatus } from "../hooks/useDossier";
import { useDeleteDocument, useDocuments, useUploadDocument } from "../hooks/useDocuments";
import { useFiscalChecks, useRunFiscalCheck } from "../hooks/useFiscalCheck";
import { useReconciliation, useRunReconciliation } from "../hooks/useReconciliation";
import { useCalculateRisk, useLatestRiskAssessment } from "../hooks/useRiskAssessment";
import { useDossierAuditLog } from "../hooks/useAuditLog";
import { formatDate, formatDateTime } from "../utils/formatDate";

type Tab = "overview" | "documents" | "fiscal" | "reconciliation" | "risk" | "audit";

const TABS: { key: Tab; label: string }[] = [
  { key: "overview", label: "General" },
  { key: "documents", label: "Documentos" },
  { key: "fiscal", label: "Listas Fiscales" },
  { key: "reconciliation", label: "Conciliacion" },
  { key: "risk", label: "Riesgo" },
  { key: "audit", label: "Auditoria" },
];

export function DossierDetailPage() {
  const { id = "" } = useParams<{ id: string }>();
  const { data: dossier, isLoading } = useDossier(id);
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  if (isLoading) return <LoadingSpinner className="py-12" />;
  if (!dossier) return <p className="text-text-secondary">Expediente no encontrado.</p>;

  return (
    <>
      <Header
        title={dossier.entity?.razon_social ?? "Expediente"}
        description={`RFC: ${dossier.entity?.rfc ?? "—"}`}
        action={
          <Link to="/dossiers">
            <Button variant="ghost"><ArrowLeft className="h-4 w-4" /> Volver</Button>
          </Link>
        }
      />

      <div className="border-b border-border mb-6">
        <nav className="flex gap-1">
          {TABS.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              onClick={() => setActiveTab(key)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer
                ${activeTab === key
                  ? "border-primary text-primary"
                  : "border-transparent text-text-secondary hover:text-text hover:border-gray-300"}`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">
        <div className="lg:col-span-2 overflow-y-auto max-h-[calc(100vh-220px)] pr-2">
          {activeTab === "overview" && <OverviewTab dossier={dossier} />}
          {activeTab === "documents" && <DocumentsTab dossierId={dossier.id} />}
          {activeTab === "fiscal" && <FiscalTab dossierId={dossier.id} />}
          {activeTab === "reconciliation" && <ReconciliationTab dossierId={dossier.id} />}
          {activeTab === "risk" && <RiskTab dossierId={dossier.id} />}
          {activeTab === "audit" && <AuditTab dossierId={dossier.id} />}
        </div>

        <div className="space-y-6 lg:sticky lg:top-0 lg:self-start">
          <Card>
            <CardTitle>Entidad</CardTitle>
            <div className="space-y-2 mt-4 text-sm">
              <div>
                <p className="text-text-secondary">Razon Social</p>
                <p className="text-text font-medium">{dossier.entity?.razon_social}</p>
              </div>
              <div>
                <p className="text-text-secondary">RFC</p>
                <p className="text-text font-mono">{dossier.entity?.rfc}</p>
              </div>
            </div>
          </Card>

          <Card>
            <DocumentChecklist dossierId={dossier.id} />
          </Card>

          {dossier.notes && (
            <Card>
              <CardTitle>Notas</CardTitle>
              <p className="text-sm text-text mt-2">{dossier.notes}</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
}

function OverviewTab({ dossier }: { dossier: NonNullable<ReturnType<typeof useDossier>["data"]> }) {
  const updateStatus = useUpdateDossierStatus(dossier.id);
  const [approveError, setApproveError] = useState<string | null>(null);

  const canApprove = ["in_review", "safe", "review_required"].includes(dossier.status)
    && dossier.current_risk_classification !== "high_risk";
  const canReject = ["in_review", "review_required", "high_risk"].includes(dossier.status);
  const canStartReview = dossier.status === "draft" || dossier.status === "needs_update";

  async function handleApprove() {
    setApproveError(null);
    try {
      await updateStatus.mutateAsync({ status: "approved", approved_by: "Admin" });
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setApproveError(err.response?.data?.detail ?? "Error al aprobar");
      } else {
        setApproveError(err instanceof Error ? err.message : "Error al aprobar");
      }
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>Progreso del Expediente</CardTitle>
        <div className="mt-4 flex justify-center">
          <DossierStatusTimeline currentStatus={dossier.status} />
        </div>
      </Card>

      <Card>
        <CardTitle>Informacion General</CardTitle>
        <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
          <div>
            <p className="text-text-secondary">Estado</p>
            <div className="mt-1"><StatusBadge status={dossier.status} /></div>
          </div>
          <div>
            <p className="text-text-secondary">Score de Riesgo</p>
            <p className="font-semibold text-text mt-1">
              {dossier.current_risk_score != null ? dossier.current_risk_score : "Sin calcular"}
            </p>
          </div>
          <div>
            <p className="text-text-secondary">Creado</p>
            <p className="text-text mt-1">{formatDateTime(dossier.created_at)}</p>
          </div>
          <div>
            <p className="text-text-secondary">Actualizado</p>
            <p className="text-text mt-1">{formatDateTime(dossier.updated_at)}</p>
          </div>
          {dossier.approved_by && (
            <>
              <div>
                <p className="text-text-secondary">Aprobado por</p>
                <p className="text-text mt-1">{dossier.approved_by}</p>
              </div>
              <div>
                <p className="text-text-secondary">Fecha de Aprobacion</p>
                <p className="text-text mt-1">{dossier.approved_at ? formatDate(dossier.approved_at) : "—"}</p>
              </div>
            </>
          )}
        </div>
      </Card>

      <Card>
        <CardTitle>Acciones</CardTitle>
        <div className="mt-4 flex gap-3 flex-wrap">
          {canStartReview && (
            <Button
              onClick={() => updateStatus.mutate({ status: "in_review" })}
              loading={updateStatus.isPending}
            >
              Iniciar Revision
            </Button>
          )}
          {canApprove && (
            <Button
              onClick={handleApprove}
              loading={updateStatus.isPending}
            >
              Aprobar Expediente
            </Button>
          )}
          {canReject && (
            <Button
              variant="danger"
              onClick={() => updateStatus.mutate({ status: "rejected", notes: "Rechazado por revision" })}
              loading={updateStatus.isPending}
            >
              Rechazar
            </Button>
          )}
          {dossier.status === "approved" && (
            <Button
              variant="secondary"
              onClick={() => updateStatus.mutate({ status: "needs_update" })}
              loading={updateStatus.isPending}
            >
              Marcar para Actualizacion
            </Button>
          )}
        </div>
        {approveError && (
          <p className="mt-3 text-sm text-danger">{approveError}</p>
        )}
        {dossier.current_risk_classification === "high_risk" && (
          <p className="mt-3 text-sm text-danger font-medium">
            Este expediente tiene riesgo alto y no puede ser aprobado.
          </p>
        )}
      </Card>
    </div>
  );
}

function DocumentsTab({ dossierId }: { dossierId: string }) {
  const { data: documents, isLoading } = useDocuments(dossierId);
  const upload = useUploadDocument(dossierId);
  const deleteMutation = useDeleteDocument(dossierId);

  function handleUpload(file: File, documentType: string, fechaEmision?: string, fechaVencimiento?: string) {
    upload.mutate({ file, documentType, fechaEmision, fechaVencimiento });
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>Subir Documento</CardTitle>
        <div className="mt-4">
          <DocumentUploadZone onUpload={handleUpload} loading={upload.isPending} />
        </div>
        {upload.isError && (
          <p className="text-sm text-danger mt-2">Error al subir el documento. Intenta de nuevo.</p>
        )}
      </Card>

      <Card>
        <CardTitle>Documentos del Expediente</CardTitle>
        {isLoading ? (
          <LoadingSpinner className="py-8" />
        ) : !documents?.length ? (
          <p className="text-sm text-text-secondary mt-4">No hay documentos cargados aun.</p>
        ) : (
          <div className="space-y-3 mt-4">
            {documents.map((doc) => (
              <DocumentCard
                key={doc.id}
                document={doc}
                onDelete={(id) => {
                  if (window.confirm("¿Eliminar este documento? Esta accion no se puede deshacer.")) {
                    deleteMutation.mutate(id);
                  }
                }}
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function RiskTab({ dossierId }: { dossierId: string }) {
  const { data: assessment, isLoading } = useLatestRiskAssessment(dossierId);
  const calculate = useCalculateRisk(dossierId);

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex items-center justify-between">
          <CardTitle>Score de Riesgo</CardTitle>
          <Button onClick={() => calculate.mutate()} loading={calculate.isPending} variant="secondary" size="sm">
            {assessment ? "Recalcular" : "Calcular Score"}
          </Button>
        </div>

        {isLoading ? (
          <LoadingSpinner className="py-8" />
        ) : !assessment ? (
          <p className="text-sm text-text-secondary mt-4">
            Calcula el score de riesgo para obtener la evaluacion del expediente.
          </p>
        ) : (
          <div className="mt-6 space-y-6">
            <div className="flex justify-center">
              <RiskScoreGauge
                score={assessment.total_score}
                classification={assessment.classification}
                blocksApproval={assessment.blocks_approval}
              />
            </div>
            <RiskFactorList factors={assessment.factors} />
            <SuggestedActions actions={assessment.suggested_actions} />
          </div>
        )}
      </Card>
    </div>
  );
}

function ReconciliationTab({ dossierId }: { dossierId: string }) {
  const { data: results, isLoading } = useReconciliation(dossierId);
  const run = useRunReconciliation(dossierId);

  return (
    <ReconciliationTable
      results={results}
      isLoading={isLoading}
      onRun={() => run.mutate()}
      isRunning={run.isPending}
    />
  );
}

function FiscalTab({ dossierId }: { dossierId: string }) {
  const { data: checks, isLoading } = useFiscalChecks(dossierId);
  const runCheck = useRunFiscalCheck(dossierId);

  return (
    <FiscalCheckResults
      checks={checks}
      isLoading={isLoading}
      onRunCheck={() => runCheck.mutate()}
      isRunning={runCheck.isPending}
    />
  );
}

function AuditTab({ dossierId }: { dossierId: string }) {
  const { data: entries, isLoading } = useDossierAuditLog(dossierId);

  return (
    <Card>
      <CardTitle>Registro de Auditoria</CardTitle>
      <div className="mt-4">
        <AuditTimeline entries={entries} isLoading={isLoading} />
      </div>
    </Card>
  );
}
