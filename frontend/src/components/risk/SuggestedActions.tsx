import { ArrowRight } from "lucide-react";

interface SuggestedActionsProps {
  actions: string[];
}

export function SuggestedActions({ actions }: SuggestedActionsProps) {
  if (actions.length === 0) return null;

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-text">Acciones Sugeridas</h4>
      <ul className="space-y-1.5">
        {actions.map((action, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <ArrowRight className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <span className={action.startsWith("CRITICO") ? "text-danger font-medium" : "text-text"}>
              {action}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
