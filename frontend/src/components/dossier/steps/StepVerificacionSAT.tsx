import { useEffect, useRef } from "react";
import { FiscalCheckResults } from "../../fiscal/FiscalCheckResults";
import { useFiscalChecks, useRunFiscalCheck } from "../../../hooks/useFiscalCheck";
import { LoadingSpinner } from "../../ui/LoadingSpinner";

interface Props {
  dossierId: string;
}

export function StepVerificacionSAT({ dossierId }: Props) {
  const { data: checks, isLoading } = useFiscalChecks(dossierId);
  const runCheck = useRunFiscalCheck(dossierId);
  const hasRun = useRef(false);

  useEffect(() => {
    if (!isLoading && !hasRun.current && (!checks || checks.length === 0) && !runCheck.isPending) {
      hasRun.current = true;
      runCheck.mutate();
    }
  }, [isLoading, checks, runCheck]);

  if (isLoading || runCheck.isPending) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-text-secondary mt-4">Consultando listas fiscales del SAT...</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Verificacion en Listas del SAT</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Se consulto el RFC en 8 listas fiscales publicas del SAT con datos reales.
      </p>
      <FiscalCheckResults
        checks={checks}
        isLoading={false}
        onRunCheck={() => runCheck.mutate()}
        isRunning={runCheck.isPending}
      />
    </div>
  );
}
