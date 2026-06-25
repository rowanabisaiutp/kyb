import type { ExtractionStatus as ExtractionStatusType } from "../../types";
import { Badge } from "../ui/Badge";

const STATUS_CONFIG: Record<
  ExtractionStatusType,
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

interface ExtractionStatusProps {
  status: ExtractionStatusType;
}

export function ExtractionStatus({ status }: ExtractionStatusProps) {
  const config = STATUS_CONFIG[status];
  return (
    <Badge className={config.className} title={config.tooltip}>
      {config.label}
    </Badge>
  );
}
