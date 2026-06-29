import axios from "axios";
import { CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { checkRfc, updateEntity } from "../../../api/entities";
import type { Dossier } from "../../../types";
import { isValidRfcFormat } from "../../../utils/formatRfc";
import { Button } from "../../ui/Button";
import { Input } from "../../ui/Input";

interface Props {
  dossier: Dossier;
  onComplete: () => void;
}

type RfcStatus = "idle" | "checking" | "valid" | "invalid_format" | "exists";

export function StepDatosEmpresa({ dossier, onComplete }: Props) {
  const entity = dossier.entity;
  const [form, setForm] = useState({
    rfc: entity?.rfc ?? "",
    razon_social: entity?.razon_social ?? "",
    nombre_comercial: entity?.nombre_comercial ?? "",
    domicilio_fiscal: "",
    codigo_postal: "",
    regimen_fiscal: "",
    objeto_social: "",
  });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rfcStatus, setRfcStatus] = useState<RfcStatus>("idle");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  }

  useEffect(() => {
    const rfc = form.rfc.trim().toUpperCase();

    if (!rfc || rfc === entity?.rfc) {
      setRfcStatus("idle");
      return;
    }

    if (!isValidRfcFormat(rfc)) {
      setRfcStatus(rfc.length >= 12 ? "invalid_format" : "idle");
      return;
    }

    setRfcStatus("checking");
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      try {
        const result = await checkRfc(rfc, entity?.id);
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
  }, [form.rfc, entity?.rfc, entity?.id]);

  const rfcBlocked = rfcStatus === "exists" || rfcStatus === "invalid_format";

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!entity || rfcBlocked) return;
    setLoading(true);
    setError(null);
    try {
      await updateEntity(entity.id, {
        rfc: form.rfc || undefined,
        razon_social: form.razon_social || undefined,
        nombre_comercial: form.nombre_comercial || undefined,
        domicilio_fiscal: form.domicilio_fiscal || undefined,
        codigo_postal: form.codigo_postal || undefined,
        regimen_fiscal: form.regimen_fiscal || undefined,
        objeto_social: form.objeto_social || undefined,
      });
      setSaved(true);
      onComplete();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail ?? "Error al guardar los datos");
      } else {
        setError("Error de conexion. Intenta de nuevo.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-text">Datos de la Empresa</h2>
      <p className="text-sm text-text-secondary mt-1 mb-6">
        Completa la informacion de la persona moral.
      </p>

      <form onSubmit={handleSave} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Input
              label="RFC"
              id="rfc"
              value={form.rfc}
              onChange={(e) => update("rfc", e.target.value)}
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
          <Input label="Razon Social" id="razon_social" value={form.razon_social}
            onChange={(e) => update("razon_social", e.target.value)} required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input label="Nombre Comercial" id="nombre_comercial" value={form.nombre_comercial}
            onChange={(e) => update("nombre_comercial", e.target.value)} />
          <Input label="Codigo Postal" id="codigo_postal" value={form.codigo_postal}
            onChange={(e) => update("codigo_postal", e.target.value)} maxLength={5} />
        </div>
        <Input label="Domicilio Fiscal" id="domicilio_fiscal" value={form.domicilio_fiscal}
          onChange={(e) => update("domicilio_fiscal", e.target.value)} />
        <div className="grid grid-cols-2 gap-4">
          <Input label="Regimen Fiscal" id="regimen_fiscal" value={form.regimen_fiscal}
            onChange={(e) => update("regimen_fiscal", e.target.value)} />
          <Input label="Objeto Social" id="objeto_social" value={form.objeto_social}
            onChange={(e) => update("objeto_social", e.target.value)} />
        </div>

        <div className="flex items-center gap-3">
          <Button type="submit" loading={loading} disabled={rfcBlocked}>Guardar Datos</Button>
          {saved && <span className="text-sm text-safe">Datos guardados correctamente</span>}
          {error && <span className="text-sm text-danger">{error}</span>}
        </div>
      </form>
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
