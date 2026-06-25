import { CheckCircle, Circle } from "lucide-react";
import type { DossierStatus } from "../../types";

const TIMELINE_STEPS: { status: DossierStatus; label: string }[] = [
  { status: "draft", label: "Borrador" },
  { status: "in_review", label: "En Revision" },
  { status: "approved", label: "Aprobado" },
];

interface DossierStatusTimelineProps {
  currentStatus: DossierStatus;
}

function getStepState(step: DossierStatus, current: DossierStatus): "done" | "active" | "pending" {
  const order: Record<string, number> = {
    draft: 0, in_review: 1, safe: 2, review_required: 2, high_risk: 2,
    needs_update: 1, approved: 3, rejected: 3,
  };
  const stepOrder = order[step] ?? 0;
  const currentOrder = order[current] ?? 0;

  if (current === "rejected" && step === "approved") return "pending";
  if (stepOrder < currentOrder) return "done";
  if (stepOrder === currentOrder) return "active";
  return "pending";
}

export function DossierStatusTimeline({ currentStatus }: DossierStatusTimelineProps) {
  return (
    <div className="flex items-center gap-2">
      {TIMELINE_STEPS.map((step, i) => {
        const state = getStepState(step.status, currentStatus);
        return (
          <div key={step.status} className="flex items-center gap-2">
            <div className="flex flex-col items-center">
              {state === "done" ? (
                <CheckCircle className="h-5 w-5 text-safe" />
              ) : state === "active" ? (
                <div className="h-5 w-5 rounded-full border-2 border-primary bg-primary/20" />
              ) : (
                <Circle className="h-5 w-5 text-text-secondary" />
              )}
              <span className={`text-xs mt-1 ${state === "active" ? "text-primary font-medium" : "text-text-secondary"}`}>
                {step.label}
              </span>
            </div>
            {i < TIMELINE_STEPS.length - 1 && (
              <div className={`w-12 h-0.5 mb-4 ${state === "done" ? "bg-safe" : "bg-border"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
