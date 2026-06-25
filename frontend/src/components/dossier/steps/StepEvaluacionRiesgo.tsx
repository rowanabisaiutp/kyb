import { useEffect, useRef } from "react";
import { RiskScoreGauge } from "../../risk/RiskScoreGauge";
import { RiskFactorList } from "../../risk/RiskFactorList";
import { SuggestedActions } from "../../risk/SuggestedActions";
import { useCalculateRisk, useLatestRiskAssessment } from "../../../hooks/useRiskAssessment";
import { LoadingSpinner } from "../../ui/LoadingSpinner";

interface Props {
  dossierId: string;
}

export function StepEvaluacionRiesgo({ dossierId }: Props) {
  const { data: assessment, isLoading } = useLatestRiskAssessment(dossierId);
  const calculate = useCalculateRisk(dossierId);
  const hasRun = useRef(false);

  useEffect(() => {
    if (!isLoading && !hasRun.current && !assessment && !calculate.isPending) {
      hasRun.current = true;
      calculate.mutate();
    }
  }, [isLoading, assessment, calculate]);

  if (isLoading || calculate.isPending) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-text-secondary mt-4">Calculando score de riesgo...</p>
      </div>
    );
  }

  if (!assessment) return null;

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Evaluacion de Riesgo</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Score calculado automaticamente basado en documentos, listas fiscales y conciliacion.
      </p>

      <div className="flex justify-center mb-8">
        <RiskScoreGauge
          score={assessment.total_score}
          classification={assessment.classification}
          blocksApproval={assessment.blocks_approval}
        />
      </div>

      <RiskFactorList factors={assessment.factors} />
      <div className="mt-6">
        <SuggestedActions actions={assessment.suggested_actions} />
      </div>
    </div>
  );
}
