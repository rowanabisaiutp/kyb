import type { Entity, EntityCreatePayload } from "../types";
import api from "./client";

export async function createEntity(payload: EntityCreatePayload): Promise<Entity> {
  const { data } = await api.post<Entity>("/entities", payload);
  return data;
}

export async function updateEntity(id: string, payload: Partial<EntityCreatePayload>): Promise<Entity> {
  const { data } = await api.put<Entity>(`/entities/${id}`, payload);
  return data;
}

export interface RfcCheckResult {
  rfc: string;
  valid: boolean;
  exists: boolean;
  sat_lists_loaded: boolean;
  found_in_sat: boolean;
  lists_matched: { list: string; article: string; description: string }[];
  total_lists_checked: number;
}

export async function checkRfc(rfc: string, excludeEntityId?: string): Promise<RfcCheckResult> {
  const params = excludeEntityId ? { exclude_entity_id: excludeEntityId } : {};
  const { data } = await api.get<RfcCheckResult>(`/entities/check-rfc/${encodeURIComponent(rfc)}`, { params });
  return data;
}
