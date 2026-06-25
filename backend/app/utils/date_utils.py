from datetime import date, datetime, timedelta

# UTILIDADES DE FECHA: usadas por vigencias (validity_service) y conciliacion.


# Vigencia CSF: True si la fecha es del mes/año actual.
def is_current_month(d: date | None) -> bool:
    if not d:
        return False
    today = date.today()
    return d.year == today.year and d.month == today.month


# Vigencia docs: True si fecha_vencimiento < hoy.
def is_expired(expiration_date: date | None) -> bool:
    if not expiration_date:
        return False
    return expiration_date < date.today()


# Vigencia fiscal: True si la fecha es anterior a hoy - (months * 30 dias).
def is_older_than_months(d: date | None, months: int) -> bool:
    if not d:
        return True
    threshold = date.today() - timedelta(days=months * 30)
    return d < threshold


# Conciliacion de fechas: parsea 4 formatos (YYYY-MM-DD, DD/MM/YYYY, etc.).
def safe_parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None
