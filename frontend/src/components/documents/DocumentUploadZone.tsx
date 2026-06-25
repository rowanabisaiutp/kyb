import { Upload } from "lucide-react";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import type { DocumentType } from "../../types";
import { DOCUMENT_TYPE_LABELS } from "../../utils/statusLabels";
import { Button } from "../ui/Button";
import { Select } from "../ui/Select";

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

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) setSelectedFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
  });

  function handleSubmit() {
    if (!selectedFile) return;
    onUpload(selectedFile, selectedType);
    setSelectedFile(null);
  }

  return (
    <div className="space-y-4">
      <Select
        label="Tipo de Documento"
        id="document_type"
        options={DOCUMENT_TYPE_OPTIONS}
        value={selectedType}
        onChange={(e) => setSelectedType(e.target.value as DocumentType)}
      />

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
            <p className="text-xs text-text-secondary mt-1">PDF, JPEG, PNG — Max 10 MB</p>
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
