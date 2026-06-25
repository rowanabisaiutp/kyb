import { AlertTriangle, CheckCircle, RefreshCw, Shield } from "lucide-react";
import type { FiscalListCheck } from "../../types";
import { formatDateTime } from "../../utils/formatDate";
import { Button } from "../ui/Button";
import { Card, CardTitle } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { FiscalListBadge } from "./FiscalListBadge";

const LIST_LABELS: Record<string, string> = {
  art_69_cancelados: "Art. 69 - Cancelados",
  art_69_exigibles: "Art. 69 - Exigibles",
  art_69_firmes: "Art. 69 - Firmes",
  art_69_no_localizados: "Art. 69 - No Localizados",
  art_69_sentencias: "Art. 69 - Sentencias",
  art_69_csd_sin_efectos: "Art. 69 - CSD Sin Efectos",
  art_69b: "Art. 69-B - EFOS",
  art_69b_bis: "Art. 69-B Bis - Perdidas",
};

interface FiscalCheckResultsProps {
  checks: FiscalListCheck[] | undefined;
  isLoading: boolean;
  onRunCheck: () => void;
  isRunning: boolean;
}

export function FiscalCheckResults({ checks, isLoading, onRunCheck, isRunning }: FiscalCheckResultsProps) {
  if (isLoading) return <LoadingSpinner className="py-8" />;

  const hasChecks = checks && checks.length > 0;
  const matchCount = checks?.filter((c) => c.found).length ?? 0;
  const isClean = hasChecks && matchCount === 0;

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex items-center justify-between">
          <CardTitle>Consulta de Listas Fiscales SAT</CardTitle>
          <Button onClick={onRunCheck} loading={isRunning} variant="secondary" size="sm">
            <RefreshCw className="h-4 w-4" />
            {hasChecks ? "Consultar de Nuevo" : "Consultar Listas"}
          </Button>
        </div>

        {!hasChecks ? (
          <EmptyState
            title="Sin consultas realizadas"
            description="Ejecuta una consulta para verificar el RFC en las listas fiscales del SAT."
          />
        ) : (
          <>
            <div className={`flex items-center gap-3 mt-4 p-3 rounded-lg ${isClean ? "bg-green-50" : "bg-red-50"}`}>
              {isClean ? (
                <>
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <p className="text-sm font-medium text-green-700">RFC limpio en todas las listas fiscales</p>
                </>
              ) : (
                <>
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <p className="text-sm font-medium text-red-700">
                    RFC encontrado en {matchCount} {matchCount === 1 ? "lista" : "listas"} fiscal{matchCount === 1 ? "" : "es"}
                  </p>
                </>
              )}
            </div>

            <div className="mt-4 space-y-2">
              {checks.map((check) => (
                <div
                  key={check.id}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    check.found ? "border-red-200 bg-red-50" : "border-border"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Shield className={`h-4 w-4 ${check.found ? "text-red-500" : "text-green-500"}`} />
                    <div>
                      <p className="text-sm font-medium text-text">
                        {LIST_LABELS[check.list_type] ?? check.list_type}
                      </p>
                      <p className="text-xs text-text-secondary">{check.list_reference}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <FiscalListBadge found={check.found} />
                    <span className="text-xs text-text-secondary">{formatDateTime(check.checked_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
