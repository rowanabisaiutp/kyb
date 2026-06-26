import { AlertTriangle, Sparkles } from "lucide-react";
import type { DossierSummary } from "../../../api/ai";

interface AISummarySectionProps {
  summary: DossierSummary | null;
  loading: boolean;
  error?: boolean;
}

export function AISummarySection({ summary, loading, error }: AISummarySectionProps) {
  if (loading) {
    return (
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-purple-700">Generando resumen ejecutivo con AI...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-yellow-600" />
          <p className="text-sm text-yellow-700">No se pudo generar el resumen ejecutivo AI. Puedes continuar sin el.</p>
        </div>
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-4 h-4 text-purple-600" />
        <span className="text-sm font-semibold text-purple-700">Resumen Ejecutivo AI</span>
      </div>
      <p className="text-sm text-text">{summary.resumen}</p>
      <p className="text-xs text-purple-600 mt-2 font-medium">
        Recomendacion AI: {summary.recomendacion}
      </p>
    </div>
  );
}
