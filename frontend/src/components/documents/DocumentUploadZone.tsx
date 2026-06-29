import { Sparkles, Upload } from "lucide-react";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { classifyDocument } from "../../api/ai";
import type { DocumentType } from "../../types";

const AI_CONFIDENCE_THRESHOLD = 50;
const MAX_FILE_SIZE = 10 * 1024 * 1024;

interface DocumentUploadZoneProps {
  onUpload: (file: File, documentType: string, fechaEmision?: string, fechaVencimiento?: string) => void;
  loading?: boolean;
}

export function DocumentUploadZone({ onUpload, loading }: DocumentUploadZoneProps) {
  const [classifying, setClassifying] = useState(false);
  const [classifyError, setClassifyError] = useState(false);

  const onDrop = useCallback(async (accepted: File[]) => {
    if (accepted.length === 0) return;
    const file = accepted[0];
    setClassifyError(false);

    let docType: DocumentType = "otro";
    setClassifying(true);
    try {
      const result = await classifyDocument(file);
      if (result?.document_type && result.confidence > AI_CONFIDENCE_THRESHOLD) {
        docType = result.document_type as DocumentType;
      }
    } catch {
      setClassifyError(true);
    } finally {
      setClassifying(false);
    }

    onUpload(file, docType);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    disabled: loading || classifying,
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? "border-primary-light bg-blue-50" : "border-border hover:border-primary-light hover:bg-gray-50"}
          ${(loading || classifying) ? "opacity-50 pointer-events-none" : ""}`}
      >
        <input {...getInputProps()} />
        <Upload className="h-8 w-8 text-text-secondary mx-auto mb-2" />
        {classifying ? (
          <p className="text-sm text-primary font-medium animate-pulse">
            <Sparkles className="w-4 h-4 inline mr-1" />
            Detectando tipo de documento con AI...
          </p>
        ) : (
          <>
            <p className="text-sm text-text-secondary">Arrastra un archivo o haz clic para seleccionar</p>
            <p className="text-xs text-text-secondary mt-1">PDF, JPEG, PNG — Max 10 MB. Se clasifica y sube automaticamente.</p>
          </>
        )}
      </div>
      {classifyError && (
        <p className="text-xs text-yellow-600">No se pudo detectar el tipo — se subio como &quot;Otro&quot;.</p>
      )}
    </div>
  );
}
