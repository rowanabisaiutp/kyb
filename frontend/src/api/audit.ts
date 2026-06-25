import type { AuditLogEntry } from "../types";
import api from "./client";

export async function listDossierAuditLog(dossierId: string): Promise<AuditLogEntry[]> {
  const { data } = await api.get<AuditLogEntry[]>(`/dossiers/${dossierId}/audit-log`);
  return data;
}
