import axios from "axios";
import { type FormEvent, useState } from "react";
import { updateEntity } from "../../../api/entities";
import type { Dossier } from "../../../types";
import { Button } from "../../ui/Button";
import { Input } from "../../ui/Input";

interface Props {
  dossier: Dossier;
  onComplete: () => void;
}

export function StepDatosEmpresa({ dossier, onComplete }: Props) {
  const entity = dossier.entity;
  const [form, setForm] = useState({
    nombre_comercial: entity?.nombre_comercial ?? "",
    domicilio_fiscal: "",
    codigo_postal: "",
    regimen_fiscal: "",
    objeto_social: "",
  });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!entity) return;
    setLoading(true);
    setError(null);
    try {
      await updateEntity(entity.id, {
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
        Completa la informacion de la persona moral. Los campos marcados con * ya fueron proporcionados.
      </p>

      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-text-secondary">RFC *</p>
            <p className="font-mono font-semibold text-text">{entity?.rfc}</p>
          </div>
          <div>
            <p className="text-text-secondary">Razon Social *</p>
            <p className="font-semibold text-text">{entity?.razon_social}</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
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
          <Button type="submit" loading={loading}>Guardar Datos</Button>
          {saved && <span className="text-sm text-safe">Datos guardados correctamente</span>}
          {error && <span className="text-sm text-danger">{error}</span>}
        </div>
      </form>
    </div>
  );
}
