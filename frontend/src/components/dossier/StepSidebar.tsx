import { Check } from "lucide-react";
import type { RiskClassification } from "../../types";
import { getRiskLabel } from "../../utils/riskColors";
import { STEP_LABELS } from "../../utils/statusLabels";

const RISK_TEXT_COLORS: Record<RiskClassification, string> = {
  safe: "text-safe",
  review_required: "text-warning",
  high_risk: "text-danger",
};

interface StepSidebarProps {
  currentStep: number;
  steps: boolean[];
  onStepClick: (step: number) => void;
  entityName: string;
  entityRfc: string;
  riskScore: number | null;
  riskClassification: RiskClassification | null;
}

export function StepSidebar({
  currentStep,
  steps,
  onStepClick,
  entityName,
  entityRfc,
  riskScore,
  riskClassification,
}: StepSidebarProps) {
  return (
    <div className="w-72 bg-white border-r border-border min-h-full p-6 shrink-0">
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-text truncate">{entityName}</h2>
        <p className="text-xs text-text-secondary font-mono mt-0.5">{entityRfc}</p>
      </div>

      <div className="space-y-1">
        {STEP_LABELS.map((step, i) => {
          const completed = steps[i];
          const active = i === currentStep;
          const clickable = completed || i === currentStep || (i > 0 && steps[i - 1]);

          return (
            <button
              key={i}
              type="button"
              onClick={() => clickable && onStepClick(i)}
              className={`w-full flex items-start gap-3 p-3 rounded-lg text-left transition-colors cursor-pointer
                ${active ? "bg-primary/5" : "hover:bg-gray-50"}
                ${!clickable ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-semibold
                ${completed ? "bg-step-complete text-white" : active ? "bg-step-active text-white" : "bg-step-pending text-white"}`}>
                {completed ? <Check className="w-4 h-4" /> : i + 1}
              </div>
              <div className="min-w-0">
                <p className={`text-sm font-medium ${active ? "text-primary" : "text-text"}`}>
                  {step.label}
                </p>
                <p className="text-xs text-text-secondary mt-0.5">{step.description}</p>
              </div>
            </button>
          );
        })}
      </div>

      {riskScore != null && riskClassification && (
        <div className="mt-8 pt-6 border-t border-border text-center">
          <p className="text-xs text-text-secondary mb-1">Score de Riesgo</p>
          <p className={`text-2xl font-bold ${RISK_TEXT_COLORS[riskClassification]}`}>
            {riskScore}
          </p>
          <p className="text-xs text-text-secondary">{getRiskLabel(riskClassification)}</p>
        </div>
      )}
    </div>
  );
}
