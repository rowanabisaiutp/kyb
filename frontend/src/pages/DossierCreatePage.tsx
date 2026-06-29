import axios from "axios";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createEntity, checkRfc } from "../api/entities";
import { Button } from "../components/ui/Button";
import { FadeIn } from "../components/ui/FadeIn";
import { Input } from "../components/ui/Input";
import { useCreateDossier } from "../hooks/useDossiers";
import { isValidRfcFormat } from "../utils/formatRfc";

type RfcStatus = "idle" | "checking" | "valid" | "invalid_format" | "exists";

const ERROR_MESSAGES: Record<string, string> = {
  "already exists": "Ya existe un expediente con este RFC. Ve a la lista de expedientes para encontrarlo.",
  "RFC format invalid": "El formato del RFC no es valido. Debe tener 12-13 caracteres (ej: XAXX010101000).",
};

function parseApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") {
      for (const [key, message] of Object.entries(ERROR_MESSAGES)) {
        if (detail.includes(key)) return message;
      }
      return detail;
    }
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
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    const normalized = rfc.trim().toUpperCase();

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
        if (!result.valid) {
          setRfcStatus("invalid_format");
        } else if (result.exists) {
          setRfcStatus("exists");
        } else {
          setRfcStatus("valid");
        }
      } catch {
        setRfcStatus("idle");
      }
    }, 500);

    return () => clearTimeout(debounceRef.current);
  }, [rfc]);

  const rfcBlocked = rfcStatus === "exists" || rfcStatus === "invalid_format";

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
      const entity = await createEntity({
        rfc: rfc.toUpperCase().trim(),
        razon_social: razonSocial.trim(),
      });
      const dossier = await createDossier.mutateAsync({ entity_id: entity.id });
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
                  rfcStatus === "exists" ? "Ya existe una entidad con este RFC" :
                  undefined
                }
              />
              <RfcIndicator status={rfcStatus} />
            </div>
            <Input
              label="Razon Social"
              id="razon_social"
              value={razonSocial}
              onChange={(e) => setRazonSocial(e.target.value)}
              placeholder="Ej: Empresa SA de CV"
              required
            />

            <Button type="submit" loading={loading} disabled={rfcBlocked} size="lg" className="w-full">
              Crear Expediente
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

function RfcIndicator({ status }: { status: RfcStatus }) {
  if (status === "checking") {
    return (
      <p className="mt-1 flex items-center gap-1 text-xs text-blue-600">
        <Loader2 className="h-3 w-3 animate-spin" /> Verificando RFC...
      </p>
    );
  }
  if (status === "valid") {
    return (
      <p className="mt-1 flex items-center gap-1 text-xs text-green-600">
        <CheckCircle className="h-3 w-3" /> RFC disponible
      </p>
    );
  }
  if (status === "exists") {
    return (
      <p className="mt-1 flex items-center gap-1 text-xs text-red-600">
        <AlertCircle className="h-3 w-3" /> RFC ya registrado en el sistema
      </p>
    );
  }
  return null;
}
