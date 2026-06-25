import { Sparkles } from "lucide-react";
import { DocumentCard } from "../../documents/DocumentCard";
import { DocumentUploadZone } from "../../documents/DocumentUploadZone";
import { DocumentChecklist } from "../DocumentChecklist";
import { LoadingSpinner } from "../../ui/LoadingSpinner";
import {
  useDeleteDocument,
  useDocuments,
  useUploadDocument,
} from "../../../hooks/useDocuments";

interface Props {
  dossierId: string;
}

export function StepDocumentos({ dossierId }: Props) {
  const { data: documents, isLoading } = useDocuments(dossierId);
  const upload = useUploadDocument(dossierId);
  const deleteMutation = useDeleteDocument(dossierId);

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">
        Documentos del Expediente
      </h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Carga los documentos requeridos. La plataforma extraera los datos
        automaticamente con AI.
      </p>

      <div className="mb-6">
        <DocumentChecklist dossierId={dossierId} />
      </div>

      <div className="mb-6">
        <DocumentUploadZone
          onUpload={(file, type, fe, fv) =>
            upload.mutate({
              file,
              documentType: type,
              fechaEmision: fe,
              fechaVencimiento: fv,
            })
          }
          loading={upload.isPending}
        />
      </div>

      {upload.isPending && (
        <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg mb-6 animate-pulse">
          <LoadingSpinner size="sm" />
          <div>
            <p className="text-sm font-medium text-primary">
              Subiendo y procesando documento...
            </p>
            <p className="text-xs text-text-secondary flex items-center gap-1 mt-0.5">
              <Sparkles className="w-3 h-3" /> AI esta extrayendo los datos del
              documento
            </p>
          </div>
        </div>
      )}

      {isLoading ? (
        <LoadingSpinner className="py-4" />
      ) : documents && documents.length > 0 ? (
        <div className="space-y-3">
          {documents.map((doc) => (
            <DocumentCard
              key={doc.id}
              document={doc}
              onDelete={(id) => {
                if (window.confirm("¿Eliminar este documento?")) {
                  deleteMutation.mutate(id);
                }
              }}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
