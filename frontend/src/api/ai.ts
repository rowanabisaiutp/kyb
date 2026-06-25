import api from "./client";

export interface ClassifyResult {
  document_type: string;
  confidence: number;
}

export interface DossierSummary {
  resumen: string;
  recomendacion: "aprobar" | "revisar" | "rechazar";
}

export async function classifyDocument(file: File): Promise<ClassifyResult> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<ClassifyResult>("/documents/classify", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getDossierSummary(dossierId: string): Promise<DossierSummary> {
  const { data } = await api.get<DossierSummary>(`/dossiers/${dossierId}/summary`);
  return data;
}
