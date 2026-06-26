import { Sparkles, Upload } from "lucide-react";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { classifyDocument } from "../../api/ai";
import type { DocumentType } from "../../types";
import { DOCUMENT_TYPE_LABELS } from "../../utils/statusLabels";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Select } from "../ui/Select";

const AI_CONFIDENCE_THRESHOLD = 50;
const MAX_FILE_SIZE = 10 * 1024 * 1024;

interface DocumentUploadZoneProps {
  onUpload: (file: File, documentType: string, fechaEmision?: string, fechaVencimiento?: string) => void;
  loading?: boolean;
}

const DOCUMENT_TYPE_OPTIONS = Object.entries(DOCUMENT_TYPE_LABELS).map(([value, label]) => ({
  value,
  label,
}));

export function DocumentUploadZone({ onUpload, loading }: DocumentUploadZoneProps) {
  const [selectedType, setSelectedType] = useState<DocumentType>("constancia_situacion_fiscal");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [classifying, setClassifying] = useState(false);
  const [autoDetected, setAutoDetected] = useState(false);
  const [classifyError, setClassifyError] = useState(false);

  const onDrop = useCallback(async (accepted: File[]) => {
    if (accepted.length === 0) return;
    const file = accepted[0];
    setSelectedFile(file);
    setAutoDetected(false);
    setClassifyError(false);

    setClassifying(true);
    try {
      const result = await classifyDocument(file);
      if (result?.document_type && result.confidence > AI_CONFIDENCE_THRESHOLD) {
        setSelectedType(result.document_type as DocumentType);
        setAutoDetected(true);
      }
    } catch {
      setClassifyError(true);
    } finally {
      setClassifying(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false,
  });

  function handleSubmit() {
    if (!selectedFile) return;
    onUpload(selectedFile, selectedType);
    setSelectedFile(null);
    setAutoDetected(false);
  }

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <label className="block text-sm font-medium text-text">Tipo de Documento</label>
          {autoDetected && (
            <Badge className="bg-purple-100 text-purple-700">
              <Sparkles className="w-3 h-3 mr-1 inline" /> Detectado por AI
            </Badge>
          )}
          {classifying && (
            <Badge className="bg-blue-100 text-blue-700 animate-pulse">Detectando tipo con AI...</Badge>
          )}
          {classifyError && (
            <Badge className="bg-yellow-100 text-yellow-700">Selecciona el tipo manualmente</Badge>
          )}
        </div>
        <Select
          id="document_type"
          options={DOCUMENT_TYPE_OPTIONS}
          value={selectedType}
          onChange={(e) => { setSelectedType(e.target.value as DocumentType); setAutoDetected(false); }}
        />
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? "border-primary-light bg-blue-50" : "border-border hover:border-primary-light hover:bg-gray-50"}`}
      >
        <input {...getInputProps()} />
        <Upload className="h-8 w-8 text-text-secondary mx-auto mb-2" />
        {selectedFile ? (
          <p className="text-sm text-text font-medium">{selectedFile.name} ({(selectedFile.size / 1024).toFixed(0)} KB)</p>
        ) : (
          <>
            <p className="text-sm text-text-secondary">Arrastra un archivo o haz clic para seleccionar</p>
            <p className="text-xs text-text-secondary mt-1">PDF, JPEG, PNG — Max 10 MB. El tipo se detecta automaticamente.</p>
          </>
        )}
      </div>

      {selectedFile && (
        <div className="flex justify-end">
          <Button onClick={handleSubmit} loading={loading}>
            Subir Documento
          </Button>
        </div>
      )}
    </div>
  );
}
