import type { RiskClassification } from "../types";

const RISK_CONFIG: Record<RiskClassification, { color: string; bg: string; label: string }> = {
  safe: { color: "text-safe", bg: "bg-safe-bg", label: "Seguro" },
  review_required: { color: "text-warning", bg: "bg-warning-bg", label: "Requiere Revision" },
  high_risk: { color: "text-danger", bg: "bg-danger-bg", label: "Alto Riesgo" },
};

export function getRiskColor(classification: RiskClassification): string {
  return RISK_CONFIG[classification].color;
}

export function getRiskBg(classification: RiskClassification): string {
  return RISK_CONFIG[classification].bg;
}

export function getRiskLabel(classification: RiskClassification): string {
  return RISK_CONFIG[classification].label;
}

export function getScoreColor(score: number): string {
  if (score >= 50) return "text-danger";
  if (score >= 20) return "text-warning";
  return "text-safe";
}
