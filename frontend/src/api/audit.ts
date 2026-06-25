import type { AuditLogEntry } from "../types";
import api from "./client";

export async function listAuditLog(params?: { action?: string }): Promise<AuditLogEntry[]> {
  const { data } = await api.get<AuditLogEntry[]>("/audit-log", { params });
  return data;
}

export async function listDossierAuditLog(dossierId: string): Promise<AuditLogEntry[]> {
  const { data } = await api.get<AuditLogEntry[]>(`/dossiers/${dossierId}/audit-log`);
  return data;
}
