import { AlertTriangle } from "lucide-react";
import { Badge } from "../ui/Badge";

interface DiscrepancyAlertProps {
  discrepancies: number;
  hasCritical: boolean;
}

const SEVERITY_BADGE: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  warning: "bg-yellow-100 text-yellow-700",
  info: "bg-blue-100 text-blue-700",
};

export function DiscrepancyAlert({ discrepancies, hasCritical }: DiscrepancyAlertProps) {
  if (discrepancies === 0) return null;

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg ${hasCritical ? "bg-red-50" : "bg-yellow-50"}`}>
      <AlertTriangle className={`h-5 w-5 ${hasCritical ? "text-red-600" : "text-yellow-600"}`} />
      <p className={`text-sm font-medium ${hasCritical ? "text-red-700" : "text-yellow-700"}`}>
        {discrepancies} discrepancia{discrepancies !== 1 ? "s" : ""} encontrada{discrepancies !== 1 ? "s" : ""}
        {hasCritical && " — incluye discrepancias criticas"}
      </p>
    </div>
  );
}

export function SeverityBadge({ severity }: { severity: string | null }) {
  if (!severity) return <Badge className="bg-green-100 text-green-700">Coincide</Badge>;
  return <Badge className={SEVERITY_BADGE[severity] ?? "bg-gray-100 text-gray-700"}>{severity}</Badge>;
}
