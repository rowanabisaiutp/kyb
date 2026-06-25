import { AlertTriangle, CheckCircle, FileText, ShieldAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardTitle } from "../components/ui/Card";
import { FadeIn } from "../components/ui/FadeIn";
import { LoadingSpinner } from "../components/ui/LoadingSpinner";
import { StatusBadge } from "../components/ui/StatusBadge";
import { Header } from "../components/layout/Header";
import { Button } from "../components/ui/Button";
import { useDossiers, useDossierStats } from "../hooks/useDossiers";
import { formatRelative } from "../utils/formatDate";
import type { DossierStatus } from "../types";

const STAT_CARDS: { key: DossierStatus; label: string; icon: typeof FileText; color: string }[] = [
  { key: "draft", label: "Borradores", icon: FileText, color: "text-gray-500" },
  { key: "in_review", label: "En Revision", icon: AlertTriangle, color: "text-blue-500" },
  { key: "approved", label: "Aprobados", icon: CheckCircle, color: "text-green-500" },
  { key: "high_risk", label: "Alto Riesgo", icon: ShieldAlert, color: "text-red-500" },
];

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useDossierStats();
  const { data: recentDossiers, isLoading: dossiersLoading } = useDossiers();

  return (
    <>
      <FadeIn>
        <Header
          title="Dashboard"
          description="Vista general de expedientes KYB"
          action={
            <Link to="/dossiers/new">
              <Button>Nuevo Expediente</Button>
            </Link>
          }
        />
      </FadeIn>

      {statsLoading ? (
        <LoadingSpinner className="py-12" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {STAT_CARDS.map(({ key, label, icon: Icon, color }, i) => (
            <FadeIn key={key} delay={80 * i}>
              <Card>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-text-secondary">{label}</p>
                    <p className="text-3xl font-bold text-text mt-1">{stats?.[key] ?? 0}</p>
                  </div>
                  <Icon className={`h-10 w-10 ${color} opacity-80`} />
                </div>
              </Card>
            </FadeIn>
          ))}
        </div>
      )}

      <FadeIn delay={350}>
        <Card>
          <CardTitle>Expedientes Recientes</CardTitle>
          {dossiersLoading ? (
            <LoadingSpinner className="py-8" />
          ) : !recentDossiers?.length ? (
            <p className="text-sm text-text-secondary py-4">No hay expedientes creados aun.</p>
          ) : (
            <div className="divide-y divide-border -mx-6">
              {recentDossiers.slice(0, 10).map((d) => (
                <Link
                  key={d.id}
                  to={`/dossiers/${d.id}`}
                  className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between px-4 sm:px-6 py-3 hover:bg-gray-50 transition-colors no-underline"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-text truncate">{d.entity?.razon_social ?? "—"}</p>
                    <p className="text-xs text-text-secondary">{d.entity?.rfc}</p>
                  </div>
                  <div className="flex items-center gap-3 mt-1 sm:mt-0">
                    <StatusBadge status={d.status} />
                    <span className="text-xs text-text-secondary">{formatRelative(d.created_at)}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </Card>
      </FadeIn>
    </>
  );
}
