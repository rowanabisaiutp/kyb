import { RISK_CATEGORY_CONFIG } from "../../constants";
import type { RiskFactor } from "../../types";
import { Badge } from "../ui/Badge";

function getRowStyle(factor: RiskFactor): string {
  if (factor.blocking) return "border-red-200 bg-red-50";
  if (factor.points > 0) return "border-border";
  return "border-border bg-gray-50";
}

function getIconColor(factor: RiskFactor): string {
  if (factor.blocking) return "text-red-500";
  if (factor.points > 0) return "text-yellow-500";
  return "text-green-500";
}

function getPointsColor(points: number): string {
  if (points === 0) return "text-green-600";
  if (points >= 30) return "text-red-600";
  return "text-yellow-600";
}

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
        const config = RISK_CATEGORY_CONFIG[factor.category] ?? RISK_CATEGORY_CONFIG.documents;
        const Icon = config.icon;

        return (
          <div key={`${factor.code}-${i}`}
            className={`flex items-start gap-3 p-3 rounded-lg border ${getRowStyle(factor)}`}>
            <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${getIconColor(factor)}`} />

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-text">{factor.description}</p>
                {factor.blocking && <Badge className="bg-red-100 text-red-700">Bloqueante</Badge>}
              </div>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-xs text-text-secondary">{config.label}</span>
                <code className="text-xs text-text-secondary">{factor.code}</code>
              </div>
            </div>

            <span className={`text-sm font-bold shrink-0 ${getPointsColor(factor.points)}`}>
              +{factor.points}
            </span>
          </div>
        );
      })}
    </div>
  );
}
