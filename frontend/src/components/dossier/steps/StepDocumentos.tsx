import { CheckCircle, Plus, Trash2, Upload, X } from "lucide-react";
import { useRef, useState } from "react";
import {
  useDeleteDocument,
  useDocuments,
  useUploadDocument,
} from "../../../hooks/useDocuments";
import type { Document, DocumentType } from "../../../types";
import { formatDate } from "../../../utils/formatDate";
import { DOCUMENT_TYPE_LABELS, REQUIRED_DOCUMENTS } from "../../../utils/statusLabels";
import { Badge } from "../../ui/Badge";
import { ExtractionStatus } from "../../documents/ExtractionStatus";
import { LoadingSpinner } from "../../ui/LoadingSpinner";

interface Props {
  dossierId: string;
}

const OPTIONAL_TYPES: DocumentType[] = ["poder_representacion", "rfc_documento", "otro"];

export function StepDocumentos({ dossierId }: Props) {
  const { data: documents, isLoading } = useDocuments(dossierId);
  const upload = useUploadDocument(dossierId);
  const deleteMutation = useDeleteDocument(dossierId);

  const docsByType = new Map<string, Document[]>();
  for (const doc of documents ?? []) {
    const list = docsByType.get(doc.document_type) ?? [];
    list.push(doc);
    docsByType.set(doc.document_type, list);
  }

  const presentCount = REQUIRED_DOCUMENTS.filter((t) => docsByType.has(t)).length;
  const progressPercent = (presentCount / REQUIRED_DOCUMENTS.length) * 100;

  const otherDocs = (documents ?? []).filter(
    (d) => !REQUIRED_DOCUMENTS.includes(d.document_type as DocumentType)
  );

  if (isLoading) return <LoadingSpinner className="py-12" />;

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Documentos del Expediente</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Sube cada documento requerido. La AI extraera los datos automaticamente.
      </p>

      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-text">Documentos Requeridos</p>
        <span className="text-xs text-text-secondary">{presentCount}/{REQUIRED_DOCUMENTS.length}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1.5 mb-6">
        <div
          className="bg-primary h-1.5 rounded-full transition-all"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="space-y-3 mb-8">
        {REQUIRED_DOCUMENTS.map((type) => (
          <DocumentSlot
            key={type}
            label={DOCUMENT_TYPE_LABELS[type]}
            documents={docsByType.get(type) ?? []}
            onUpload={(file) => upload.mutate({ file, documentType: type })}
            onDelete={(id) => {
              if (window.confirm("¿Eliminar este documento?")) {
                deleteMutation.mutate(id);
              }
            }}
            uploading={upload.isPending}
          />
        ))}
      </div>

      <div className="border-t border-border pt-6">
        <h3 className="text-sm font-semibold text-text mb-4">Documentos Adicionales</h3>

        {otherDocs.length > 0 && (
          <div className="space-y-3 mb-4">
            {otherDocs.map((doc) => (
              <UploadedDocRow
                key={doc.id}
                doc={doc}
                onDelete={(id) => {
                  if (window.confirm("¿Eliminar este documento?")) {
                    deleteMutation.mutate(id);
                  }
                }}
              />
            ))}
          </div>
        )}

        <AdditionalUploadZone
          optionalTypes={OPTIONAL_TYPES}
          onUpload={(file, type) => upload.mutate({ file, documentType: type })}
          uploading={upload.isPending}
        />
      </div>
    </div>
  );
}

function DocumentSlot({
  label,
  documents,
  onUpload,
  onDelete,
  uploading,
}: {
  label: string;
  documents: Document[];
  onUpload: (file: File) => void;
  onDelete: (id: string) => void;
  uploading: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const hasDoc = documents.length > 0;

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
    if (inputRef.current) inputRef.current.value = "";
  }

  if (hasDoc) {
    return (
      <div className="space-y-2">
        {documents.map((doc) => (
          <UploadedDocRow key={doc.id} doc={doc} onDelete={onDelete} />
        ))}
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-4 p-4 border border-dashed border-border rounded-lg hover:border-primary-light hover:bg-gray-50 transition-colors cursor-pointer"
      onClick={() => inputRef.current?.click()}
    >
      <div className="p-2 bg-gray-100 rounded-lg shrink-0">
        <Upload className="h-5 w-5 text-text-secondary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text">{label}</p>
        <p className="text-xs text-text-secondary mt-0.5">Haz clic o arrastra para subir</p>
      </div>
      <span className="text-xs text-text-secondary bg-gray-100 px-2 py-1 rounded">Pendiente</span>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        className="hidden"
        onChange={handleFileChange}
        disabled={uploading}
      />
    </div>
  );
}

function UploadedDocRow({ doc, onDelete }: { doc: Document; onDelete: (id: string) => void }) {
  const label = DOCUMENT_TYPE_LABELS[doc.document_type as keyof typeof DOCUMENT_TYPE_LABELS] ?? doc.document_type;

  return (
    <div className="flex items-center gap-4 p-4 border border-border rounded-lg bg-white">
      <div className="p-2 bg-green-50 rounded-lg shrink-0">
        <CheckCircle className="h-5 w-5 text-safe" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-text truncate">{label}</p>
          <ExtractionStatus status={doc.extraction_status} />
        </div>
        <div className="flex items-center gap-3 mt-0.5 text-xs text-text-secondary">
          <span className="truncate">{doc.file_name}</span>
          {doc.file_size && <span>{(doc.file_size / 1024).toFixed(0)} KB</span>}
          {doc.fecha_vencimiento && (
            <Badge className={doc.is_expired ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}>
              {doc.is_expired ? "Vencido" : `Vence: ${formatDate(doc.fecha_vencimiento)}`}
            </Badge>
          )}
        </div>
        {doc.extracted_data && Object.keys(doc.extracted_data).length > 0 && (
          <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(doc.extracted_data).slice(0, 4).map(([key, value]) => (
                <div key={key}>
                  <span className="text-text-secondary">{key}: </span>
                  <span className="text-text">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <button
        type="button"
        onClick={() => onDelete(doc.id)}
        className="p-1.5 text-text-secondary hover:text-danger hover:bg-red-50 rounded transition-colors cursor-pointer shrink-0"
        title="Eliminar"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  );
}

function AdditionalUploadZone({
  optionalTypes,
  onUpload,
  uploading,
}: {
  optionalTypes: DocumentType[];
  onUpload: (file: File, type: string) => void;
  uploading: boolean;
}) {
  const [showForm, setShowForm] = useState(false);
  const [selectedType, setSelectedType] = useState<DocumentType>(optionalTypes[0]);
  const inputRef = useRef<HTMLInputElement>(null);

  const allTypes: DocumentType[] = [...optionalTypes];

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file, selectedType);
      setShowForm(false);
    }
    if (inputRef.current) inputRef.current.value = "";
  }

  if (!showForm) {
    return (
      <button
        type="button"
        onClick={() => setShowForm(true)}
        className="flex items-center gap-2 text-sm text-primary hover:text-primary-dark transition-colors cursor-pointer"
      >
        <Plus className="h-4 w-4" />
        Agregar otro documento
      </button>
    );
  }

  return (
    <div className="flex items-center gap-3 p-4 border border-dashed border-border rounded-lg">
      <select
        value={selectedType}
        onChange={(e) => setSelectedType(e.target.value as DocumentType)}
        className="rounded-lg border border-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
      >
        {allTypes.map((type) => (
          <option key={type} value={type}>{DOCUMENT_TYPE_LABELS[type]}</option>
        ))}
      </select>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        className="flex items-center gap-2 px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors cursor-pointer disabled:opacity-50"
      >
        <Upload className="h-4 w-4" />
        Seleccionar archivo
      </button>
      <button
        type="button"
        onClick={() => setShowForm(false)}
        className="p-2 text-text-secondary hover:text-danger rounded transition-colors cursor-pointer"
      >
        <X className="h-4 w-4" />
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        className="hidden"
        onChange={handleFileChange}
        disabled={uploading}
      />
    </div>
  );
}
