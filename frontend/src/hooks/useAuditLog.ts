import { useQuery } from "@tanstack/react-query";
import { listDossierAuditLog } from "../api/audit";

export function useDossierAuditLog(dossierId: string) {
  return useQuery({
    queryKey: ["audit-log", dossierId],
    queryFn: () => listDossierAuditLog(dossierId),
    enabled: !!dossierId,
  });
}
