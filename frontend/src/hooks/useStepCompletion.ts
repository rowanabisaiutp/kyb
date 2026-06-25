import { useDossier } from "./useDossier";
import { useDocumentChecklist } from "./useDocuments";
import { useFiscalChecks } from "./useFiscalCheck";
import { useReconciliation } from "./useReconciliation";
import { useLatestRiskAssessment } from "./useRiskAssessment";

export function useStepCompletion(dossierId: string) {
  const { data: dossier } = useDossier(dossierId);
  const { data: checklist } = useDocumentChecklist(dossierId);
  const { data: fiscalChecks } = useFiscalChecks(dossierId);
  const { data: reconciliation } = useReconciliation(dossierId);
  const { data: riskAssessment } = useLatestRiskAssessment(dossierId);

  const entity = dossier?.entity;

  const steps = [
    !!(entity?.rfc && entity?.razon_social),
    checklist ? checklist.total_present >= checklist.total_required : false,
    (fiscalChecks?.length ?? 0) > 0,
    (reconciliation?.length ?? 0) > 0,
    !!riskAssessment,
    dossier?.status === "approved" || dossier?.status === "rejected",
  ];

  const currentStep = steps.findIndex((s) => !s);
  const activeStep = currentStep === -1 ? 5 : currentStep;

  return {
    steps,
    activeStep,
    completedCount: steps.filter(Boolean).length,
    totalSteps: 6,
    isFullyComplete: steps.every(Boolean),
  };
}
