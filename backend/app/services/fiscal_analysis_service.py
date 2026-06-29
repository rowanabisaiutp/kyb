import json
import logging

from app.services.ai_providers import call_text_ai

logger = logging.getLogger(__name__)

FISCAL_ANALYSIS_PROMPT = """Eres un experto en cumplimiento fiscal mexicano y compliance KYB para agencias aduanales.

Analiza los resultados de la verificacion del RFC en las listas fiscales del SAT y genera un dictamen detallado.

Para cada lista donde el RFC fue ENCONTRADO, explica:
1. Que significa estar en esa lista
2. Las implicaciones legales y de riesgo
3. Si bloquea operaciones de comercio exterior
4. Recomendacion especifica

Para las listas donde NO fue encontrado, confirma que el contribuyente esta limpio en ese rubro.

Al final genera:
- Un veredicto general: "limpio", "riesgo_medio" o "alto_riesgo"
- Un resumen ejecutivo de 2-3 oraciones
- Acciones recomendadas

Responde UNICAMENTE con un JSON valido con esta estructura:
{
  "veredicto": "limpio|riesgo_medio|alto_riesgo",
  "resumen": "<resumen ejecutivo en 2-3 oraciones>",
  "hallazgos": [
    {
      "lista": "<nombre de la lista>",
      "encontrado": true/false,
      "explicacion": "<que significa>",
      "implicacion": "<implicacion legal>",
      "severidad": "info|warning|critical"
    }
  ],
  "acciones_recomendadas": ["<accion 1>", "<accion 2>"],
  "puede_operar_comercio_exterior": true/false,
  "fundamento_legal": "<articulos aplicables>"
}"""


async def analyze_fiscal_results(
    entity_data: dict,
    fiscal_checks: list[dict],
) -> dict | None:
    context = json.dumps(
        {
            "empresa": entity_data,
            "resultados_fiscales": fiscal_checks,
        },
        ensure_ascii=False,
        default=str,
    )
    prompt = f"{FISCAL_ANALYSIS_PROMPT}\n\nDatos:\n{context}"

    try:
        result = await call_text_ai(prompt)
        if result and "veredicto" in result:
            return result
        logger.warning("AI fiscal analysis returned unexpected format")
        return result
    except Exception as e:
        logger.error("Fiscal analysis failed: %s", e)
        return None
