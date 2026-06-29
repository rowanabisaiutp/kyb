import { AlertTriangle, CheckCircle, FileSearch, ShieldAlert, ShieldCheck, Sparkles, XCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { FiscalAnalysis, FiscalAnalysisHallazgo } from "../../../api/fiscal";
import { FiscalCheckResults } from "../../fiscal/FiscalCheckResults";
import { useFiscalChecks, useRunFiscalCheck, useRunFiscalAnalysis } from "../../../hooks/useFiscalCheck";
import { Button } from "../../ui/Button";
import { Card, CardTitle } from "../../ui/Card";
import { LoadingSpinner } from "../../ui/LoadingSpinner";

interface Props {
  dossierId: string;
}

const VEREDICTO_CONFIG = {
  limpio: {
    icon: ShieldCheck,
    label: "Limpio",
    bg: "bg-green-50 border-green-200",
    text: "text-green-700",
    iconColor: "text-green-600",
  },
  riesgo_medio: {
    icon: AlertTriangle,
    label: "Riesgo Medio",
    bg: "bg-yellow-50 border-yellow-200",
    text: "text-yellow-700",
    iconColor: "text-yellow-600",
  },
  alto_riesgo: {
    icon: ShieldAlert,
    label: "Alto Riesgo",
    bg: "bg-red-50 border-red-200",
    text: "text-red-700",
    iconColor: "text-red-600",
  },
};

const SEVERIDAD_COLORS = {
  info: "border-l-blue-400 bg-blue-50/50",
  warning: "border-l-yellow-400 bg-yellow-50/50",
  critical: "border-l-red-400 bg-red-50/50",
};

export function StepVerificacionSAT({ dossierId }: Props) {
  const { data: checks, isLoading } = useFiscalChecks(dossierId);
  const runCheck = useRunFiscalCheck(dossierId);
  const runAnalysis = useRunFiscalAnalysis(dossierId);
  const hasRun = useRef(false);
  const [analysis, setAnalysis] = useState<FiscalAnalysis | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !hasRun.current && (!checks || checks.length === 0) && !runCheck.isPending) {
      hasRun.current = true;
      runCheck.mutate();
    }
  }, [isLoading, checks, runCheck]);

  async function handleAnalysis() {
    setAnalysisError(null);
    try {
      const result = await runAnalysis.mutateAsync();
      setAnalysis(result);
    } catch {
      setAnalysisError("No se pudo generar el analisis. Verifica que las API keys esten configuradas.");
    }
  }

  if (isLoading || runCheck.isPending) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-text-secondary mt-4">Consultando listas fiscales del SAT...</p>
      </div>
    );
  }

  const hasChecks = checks && checks.length > 0;

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Verificacion en Listas del SAT</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Se consulto el RFC en las listas fiscales publicas del SAT con datos reales.
      </p>

      <FiscalCheckResults
        checks={checks}
        isLoading={false}
        onRunCheck={() => {
          setAnalysis(null);
          runCheck.mutate();
        }}
        isRunning={runCheck.isPending}
      />

      {hasChecks && (
        <Card className="mt-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              <CardTitle>Analisis AI de Resultados Fiscales</CardTitle>
            </div>
            {!analysis && (
              <Button
                onClick={handleAnalysis}
                loading={runAnalysis.isPending}
                variant="secondary"
                size="sm"
              >
                <FileSearch className="h-4 w-4" />
                Analizar con AI
              </Button>
            )}
          </div>

          {runAnalysis.isPending && (
            <div className="flex items-center gap-3 mt-4 p-4 bg-purple-50 rounded-lg animate-pulse">
              <LoadingSpinner size="sm" />
              <div>
                <p className="text-sm font-medium text-purple-700">Analizando resultados con AI...</p>
                <p className="text-xs text-purple-600 mt-0.5">
                  Verificando implicaciones legales y de riesgo para comercio exterior
                </p>
              </div>
            </div>
          )}

          {analysisError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{analysisError}</p>
            </div>
          )}

          {analysis && <FiscalAnalysisResults analysis={analysis} />}
        </Card>
      )}
    </div>
  );
}

function FiscalAnalysisResults({ analysis }: { analysis: FiscalAnalysis }) {
  const config = VEREDICTO_CONFIG[analysis.veredicto] ?? VEREDICTO_CONFIG.limpio;
  const VIcon = config.icon;

  return (
    <div className="mt-4 space-y-4">
      <div className={`flex items-start gap-4 p-4 rounded-lg border ${config.bg}`}>
        <VIcon className={`h-8 w-8 ${config.iconColor} shrink-0 mt-0.5`} />
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-sm font-bold ${config.text}`}>{config.label}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              analysis.puede_operar_comercio_exterior
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}>
              {analysis.puede_operar_comercio_exterior
                ? "Puede operar comercio exterior"
                : "No puede operar comercio exterior"}
            </span>
          </div>
          <p className={`text-sm ${config.text}`}>{analysis.resumen}</p>
          {analysis.fundamento_legal && (
            <p className="text-xs text-text-secondary mt-2">
              Fundamento: {analysis.fundamento_legal}
            </p>
          )}
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-text mb-3">Hallazgos por Lista</p>
        <div className="space-y-2">
          {analysis.hallazgos.map((h, i) => (
            <HallazgoRow key={i} hallazgo={h} />
          ))}
        </div>
      </div>

      {analysis.acciones_recomendadas.length > 0 && (
        <div>
          <p className="text-sm font-medium text-text mb-2">Acciones Recomendadas</p>
          <ul className="space-y-1.5">
            {analysis.acciones_recomendadas.map((accion, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                <span className="text-primary mt-0.5">•</span>
                {accion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function HallazgoRow({ hallazgo }: { hallazgo: FiscalAnalysisHallazgo }) {
  const severityClass = SEVERIDAD_COLORS[hallazgo.severidad] ?? SEVERIDAD_COLORS.info;

  return (
    <div className={`border-l-4 rounded-r-lg p-3 ${severityClass}`}>
      <div className="flex items-center gap-2 mb-1">
        {hallazgo.encontrado ? (
          <XCircle className="h-4 w-4 text-red-500 shrink-0" />
        ) : (
          <CheckCircle className="h-4 w-4 text-green-500 shrink-0" />
        )}
        <span className="text-sm font-medium text-text">{hallazgo.lista}</span>
        <span className={`text-xs px-1.5 py-0.5 rounded ${
          hallazgo.encontrado ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
        }`}>
          {hallazgo.encontrado ? "Encontrado" : "Limpio"}
        </span>
      </div>
      <p className="text-xs text-text-secondary ml-6">{hallazgo.explicacion}</p>
      {hallazgo.encontrado && hallazgo.implicacion && (
        <p className="text-xs text-text-secondary ml-6 mt-1 italic">{hallazgo.implicacion}</p>
      )}
    </div>
  );
}
