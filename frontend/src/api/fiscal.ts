import type { FiscalListCheck } from "../types";
import api from "./client";

export interface FiscalCheckSummary {
  total_lists_checked: number;
  matches_found: number;
  clean: boolean;
  checks: FiscalListCheck[];
}

export interface FiscalListsStatus {
  loaded: boolean;
  last_loaded: string | null;
  lists_count: number;
  lists: Record<string, { rfcs_count: number; article: string; description: string }>;
}

export async function runFiscalCheck(dossierId: string): Promise<FiscalCheckSummary> {
  const { data } = await api.post<FiscalCheckSummary>(`/dossiers/${dossierId}/fiscal-check`);
  return data;
}

export async function listFiscalChecks(dossierId: string): Promise<FiscalListCheck[]> {
  const { data } = await api.get<FiscalListCheck[]>(`/dossiers/${dossierId}/fiscal-checks`);
  return data;
}

export async function getFiscalListsStatus(): Promise<FiscalListsStatus> {
  const { data } = await api.get<FiscalListsStatus>("/fiscal-lists/status");
  return data;
}
