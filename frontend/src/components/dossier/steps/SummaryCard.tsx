import { CheckCircle, XCircle } from "lucide-react";

interface SummaryCardProps {
  label: string;
  value: string;
  ok: boolean;
}

export function SummaryCard({ label, value, ok }: SummaryCardProps) {
  return (
    <div className={`p-4 rounded-lg border ${ok ? "border-green-200 bg-green-50" : "border-yellow-200 bg-yellow-50"}`}>
      <div className="flex items-center gap-2 mb-1">
        {ok ? <CheckCircle className="w-4 h-4 text-safe" /> : <XCircle className="w-4 h-4 text-warning" />}
        <span className="text-sm font-medium text-text">{label}</span>
      </div>
      <p className="text-sm text-text-secondary">{value}</p>
    </div>
  );
}
