import { ArrowLeft } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { createEntity } from "../api/entities";
import { isValidRfcFormat } from "../utils/formatRfc";
import { Header } from "../components/layout/Header";
import { Button } from "../components/ui/Button";
import { Card, CardTitle } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { useCreateDossier } from "../hooks/useDossiers";

export function DossierCreatePage() {
  const navigate = useNavigate();
  const createDossier = useCreateDossier();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    rfc: "",
    razon_social: "",
    nombre_comercial: "",
    domicilio_fiscal: "",
    codigo_postal: "",
    regimen_fiscal: "",
    objeto_social: "",
    representante_nombre: "",
    representante_cargo: "",
    representante_curp: "",
  });

  function updateField(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isValidRfcFormat(form.rfc)) {
      setError("Formato de RFC invalido. Debe tener 12-13 caracteres alfanumericos.");
      return;
    }

    setLoading(true);

    try {
      const entity = await createEntity({
        rfc: form.rfc.toUpperCase().trim(),
        razon_social: form.razon_social.trim(),
        nombre_comercial: form.nombre_comercial || undefined,
        domicilio_fiscal: form.domicilio_fiscal || undefined,
        codigo_postal: form.codigo_postal || undefined,
        regimen_fiscal: form.regimen_fiscal || undefined,
        objeto_social: form.objeto_social || undefined,
        representatives: form.representante_nombre
          ? [{ nombre_completo: form.representante_nombre, cargo: form.representante_cargo || undefined, curp: form.representante_curp || undefined }]
          : [],
      });

      const dossier = await createDossier.mutateAsync({ entity_id: entity.id });
      navigate(`/dossiers/${dossier.id}`);
    } catch (err: unknown) {
      let message = "Error al crear el expediente";
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        if (typeof detail === "string") {
          message = detail;
        } else if (Array.isArray(detail)) {
          message = detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join(". ");
        }
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Header
        title="Nuevo Expediente KYB"
        description="Registra una persona moral y crea su expediente"
        action={
          <Link to="/dossiers">
            <Button variant="ghost"><ArrowLeft className="h-4 w-4" /> Volver</Button>
          </Link>
        }
      />

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
        {error && (
          <div className="bg-danger-bg border border-red-200 text-danger rounded-lg p-3 text-sm">
            {error}
          </div>
        )}

        <Card>
          <CardTitle>Datos de la Persona Moral</CardTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <Input
              label="RFC *"
              id="rfc"
              value={form.rfc}
              onChange={(e) => updateField("rfc", e.target.value)}
              placeholder="XAXX010101000"
              maxLength={13}
              required
            />
            <Input
              label="Razon Social *"
              id="razon_social"
              value={form.razon_social}
              onChange={(e) => updateField("razon_social", e.target.value)}
              placeholder="Empresa SA de CV"
              required
            />
            <Input
              label="Nombre Comercial"
              id="nombre_comercial"
              value={form.nombre_comercial}
              onChange={(e) => updateField("nombre_comercial", e.target.value)}
            />
            <Input
              label="Codigo Postal"
              id="codigo_postal"
              value={form.codigo_postal}
              onChange={(e) => updateField("codigo_postal", e.target.value)}
              maxLength={5}
            />
            <div className="md:col-span-2">
              <Input
                label="Domicilio Fiscal"
                id="domicilio_fiscal"
                value={form.domicilio_fiscal}
                onChange={(e) => updateField("domicilio_fiscal", e.target.value)}
              />
            </div>
            <Input
              label="Regimen Fiscal"
              id="regimen_fiscal"
              value={form.regimen_fiscal}
              onChange={(e) => updateField("regimen_fiscal", e.target.value)}
            />
            <Input
              label="Objeto Social"
              id="objeto_social"
              value={form.objeto_social}
              onChange={(e) => updateField("objeto_social", e.target.value)}
            />
          </div>
        </Card>

        <Card>
          <CardTitle>Representante Legal</CardTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <Input
              label="Nombre Completo"
              id="representante_nombre"
              value={form.representante_nombre}
              onChange={(e) => updateField("representante_nombre", e.target.value)}
            />
            <Input
              label="Cargo"
              id="representante_cargo"
              value={form.representante_cargo}
              onChange={(e) => updateField("representante_cargo", e.target.value)}
              placeholder="Administrador Unico"
            />
            <Input
              label="CURP"
              id="representante_curp"
              value={form.representante_curp}
              onChange={(e) => updateField("representante_curp", e.target.value)}
              maxLength={18}
            />
          </div>
        </Card>

        <div className="flex justify-end gap-3">
          <Link to="/dossiers">
            <Button type="button" variant="secondary">Cancelar</Button>
          </Link>
          <Button type="submit" loading={loading}>
            Crear Expediente
          </Button>
        </div>
      </form>
    </>
  );
}
