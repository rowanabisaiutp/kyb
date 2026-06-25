import { CheckCircle, RefreshCw, XCircle } from "lucide-react";
import type { ReconciliationResult } from "../../types";
import { Button } from "../ui/Button";
import { Card, CardTitle } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { DiscrepancyAlert, SeverityBadge } from "./DiscrepancyAlert";

const FIELD_LABELS: Record<string, string> = {
  rfc: "RFC",
  razon_social: "Razon Social",
  domicilio: "Domicilio",
  representante_legal: "Representante Legal",
};

const SOURCE_LABELS: Record<string, string> = {
  formulario: "Formulario",
  constancia_situacion_fiscal: "CSF",
  acta_constitutiva: "Acta Constitutiva",
  comprobante_domicilio: "Comprobante Domicilio",
  poder_representacion: "Poder de Representacion",
  identificacion_representante: "Identificacion",
};

interface ReconciliationTableProps {
  results: ReconciliationResult[] | undefined;
  isLoading: boolean;
  onRun: () => void;
  isRunning: boolean;
}

export function ReconciliationTable({ results, isLoading, onRun, isRunning }: ReconciliationTableProps) {
  if (isLoading) return <LoadingSpinner className="py-8" />;

  const hasResults = results && results.length > 0;
  const discrepancies = results?.filter((r) => !r.match) ?? [];
  const hasCritical = discrepancies.some((r) => r.severity === "critical");

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle>Conciliacion de Datos</CardTitle>
          <Button onClick={onRun} loading={isRunning} variant="secondary" size="sm">
            <RefreshCw className="h-4 w-4" />
            {hasResults ? "Ejecutar de Nuevo" : "Ejecutar Conciliacion"}
          </Button>
        </div>

        {!hasResults ? (
          <EmptyState
            title="Sin conciliacion realizada"
            description="Sube documentos y ejecuta la conciliacion para comparar datos entre fuentes."
          />
        ) : (
          <>
            <div className="mt-4">
              <DiscrepancyAlert discrepancies={discrepancies.length} hasCritical={hasCritical} />
            </div>

            {discrepancies.length === 0 && (
              <div className="flex items-center gap-3 mt-4 p-3 rounded-lg bg-green-50">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <p className="text-sm font-medium text-green-700">
                  Todos los datos concilian correctamente
                </p>
              </div>
            )}

            <div className="mt-4 space-y-3">
              {results.map((r) => (
                <div
                  key={r.id}
                  className={`p-4 rounded-lg border ${
                    !r.match
                      ? r.severity === "critical"
                        ? "border-red-200 bg-red-50"
                        : "border-yellow-200 bg-yellow-50"
                      : "border-border"
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {r.match ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <span className="text-sm font-medium text-text">
                        {FIELD_LABELS[r.field_name] ?? r.field_name}
                      </span>
                    </div>
                    <SeverityBadge severity={r.severity} />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 text-sm">
                    <div>
                      <p className="text-xs text-text-secondary mb-1">
                        {SOURCE_LABELS[r.source_a] ?? r.source_a}
                      </p>
                      <p className={`font-mono text-xs ${!r.match ? "text-red-700" : "text-text"}`}>
                        {r.value_a || "—"}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-text-secondary mb-1">
                        {SOURCE_LABELS[r.source_b] ?? r.source_b}
                      </p>
                      <p className={`font-mono text-xs ${!r.match ? "text-red-700" : "text-text"}`}>
                        {r.value_b || "—"}
                      </p>
                    </div>
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
