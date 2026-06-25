import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fiscal_check import FiscalListCheck
from app.services.audit_service import log_action
from app.utils.csv_parser import SAT_LISTS, search_rfc

logger = logging.getLogger(__name__)

_fiscal_lists: dict[str, dict[str, list[dict]]] = {}
_last_loaded: datetime | None = None


def get_loaded_lists() -> dict[str, dict[str, list[dict]]]:
    return _fiscal_lists


def set_loaded_lists(lists: dict[str, dict[str, list[dict]]]) -> None:
    global _fiscal_lists, _last_loaded
    _fiscal_lists = lists
    _last_loaded = datetime.now(timezone.utc)


def get_lists_status() -> dict:
    return {
        "loaded": bool(_fiscal_lists),
        "last_loaded": _last_loaded.isoformat() if _last_loaded else None,
        "lists_count": len(_fiscal_lists),
        "lists": {
            key: {
                "rfcs_count": len(rfc_index),
                "article": SAT_LISTS[key]["article"],
                "description": SAT_LISTS[key]["description"],
            }
            for key, rfc_index in _fiscal_lists.items()
        },
    }


async def check_rfc_in_lists(
    db: AsyncSession,
    *,
    dossier_id: uuid.UUID,
    rfc: str,
) -> list[FiscalListCheck]:
    if not _fiscal_lists:
        logger.warning("Fiscal lists not loaded, cannot check RFC %s", rfc)
        return []

    results = search_rfc(_fiscal_lists, rfc)
    checks: list[FiscalListCheck] = []

    for result in results:
        check = FiscalListCheck(
            dossier_id=dossier_id,
            rfc_searched=rfc.upper().strip(),
            list_type=result["list_type"],
            source_url=result["source_url"],
            found=result["found"],
            result_detail=result["details"] if result["found"] else None,
            list_reference=f"{result['article']} - {result['description']}",
        )
        db.add(check)
        checks.append(check)

    await db.flush()

    await log_action(
        db,
        action="fiscal.checked",
        dossier_id=dossier_id,
        details={
            "rfc": rfc,
            "lists_checked": len(results),
            "matches_found": sum(1 for r in results if r["found"]),
        },
    )

    return checks
