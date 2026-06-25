import json

from app.services.ai_providers import call_text_ai

SUMMARY_PROMPT = (
    "Eres un oficial de cumplimiento de una agencia aduanal mexicana. "
    "Genera un resumen ejecutivo en español (maximo 3 oraciones) del estado de este expediente KYB. "
    "Incluye: nombre de la empresa, estado en listas fiscales, documentos faltantes, "
    "discrepancias encontradas, y tu recomendacion (aprobar, revisar, o rechazar). "
    'Responde UNICAMENTE con un JSON: {"resumen": "<texto>", "recomendacion": "<aprobar|revisar|rechazar>"}'
)


async def generate_dossier_summary(dossier_data: dict) -> dict | None:
    context = json.dumps(dossier_data, ensure_ascii=False, default=str)
    prompt = f"{SUMMARY_PROMPT}\n\nDatos del expediente:\n{context}"
    return await call_text_ai(prompt)
