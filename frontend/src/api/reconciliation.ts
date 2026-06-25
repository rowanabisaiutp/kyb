import type { ReconciliationResult } from "../types";
import api from "./client";

export interface ReconciliationSummary {
  total_comparisons: number;
  matches: number;
  discrepancies: number;
  has_critical: boolean;
  results: ReconciliationResult[];
}

export async function runReconciliation(dossierId: string): Promise<ReconciliationSummary> {
  const { data } = await api.post<ReconciliationSummary>(`/dossiers/${dossierId}/reconciliation`);
  return data;
}

export async function getReconciliation(dossierId: string): Promise<ReconciliationResult[]> {
  const { data } = await api.get<ReconciliationResult[]>(`/dossiers/${dossierId}/reconciliation`);
  return data;
}
