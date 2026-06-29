import axios from "axios";
import { AlertCircle, CheckCircle, Info, Loader2, ShieldAlert, ShieldCheck } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createEntity, checkRfc } from "../api/entities";
import type { RfcCheckResult } from "../api/entities";
import { Button } from "../components/ui/Button";
import { FadeIn } from "../components/ui/FadeIn";
import { Input } from "../components/ui/Input";
import { useCreateDossier } from "../hooks/useDossiers";
import { isValidRfcFormat } from "../utils/formatRfc";

type RfcStatus = "idle" | "checking" | "valid" | "invalid_format" | "exists" | "sat_alert";

function parseApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    return "Error al crear el expediente. Verifica los datos e intenta de nuevo.";
  }
  return "Error de conexion. Intenta de nuevo.";
}

export function DossierCreatePage() {
  const navigate = useNavigate();
  const createDossier = useCreateDossier();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rfc, setRfc] = useState("");
  const [razonSocial, setRazonSocial] = useState("");
  const [rfcStatus, setRfcStatus] = useState<RfcStatus>("idle");
  const [rfcCheckResult, setRfcCheckResult] = useState<RfcCheckResult | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    const normalized = rfc.trim().toUpperCase();
    setRfcCheckResult(null);

    if (!normalized) {
      setRfcStatus("idle");
      return;
    }

    if (!isValidRfcFormat(normalized)) {
      setRfcStatus(normalized.length >= 12 ? "invalid_format" : "idle");
      return;
    }

    setRfcStatus("checking");
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const result = await checkRfc(normalized);
        setRfcCheckResult(result);
        if (!result.valid) {
          setRfcStatus("invalid_format");
        } else if (result.exists) {
          setRfcStatus("exists");
        } else if (result.found_in_sat) {
          setRfcStatus("sat_alert");
        } else {
          setRfcStatus("valid");
        }
      } catch {
        setRfcStatus("idle");
      }
    }, 500);

    return () => clearTimeout(debounceRef.current);
  }, [rfc]);

  const rfcBlocked = rfcStatus === "invalid_format";
  const existingEntity = rfcStatus === "exists" && rfcCheckResult?.entity_id;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (rfcBlocked) return;

    if (!isValidRfcFormat(rfc)) {
      setError("Formato de RFC invalido. Debe tener 12-13 caracteres.");
      return;
    }

    setLoading(true);
    try {
      let entityId: string;

      if (existingEntity) {
        entityId = rfcCheckResult!.entity_id!;
      } else {
        const entity = await createEntity({
          rfc: rfc.toUpperCase().trim(),
          razon_social: razonSocial.trim(),
        });
        entityId = entity.id;
      }

      const dossier = await createDossier.mutateAsync({ entity_id: entityId });
      navigate(`/dossiers/${dossier.id}?step=0`);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <FadeIn className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-text">Nuevo Expediente KYB</h1>
          <p className="text-sm text-text-secondary mt-2">
            Ingresa el RFC y la razon social para iniciar el proceso de evaluacion.
          </p>
        </div>

        <div className="bg-white border border-border rounded-xl p-8">
          {error && (
            <div className="bg-danger-bg border border-red-200 text-danger rounded-lg p-3 text-sm mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Input
                label="RFC de la Persona Moral"
                id="rfc"
                value={rfc}
                onChange={(e) => setRfc(e.target.value)}
                placeholder="Ej: AAA010101AAA"
                maxLength={13}
                required
                error={
                  rfcStatus === "invalid_format" ? "Formato de RFC invalido (ej: XAXX010101000)" :
                  undefined
                }
              />
              <RfcIndicator status={rfcStatus} checkResult={rfcCheckResult} />
            </div>
            {!existingEntity && (
              <Input
                label="Razon Social"
                id="razon_social"
                value={razonSocial}
                onChange={(e) => setRazonSocial(e.target.value)}
                placeholder="Ej: Empresa SA de CV"
                required
              />
            )}

            <Button type="submit" loading={loading} disabled={rfcBlocked} size="lg" className="w-full">
              {existingEntity ? "Crear Nuevo Expediente" : "Crear Expediente"}
            </Button>
          </form>

          <p className="text-xs text-text-secondary text-center mt-4">
            Podras completar los datos adicionales en el siguiente paso.
          </p>
        </div>

        <div className="text-center mt-4">
          <Link to="/dossiers" className="text-sm text-primary hover:underline">
            Volver a expedientes
          </Link>
        </div>
      </FadeIn>
    </div>
  );
}

function RfcIndicator({ status, checkResult }: { status: RfcStatus; checkResult: RfcCheckResult | null }) {
  if (status === "checking") {
    return (
      <p className="mt-1 flex items-center gap-1 text-xs text-blue-600">
        <Loader2 className="h-3 w-3 animate-spin" /> Verificando RFC en SAT...
      </p>
    );
  }
  if (status === "exists" && checkResult) {
    return (
      <div className="mt-1 space-y-1">
        <div className="p-2 bg-blue-50 border border-blue-200 rounded">
          <p className="flex items-center gap-1 text-xs font-medium text-blue-700">
            <Info className="h-3 w-3" /> Entidad ya registrada: {checkResult.razon_social}
          </p>
          <p className="text-xs text-blue-600 ml-4 mt-0.5">
            Se creara un nuevo expediente vinculado a esta entidad.
          </p>
        </div>
        {checkResult.found_in_sat && (
          <div className="p-2 bg-red-50 border border-red-200 rounded">
            <p className="flex items-center gap-1 text-xs font-medium text-red-700">
              <ShieldAlert className="h-3 w-3" /> RFC encontrado en {checkResult.lists_matched.length} lista(s) del SAT:
            </p>
            <ul className="mt-1 space-y-0.5">
              {checkResult.lists_matched.map((m, i) => (
                <li key={i} className="text-xs text-red-600 ml-4">
                  • {m.article} — {m.description}
                </li>
              ))}
            </ul>
          </div>
        )}
        {!checkResult.found_in_sat && checkResult.sat_lists_loaded && (
          <p className="flex items-center gap-1 text-xs text-green-600">
            <ShieldCheck className="h-3 w-3" /> Limpio en {checkResult.total_lists_checked} listas del SAT
          </p>
        )}
      </div>
    );
  }
  if (status === "valid") {
    return (
      <div className="mt-1 space-y-0.5">
        <p className="flex items-center gap-1 text-xs text-green-600">
          <CheckCircle className="h-3 w-3" /> RFC disponible
        </p>
        <p className="flex items-center gap-1 text-xs text-green-600">
          <ShieldCheck className="h-3 w-3" /> Limpio en {checkResult?.total_lists_checked ?? 0} listas del SAT
        </p>
      </div>
    );
  }
  if (status === "sat_alert" && checkResult) {
    return (
      <div className="mt-1 space-y-1">
        <p className="flex items-center gap-1 text-xs text-green-600">
          <CheckCircle className="h-3 w-3" /> RFC disponible
        </p>
        <div className="p-2 bg-red-50 border border-red-200 rounded">
          <p className="flex items-center gap-1 text-xs font-medium text-red-700">
            <ShieldAlert className="h-3 w-3" /> RFC encontrado en {checkResult.lists_matched.length} lista(s) del SAT:
          </p>
          <ul className="mt-1 space-y-0.5">
            {checkResult.lists_matched.map((m, i) => (
              <li key={i} className="text-xs text-red-600 ml-4">
                • {m.article} — {m.description}
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
  if (status === "invalid_format") {
    return (
      <p className="mt-1 flex items-center gap-1 text-xs text-red-600">
        <AlertCircle className="h-3 w-3" /> Formato invalido
      </p>
    );
  }
  return null;
}
