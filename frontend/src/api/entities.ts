import type { Entity, EntityCreatePayload, EntityListItem } from "../types";
import api from "./client";

export async function listEntities(search?: string): Promise<EntityListItem[]> {
  const params = search ? { search } : {};
  const { data } = await api.get<EntityListItem[]>("/entities", { params });
  return data;
}

export async function getEntity(id: string): Promise<Entity> {
  const { data } = await api.get<Entity>(`/entities/${id}`);
  return data;
}

export async function createEntity(payload: EntityCreatePayload): Promise<Entity> {
  const { data } = await api.post<Entity>("/entities", payload);
  return data;
}

export async function updateEntity(id: string, payload: Partial<EntityCreatePayload>): Promise<Entity> {
  const { data } = await api.put<Entity>(`/entities/${id}`, payload);
  return data;
}
