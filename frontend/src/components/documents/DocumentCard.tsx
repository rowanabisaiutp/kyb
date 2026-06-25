import { FileText, Trash2 } from "lucide-react";
import type { Document } from "../../types";
import { formatDate } from "../../utils/formatDate";
import { DOCUMENT_TYPE_LABELS } from "../../utils/statusLabels";
import { Badge } from "../ui/Badge";
import { ExtractionStatus } from "./ExtractionStatus";

interface DocumentCardProps {
  document: Document;
  onDelete?: (id: string) => void;
}

export function DocumentCard({ document: doc, onDelete }: DocumentCardProps) {
  const label = DOCUMENT_TYPE_LABELS[doc.document_type as keyof typeof DOCUMENT_TYPE_LABELS] ?? doc.document_type;

  return (
    <div className="flex items-start gap-4 p-4 border border-border rounded-lg hover:bg-gray-50 transition-colors">
      <div className="p-2 bg-blue-50 rounded-lg shrink-0">
        <FileText className="h-5 w-5 text-primary" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-text truncate">{label}</p>
          <ExtractionStatus status={doc.extraction_status} />
        </div>

        <p className="text-xs text-text-secondary mt-0.5 truncate">{doc.file_name}</p>

        <div className="flex items-center gap-3 mt-2 text-xs text-text-secondary">
          {doc.file_size && <span>{(doc.file_size / 1024).toFixed(0)} KB</span>}
          {doc.fecha_emision && <span>Emision: {formatDate(doc.fecha_emision)}</span>}
          {doc.fecha_vencimiento && (
            <Badge className={doc.is_expired ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}>
              {doc.is_expired ? "Vencido" : `Vence: ${formatDate(doc.fecha_vencimiento)}`}
            </Badge>
          )}
        </div>

        {doc.extracted_data && Object.keys(doc.extracted_data).length > 0 && (
          <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
            <p className="font-medium text-text-secondary mb-1">Datos extraidos:</p>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(doc.extracted_data).slice(0, 6).map(([key, value]) => (
                <div key={key}>
                  <span className="text-text-secondary">{key}: </span>
                  <span className="text-text">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {onDelete && (
        <button
          type="button"
          onClick={() => onDelete(doc.id)}
          className="p-1.5 text-text-secondary hover:text-danger hover:bg-red-50 rounded transition-colors cursor-pointer"
          title="Eliminar documento"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
