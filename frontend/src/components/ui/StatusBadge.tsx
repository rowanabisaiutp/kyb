import type { DossierStatus } from "../../types";
import { DOSSIER_STATUS_COLORS, DOSSIER_STATUS_LABELS } from "../../utils/statusLabels";
import { Badge } from "./Badge";

interface StatusBadgeProps {
  status: DossierStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <Badge className={DOSSIER_STATUS_COLORS[status]}>
      {DOSSIER_STATUS_LABELS[status]}
    </Badge>
  );
}
