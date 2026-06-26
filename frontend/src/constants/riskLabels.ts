import { AlertTriangle, Shield, ShieldAlert, ShieldCheck } from "lucide-react";
import type { RiskClassification } from "../types";

export const RISK_CATEGORY_CONFIG: Record<string, { label: string; icon: typeof Shield }> = {
  fiscal: { label: "Fiscal", icon: ShieldAlert },
  documents: { label: "Documentos", icon: Shield },
  reconciliation: { label: "Conciliacion", icon: AlertTriangle },
  completeness: { label: "Completitud", icon: ShieldCheck },
};

export const RISK_GAUGE_COLORS: Record<RiskClassification, string> = {
  safe: "#16a34a",
  review_required: "#d97706",
  high_risk: "#dc2626",
};
