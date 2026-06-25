import { format, formatDistanceToNow, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export function formatDate(iso: string): string {
  try {
    const date = parseISO(iso);
    if (isNaN(date.getTime())) return iso;
    return format(date, "dd/MM/yyyy", { locale: es });
  } catch {
    return iso;
  }
}

export function formatDateTime(iso: string): string {
  try {
    const date = parseISO(iso);
    if (isNaN(date.getTime())) return iso;
    return format(date, "dd/MM/yyyy HH:mm", { locale: es });
  } catch {
    return iso;
  }
}

export function formatRelative(iso: string): string {
  try {
    const date = parseISO(iso);
    if (isNaN(date.getTime())) return iso;
    return formatDistanceToNow(date, { addSuffix: true, locale: es });
  } catch {
    return iso;
  }
}
