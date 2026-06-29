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

export async function checkRfc(rfc: string, excludeEntityId?: string): Promise<{ rfc: string; valid: boolean; exists: boolean }> {
  const params = excludeEntityId ? { exclude_entity_id: excludeEntityId } : {};
  const { data } = await api.get(`/entities/check-rfc/${encodeURIComponent(rfc)}`, { params });
  return data;
}
