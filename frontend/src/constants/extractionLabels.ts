import type { ExtractionStatus } from "../types";

export const EXTRACTION_STATUS_CONFIG: Record<
  ExtractionStatus,
  { label: string; className: string; tooltip: string }
> = {
  pending: {
    label: "Pendiente",
    className: "bg-gray-100 text-gray-600",
    tooltip: "La extraccion AI aun no se ha ejecutado",
  },
  processing: {
    label: "Procesando...",
    className: "bg-blue-100 text-blue-700",
    tooltip: "AI esta extrayendo los datos del documento",
  },
  completed: {
    label: "Extraido",
    className: "bg-green-100 text-green-700",
    tooltip: "Los datos fueron extraidos correctamente",
  },
  failed: {
    label: "Extraccion no disponible",
    className: "bg-yellow-100 text-yellow-700",
    tooltip:
      "La extraccion AI no pudo procesar este documento. Puede ser por limite de quota del servicio AI. Los datos del expediente no se ven afectados.",
  },
};
