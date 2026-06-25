import type { Document } from "../types";
import api from "./client";

export async function listDocuments(dossierId: string): Promise<Document[]> {
  const { data } = await api.get<Document[]>(`/dossiers/${dossierId}/documents`);
  return data;
}

export async function uploadDocument(
  dossierId: string,
  file: File,
  documentType: string,
  opts?: { fecha_emision?: string; fecha_vencimiento?: string },
): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", documentType);
  if (opts?.fecha_emision) formData.append("fecha_emision", opts.fecha_emision);
  if (opts?.fecha_vencimiento) formData.append("fecha_vencimiento", opts.fecha_vencimiento);

  const { data } = await api.post<Document>(`/dossiers/${dossierId}/documents`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getDocument(documentId: string): Promise<Document> {
  const { data } = await api.get<Document>(`/documents/${documentId}`);
  return data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/documents/${documentId}`);
}

export async function getDocumentDownloadUrl(documentId: string): Promise<string> {
  const { data } = await api.get<{ download_url: string }>(`/documents/${documentId}/download`);
  return data.download_url;
}

export interface DocumentChecklist {
  missing: string[];
  total_required: number;
  total_present: number;
}

export async function getDocumentChecklist(dossierId: string): Promise<DocumentChecklist> {
  const { data } = await api.get<DocumentChecklist>(`/dossiers/${dossierId}/documents/checklist`);
  return data;
}
