import csv
import io
import logging

import httpx

logger = logging.getLogger(__name__)

SAT_LISTS = {
    "art_69_cancelados": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Cancelados.csv",
        "article": "69 CFF",
        "description": "Contribuyentes con creditos fiscales cancelados",
    },
    "art_69_exigibles": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Exigibles.csv",
        "article": "69 CFF",
        "description": "Contribuyentes con creditos fiscales exigibles",
    },
    "art_69_firmes": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Firmes.csv",
        "article": "69 CFF",
        "description": "Contribuyentes con creditos fiscales firmes",
    },
    "art_69_no_localizados": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/No_localizados.csv",
        "article": "69 CFF",
        "description": "Contribuyentes no localizados",
    },
    "art_69_sentencias": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Sentencias.csv",
        "article": "69 CFF",
        "description": "Contribuyentes con sentencia condenatoria por delito fiscal",
    },
    "art_69_csd_sin_efectos": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/CSDsinefectos.csv",
        "article": "69 CFF",
        "description": "Contribuyentes con CSD sin efectos",
    },
    "art_69b": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv",
        "article": "69-B CFF",
        "description": "Operaciones presuntamente inexistentes (EFOS) - listado completo",
    },
    "art_69b_bis": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_Completo.csv",
        "article": "69-B Bis CFF",
        "description": "Transmision indebida de perdidas fiscales",
    },
    "art_49bis": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv",
        "article": "49 Bis CFF",
        "description": "Operaciones con EFOS (fuente: listado Art. 69-B, unica base publica disponible del SAT)",
    },
}


def _find_rfc_column(headers: list[str]) -> int | None:
    for i, h in enumerate(headers):
        if h.strip().upper() == "RFC":
            return i
    for i, h in enumerate(headers):
        if "RFC" in h.strip().upper():
            return i
    return None


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
