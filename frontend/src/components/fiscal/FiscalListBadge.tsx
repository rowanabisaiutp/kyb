import { Badge } from "../ui/Badge";

interface FiscalListBadgeProps {
  found: boolean;
}

export function FiscalListBadge({ found }: FiscalListBadgeProps) {
  return found ? (
    <Badge className="bg-red-100 text-red-700">Encontrado</Badge>
  ) : (
    <Badge className="bg-green-100 text-green-700">Limpio</Badge>
  );
}
