import { AlertTriangle, Shield, ShieldAlert, ShieldCheck } from "lucide-react";
import type { RiskFactor } from "../../types";
import { Badge } from "../ui/Badge";

const CATEGORY_CONFIG: Record<string, { label: string; icon: typeof Shield }> = {
  fiscal: { label: "Fiscal", icon: ShieldAlert },
  documents: { label: "Documentos", icon: Shield },
  reconciliation: { label: "Conciliacion", icon: AlertTriangle },
  completeness: { label: "Completitud", icon: ShieldCheck },
};

interface RiskFactorListProps {
  factors: RiskFactor[];
}

export function RiskFactorList({ factors }: RiskFactorListProps) {
  if (factors.length === 0) {
    return <p className="text-sm text-text-secondary py-4">Sin factores de riesgo identificados.</p>;
  }

  const sorted = [...factors].sort((a, b) => b.points - a.points);

  return (
    <div className="space-y-2">
      {sorted.map((factor, i) => {
        const config = CATEGORY_CONFIG[factor.category] ?? CATEGORY_CONFIG.documents;
        const Icon = config.icon;

        return (
          <div
            key={`${factor.code}-${i}`}
            className={`flex items-start gap-3 p-3 rounded-lg border ${
              factor.blocking ? "border-red-200 bg-red-50" : factor.points > 0 ? "border-border" : "border-border bg-gray-50"
            }`}
          >
            <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${
              factor.blocking ? "text-red-500" : factor.points > 0 ? "text-yellow-500" : "text-green-500"
            }`} />

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-text">{factor.description}</p>
                {factor.blocking && (
                  <Badge className="bg-red-100 text-red-700">Bloqueante</Badge>
                )}
              </div>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-xs text-text-secondary">{config.label}</span>
                <code className="text-xs text-text-secondary">{factor.code}</code>
              </div>
            </div>

            <span className={`text-sm font-bold shrink-0 ${
              factor.points === 0 ? "text-green-600" : factor.points >= 30 ? "text-red-600" : "text-yellow-600"
            }`}>
              +{factor.points}
            </span>
          </div>
        );
      })}
    </div>
  );
}
