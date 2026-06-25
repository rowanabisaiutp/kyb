import { useEffect } from "react";
import { ReconciliationTable } from "../../reconciliation/ReconciliationTable";
import { useReconciliation, useRunReconciliation } from "../../../hooks/useReconciliation";
import { LoadingSpinner } from "../../ui/LoadingSpinner";

interface Props {
  dossierId: string;
}

export function StepConciliacion({ dossierId }: Props) {
  const { data: results, isLoading } = useReconciliation(dossierId);
  const run = useRunReconciliation(dossierId);

  useEffect(() => {
    if (!isLoading && (!results || results.length === 0) && !run.isPending) {
      run.mutate();
    }
  }, [isLoading]);

  if (isLoading || run.isPending) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-text-secondary mt-4">Ejecutando conciliacion de datos...</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Conciliacion de Datos</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Se compararon los datos entre documentos y el formulario para detectar discrepancias.
      </p>
      <ReconciliationTable
        results={results}
        isLoading={false}
        onRun={() => run.mutate()}
        isRunning={run.isPending}
      />
    </div>
  );
}
