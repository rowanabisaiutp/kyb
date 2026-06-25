import type { RiskClassification } from "../types";

const RISK_CONFIG: Record<RiskClassification, { bg: string; label: string }> = {
  safe: { bg: "bg-safe-bg", label: "Seguro" },
  review_required: { bg: "bg-warning-bg", label: "Requiere Revision" },
  high_risk: { bg: "bg-danger-bg", label: "Alto Riesgo" },
};

export function getRiskBg(classification: RiskClassification): string {
  return RISK_CONFIG[classification].bg;
}

export function getRiskLabel(classification: RiskClassification): string {
  return RISK_CONFIG[classification].label;
}
