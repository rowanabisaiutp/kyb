import { Link } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { EmptyState } from "../components/ui/EmptyState";

export function NotFoundPage() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <EmptyState
        title="Pagina no encontrada"
        description="La pagina que buscas no existe."
        action={
          <Link to="/">
            <Button>Ir al Dashboard</Button>
          </Link>
        }
      />
    </div>
  );
}
