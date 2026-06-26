import { CheckCircle, Circle } from "lucide-react";
import { useDocumentChecklist } from "../../hooks/useDocuments";
import { DOCUMENT_TYPE_LABELS, REQUIRED_DOCUMENTS } from "../../utils/statusLabels";
import { LoadingSpinner } from "../ui/LoadingSpinner";

const TOTAL_REQUIRED_DOCS = REQUIRED_DOCUMENTS.length;

interface DocumentChecklistProps {
  dossierId: string;
}

export function DocumentChecklist({ dossierId }: DocumentChecklistProps) {
  const { data: checklist, isLoading } = useDocumentChecklist(dossierId);

  if (isLoading) return <LoadingSpinner size="sm" />;

  const missingSet = new Set(checklist?.missing ?? []);
  const present = checklist?.total_present ?? 0;
  const required = checklist?.total_required ?? TOTAL_REQUIRED_DOCS;
  const progressPercent = required > 0 ? (present / required) * 100 : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-text">Documentos Requeridos</p>
        <span className="text-xs text-text-secondary">{present}/{required}</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-1.5 mb-3">
        <div
          className="bg-primary h-1.5 rounded-full transition-all"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {REQUIRED_DOCUMENTS.map((type) => {
        const present = !missingSet.has(type);
        return (
          <div key={type} className="flex items-center gap-2 text-sm">
            {present ? (
              <CheckCircle className="h-4 w-4 text-safe shrink-0" />
            ) : (
              <Circle className="h-4 w-4 text-text-secondary shrink-0" />
            )}
            <span className={present ? "text-text" : "text-text-secondary"}>
              {DOCUMENT_TYPE_LABELS[type]}
            </span>
          </div>
        );
      })}
    </div>
  );
}
