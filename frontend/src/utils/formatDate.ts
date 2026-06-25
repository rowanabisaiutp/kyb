import { format, formatDistanceToNow, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export function formatDate(iso: string): string {
  return format(parseISO(iso), "dd/MM/yyyy", { locale: es });
}

export function formatDateTime(iso: string): string {
  return format(parseISO(iso), "dd/MM/yyyy HH:mm", { locale: es });
}

export function formatRelative(iso: string): string {
  return formatDistanceToNow(parseISO(iso), { addSuffix: true, locale: es });
}
