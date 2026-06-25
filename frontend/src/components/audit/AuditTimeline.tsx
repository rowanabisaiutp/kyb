import { Clock } from "lucide-react";
import type { AuditLogEntry } from "../../types";
import { formatDateTime } from "../../utils/formatDate";
import { LoadingSpinner } from "../ui/LoadingSpinner";

const ACTION_LABELS: Record<string, string> = {
  "entity.created": "Entidad creada",
  "entity.updated": "Entidad actualizada",
  "dossier.created": "Expediente creado",
  "dossier.status_changed": "Estado cambiado",
  "dossier.approved": "Expediente aprobado",
  "dossier.rejected": "Expediente rechazado",
  "dossier.auto_needs_update": "Requiere actualizacion (automatico)",
  "document.uploaded": "Documento cargado",
  "document.deleted": "Documento eliminado",
  "extraction.completed": "Extraccion completada",
  "extraction.failed": "Extraccion fallida",
  "fiscal.checked": "Listas fiscales consultadas",
  "reconciliation.run": "Conciliacion ejecutada",
  "risk.calculated": "Score de riesgo calculado",
  "representative.added": "Representante agregado",
  "shareholder.added": "Socio/accionista agregado",
};

interface AuditTimelineProps {
  entries: AuditLogEntry[] | undefined;
  isLoading: boolean;
}

export function AuditTimeline({ entries, isLoading }: AuditTimelineProps) {
  if (isLoading) return <LoadingSpinner className="py-8" />;
  if (!entries?.length) return <p className="text-sm text-text-secondary py-4">Sin registros de auditoria.</p>;

  return (
    <div className="space-y-1">
      {entries.map((entry, i) => (
        <div key={entry.id} className="flex gap-3 py-2">
          <div className="flex flex-col items-center">
            <div className="w-2 h-2 rounded-full bg-primary mt-2 shrink-0" />
            {i < entries.length - 1 && <div className="w-px flex-1 bg-border mt-1" />}
          </div>
          <div className="flex-1 pb-2">
            <p className="text-sm font-medium text-text">
              {ACTION_LABELS[entry.action] ?? entry.action}
            </p>
            {entry.details && Object.keys(entry.details).length > 0 && (
              <div className="text-xs text-text-secondary mt-0.5 space-x-2">
                {Object.entries(entry.details).map(([k, v]) => (
                  <span key={k}>{k}: <span className="font-medium">{String(v)}</span></span>
                ))}
              </div>
            )}
            <div className="flex items-center gap-2 mt-1 text-xs text-text-secondary">
              <Clock className="h-3 w-3" />
              <span>{formatDateTime(entry.created_at)}</span>
              <span className="text-text-secondary">por {entry.actor}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
