import { Plus, Search, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Header } from "../components/layout/Header";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useDeleteDossier, useDossiers } from "../hooks/useDossiers";
import { formatDate } from "../utils/formatDate";

export function DossierListPage() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data: dossiers, isLoading } = useDossiers({
    search: debouncedSearch || undefined,
    status: statusFilter || undefined,
  });

  return (
    <>
      <Header
        title="Expedientes KYB"
        description="Gestion de expedientes de personas morales"
        action={
          <Link to="/dossiers/new">
            <Button><Plus className="h-4 w-4" /> Nuevo Expediente</Button>
          </Link>
        }
      />

      <Card className="mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
            <input
              type="text"
              placeholder="Buscar por RFC o razon social..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
          >
            <option value="">Todos los estados</option>
            <option value="draft">Borrador</option>
            <option value="in_review">En Revision</option>
            <option value="safe">Seguro</option>
            <option value="review_required">Requiere Revision</option>
            <option value="high_risk">Alto Riesgo</option>
            <option value="approved">Aprobado</option>
            <option value="rejected">Rechazado</option>
          </select>
        </div>
      </Card>

      {isLoading ? (
        <LoadingSpinner className="py-12" />
      ) : !dossiers?.length ? (
        <EmptyState
          title="No hay expedientes"
          description="Crea tu primer expediente KYB para comenzar."
          action={
            <Link to="/dossiers/new">
              <Button>Crear Expediente</Button>
            </Link>
          }
        />
      ) : (
        <div className="space-y-3">
          {dossiers.map((d) => (
            <div key={d.id} className="flex items-center gap-2">
              <Link to={`/dossiers/${d.id}`} className="block no-underline flex-1">
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-text">{d.entity?.razon_social ?? "—"}</p>
                      <p className="text-xs text-text-secondary mt-0.5">RFC: {d.entity?.rfc}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      {d.current_risk_score != null && (
                        <span className="text-sm font-mono text-text-secondary">
                          Score: {d.current_risk_score}
                        </span>
                      )}
                      <StatusBadge status={d.status} />
                      <span className="text-xs text-text-secondary">{formatDate(d.created_at)}</span>
                    </div>
                  </div>
                </Card>
              </Link>
              <DeleteButton dossierId={d.id} />
            </div>
          ))}
        </div>
      )}
    </>
  );
}

function DeleteButton({ dossierId }: { dossierId: string }) {
  const deleteMutation = useDeleteDossier();

  function handleDelete(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (window.confirm("¿Eliminar este expediente? Esta accion no se puede deshacer.")) {
      deleteMutation.mutate(dossierId);
    }
  }

  return (
    <button
      type="button"
      onClick={handleDelete}
      className="p-2 text-text-secondary hover:text-danger hover:bg-red-50 rounded-lg transition-colors cursor-pointer shrink-0"
      title="Eliminar expediente"
    >
      <Trash2 className="h-4 w-4" />
    </button>
  );
}
