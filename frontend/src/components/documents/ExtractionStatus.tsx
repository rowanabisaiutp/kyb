import { EXTRACTION_STATUS_CONFIG } from "../../constants";
import type { ExtractionStatus as ExtractionStatusType } from "../../types";
import { Badge } from "../ui/Badge";

interface ExtractionStatusProps {
  status: ExtractionStatusType;
}

export function ExtractionStatus({ status }: ExtractionStatusProps) {
  const config = EXTRACTION_STATUS_CONFIG[status];
  return (
    <Badge className={config.className} title={config.tooltip}>
      {config.label}
    </Badge>
  );
}
