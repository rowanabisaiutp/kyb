import axios from "axios";
import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createEntity } from "../api/entities";
import { Button } from "../components/ui/Button";
import { FadeIn } from "../components/ui/FadeIn";
import { Input } from "../components/ui/Input";
import { useCreateDossier } from "../hooks/useDossiers";
import { formatRfc, isValidRfcFormat } from "../utils/formatRfc";

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

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isValidRfcFormat(rfc)) {
      setError("Formato de RFC invalido. Debe tener 12-13 caracteres.");
      return;
    }

    setLoading(true);
    try {
      const entity = await createEntity({
        rfc: formatRfc(rfc),
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
            <Input
              label="RFC de la Persona Moral"
              id="rfc"
              value={rfc}
              onChange={(e) => setRfc(e.target.value)}
              placeholder="Ej: AAA010101AAA"
              maxLength={13}
              required
            />
            <Input
              label="Razon Social"
              id="razon_social"
              value={razonSocial}
              onChange={(e) => setRazonSocial(e.target.value)}
              placeholder="Ej: Empresa SA de CV"
              required
            />

            <Button type="submit" loading={loading} size="lg" className="w-full">
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
