import type { RiskClassification } from "../../types";
import { getRiskBg, getRiskLabel } from "../../utils/riskColors";

interface RiskScoreGaugeProps {
  score: number;
  classification: RiskClassification;
  blocksApproval: boolean;
}

function getGaugeColor(classification: RiskClassification): string {
  const colors: Record<RiskClassification, string> = {
    safe: "#16a34a",
    review_required: "#d97706",
    high_risk: "#dc2626",
  };
  return colors[classification];
}

export function RiskScoreGauge({ score, classification, blocksApproval }: RiskScoreGaugeProps) {
  const color = getGaugeColor(classification);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const cappedScore = Math.min(score, 100);
  const offset = circumference - (cappedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle
            cx="60" cy="60" r={radius} fill="none"
            stroke={color} strokeWidth="10" strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={offset}
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color }}>{score}</span>
          <span className="text-xs text-text-secondary">puntos</span>
        </div>
      </div>

      <div className={`mt-3 px-4 py-1.5 rounded-full text-sm font-semibold ${getRiskBg(classification)}`} style={{ color }}>
        {getRiskLabel(classification)}
      </div>

      {blocksApproval && (
        <p className="mt-2 text-xs text-danger font-medium">Aprobacion bloqueada</p>
      )}
    </div>
  );
}
