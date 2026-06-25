import type { ExtractionStatus as ExtractionStatusType } from "../../types";
import { Badge } from "../ui/Badge";

const STATUS_CONFIG: Record<ExtractionStatusType, { label: string; className: string }> = {
  pending: { label: "Pendiente", className: "bg-gray-100 text-gray-600" },
  processing: { label: "Procesando", className: "bg-blue-100 text-blue-700" },
  completed: { label: "Extraido", className: "bg-green-100 text-green-700" },
  failed: { label: "Error", className: "bg-red-100 text-red-700" },
};

interface ExtractionStatusProps {
  status: ExtractionStatusType;
}

export function ExtractionStatus({ status }: ExtractionStatusProps) {
  const config = STATUS_CONFIG[status];
  return <Badge className={config.className}>{config.label}</Badge>;
}
