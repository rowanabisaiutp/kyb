import type { Dossier, DossierCreatePayload, DossierStatusUpdatePayload } from "../types";
import api from "./client";

export async function listDossiers(params?: {
  status?: string;
  search?: string;
}): Promise<Dossier[]> {
  const { data } = await api.get<Dossier[]>("/dossiers", { params });
  return data;
}

export async function getDossier(id: string): Promise<Dossier> {
  const { data } = await api.get<Dossier>(`/dossiers/${id}`);
  return data;
}

export async function createDossier(payload: DossierCreatePayload): Promise<Dossier> {
  const { data } = await api.post<Dossier>("/dossiers", payload);
  return data;
}

export async function updateDossierStatus(
  id: string,
  payload: DossierStatusUpdatePayload,
): Promise<Dossier> {
  const { data } = await api.patch<Dossier>(`/dossiers/${id}/status`, payload);
  return data;
}

export async function deleteDossier(id: string): Promise<void> {
  await api.delete(`/dossiers/${id}`);
}

export async function getDossierStats(): Promise<Record<string, number>> {
  const { data } = await api.get<Record<string, number>>("/dossiers/stats");
  return data;
}
