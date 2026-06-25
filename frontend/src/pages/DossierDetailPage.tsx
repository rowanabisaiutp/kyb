import { ArrowLeft } from "lucide-react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { StepSidebar } from "../components/dossier/StepSidebar";
import { StepNavigation } from "../components/dossier/StepNavigation";
import { StepDatosEmpresa } from "../components/dossier/steps/StepDatosEmpresa";
import { StepDocumentos } from "../components/dossier/steps/StepDocumentos";
import { StepVerificacionSAT } from "../components/dossier/steps/StepVerificacionSAT";
import { StepConciliacion } from "../components/dossier/steps/StepConciliacion";
import { StepEvaluacionRiesgo } from "../components/dossier/steps/StepEvaluacionRiesgo";
import { StepDecision } from "../components/dossier/steps/StepDecision";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { useDossier } from "../hooks/useDossier";
import { useStepCompletion } from "../hooks/useStepCompletion";

export function DossierDetailPage() {
  const { id = "" } = useParams<{ id: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: dossier, isLoading } = useDossier(id);
  const completion = useStepCompletion(id);

  const stepParam = searchParams.get("step");
  const currentStep = stepParam !== null ? parseInt(stepParam, 10) : completion.activeStep;

  function goToStep(step: number) {
    setSearchParams({ step: String(step) });
  }

  if (isLoading) return <LoadingSpinner className="py-12" />;
  if (!dossier) return <p className="text-text-secondary text-center py-12">Expediente no encontrado.</p>;

  return (
    <div className="flex min-h-[calc(100vh-4rem)] -m-6 lg:-m-8">
      <StepSidebar
        currentStep={currentStep}
        steps={completion.steps}
        onStepClick={goToStep}
        entityName={dossier.entity?.razon_social ?? ""}
        entityRfc={dossier.entity?.rfc ?? ""}
        riskScore={dossier.current_risk_score}
        riskClassification={dossier.current_risk_classification}
      />

      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between px-8 py-4 border-b border-border">
          <div className="flex items-center gap-2 text-sm text-text-secondary">
            <Link to="/dossiers" className="hover:text-primary flex items-center gap-1">
              <ArrowLeft className="w-4 h-4" /> Expedientes
            </Link>
            <span>/</span>
            <span className="text-text font-medium">{dossier.entity?.razon_social}</span>
          </div>
          <span className="text-xs text-text-secondary">
            Paso {currentStep + 1} de {completion.totalSteps}
          </span>
        </div>

        <div className="h-1 bg-gray-100">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${((currentStep + 1) / completion.totalSteps) * 100}%` }}
          />
        </div>

        <div className="flex-1 overflow-y-auto px-8 py-6">
          {currentStep === 0 && <StepDatosEmpresa dossier={dossier} onComplete={() => goToStep(1)} />}
          {currentStep === 1 && <StepDocumentos dossierId={dossier.id} />}
          {currentStep === 2 && <StepVerificacionSAT dossierId={dossier.id} />}
          {currentStep === 3 && <StepConciliacion dossierId={dossier.id} />}
          {currentStep === 4 && <StepEvaluacionRiesgo dossierId={dossier.id} />}
          {currentStep === 5 && <StepDecision dossier={dossier} />}

          {currentStep < 5 && (
            <StepNavigation
              currentStep={currentStep}
              totalSteps={completion.totalSteps}
              canProceed={completion.steps[currentStep]}
              onPrevious={() => goToStep(Math.max(0, currentStep - 1))}
              onNext={() => goToStep(Math.min(5, currentStep + 1))}
            />
          )}
        </div>
      </div>
    </div>
  );
}
