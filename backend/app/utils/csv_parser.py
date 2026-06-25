import csv
import io
import logging
import httpx
from app.utils.data.data_csv import SAT_LISTS

logger = logging.getLogger(__name__)


def _find_rfc_column(headers: list[str]) -> int | None:
    for i, h in enumerate(headers):
        if h.strip().upper() == "RFC":
            return i
    for i, h in enumerate(headers):
        if "RFC" in h.strip().upper():
            return i
    return None


# Req: Consultar listas fiscales publicas del SAT con datos reales, sin mocks.
async def download_and_parse_csv(list_key: str) -> dict[str, list[dict]]:
    config = SAT_LISTS[list_key]
    url = config["url"]
    rfc_index: dict[str, list[dict]] = {}

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url)
            response.raise_for_status()

        content = response.text
        reader = csv.reader(io.StringIO(content))

        rfc_col = None
        headers = None
        for row in reader:
            rfc_col = _find_rfc_column(row)
            if rfc_col is not None:
                headers = row
                break

        if headers is None or rfc_col is None:
            logger.warning("No RFC column found in %s", list_key)
            return rfc_index

        clean_headers = [h.strip() for h in headers]

        for row in reader:
            if len(row) <= rfc_col:
                continue
            rfc = row[rfc_col].strip().upper()
            if not rfc:
                continue
            row_data = {}
            for i, val in enumerate(row):
                if i < len(clean_headers):
                    row_data[clean_headers[i]] = val.strip()
            rfc_index.setdefault(rfc, []).append(row_data)

        logger.info("Loaded %s: %d unique RFCs", list_key, len(rfc_index))

    except Exception as e:
        logger.error("Failed to download/parse %s: %s", list_key, e)

    return rfc_index


async def load_all_lists() -> dict[str, dict[str, list[dict]]]:
    import asyncio

    keys = list(SAT_LISTS.keys())
    url_to_key: dict[str, str] = {}
    to_download: list[str] = []
    reuse_map: dict[str, str] = {}

    for k in keys:
        url = SAT_LISTS[k]["url"]
        if url in url_to_key:
            reuse_map[k] = url_to_key[url]
        else:
            url_to_key[url] = k
            to_download.append(k)

    results = await asyncio.gather(*[download_and_parse_csv(k) for k in to_download])
    all_lists = dict(zip(to_download, results))

    for k, source_k in reuse_map.items():
        all_lists[k] = all_lists[source_k]
        logger.info("Reused %s data for %s (same source URL)", source_k, k)

    return all_lists


# Req: Cada revision guarda fuente, RFC buscado, resultado y referencia al listado.
def search_rfc(all_lists: dict[str, dict[str, list[dict]]], rfc: str) -> list[dict]:
    rfc = rfc.strip().upper()
    results = []
    for list_key, rfc_index in all_lists.items():
        config = SAT_LISTS[list_key]
        found = rfc in rfc_index
        results.append(
            {
                "list_type": list_key,
                "article": config["article"],
                "description": config["description"],
                "source_url": config["url"],
                "found": found,
                "details": rfc_index.get(rfc, []) if found else [],
            }
        )
    return results
