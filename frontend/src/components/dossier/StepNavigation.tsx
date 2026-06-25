import { ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "../ui/Button";

interface StepNavigationProps {
  currentStep: number;
  totalSteps: number;
  canProceed: boolean;
  onPrevious: () => void;
  onNext: () => void;
  nextLabel?: string;
  loading?: boolean;
}

export function StepNavigation({
  currentStep,
  totalSteps,
  canProceed,
  onPrevious,
  onNext,
  nextLabel = "Continuar",
  loading,
}: StepNavigationProps) {
  return (
    <div className="flex items-center justify-between pt-6 mt-6 border-t border-border">
      {currentStep > 0 ? (
        <Button variant="ghost" onClick={onPrevious}>
          <ArrowLeft className="w-4 h-4" /> Paso Anterior
        </Button>
      ) : (
        <div />
      )}

      {currentStep < totalSteps - 1 && (
        <Button onClick={onNext} disabled={!canProceed} loading={loading}>
          {nextLabel} <ArrowRight className="w-4 h-4" />
        </Button>
      )}
    </div>
  );
}
