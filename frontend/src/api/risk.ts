import type { RiskAssessment } from "../types";
import api from "./client";

export async function calculateRisk(dossierId: string): Promise<RiskAssessment> {
  const { data } = await api.post<RiskAssessment>(`/dossiers/${dossierId}/risk-assessment`);
  return data;
}

export async function listRiskAssessments(dossierId: string): Promise<RiskAssessment[]> {
  const { data } = await api.get<RiskAssessment[]>(`/dossiers/${dossierId}/risk-assessments`);
  return data;
}

export async function getLatestRiskAssessment(dossierId: string): Promise<RiskAssessment | null> {
  const { data } = await api.get<RiskAssessment | null>(`/dossiers/${dossierId}/risk-assessment/latest`);
  return data;
}
