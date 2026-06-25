import base64
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, ExtractionStatus
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)

EXTRACTION_PROMPTS: dict[str, str] = {
    "constancia_situacion_fiscal": (
        "Extrae los siguientes datos de esta Constancia de Situacion Fiscal (CSF) del SAT. "
        "Responde UNICAMENTE con un JSON valido, sin explicaciones:\n"
        '{"rfc": "", "razon_social": "", "domicilio_fiscal": "", '
        '"codigo_postal": "", "regimen_fiscal": "", "fecha_emision": ""}'
    ),
    "acta_constitutiva": (
        "Extrae los siguientes datos de esta Acta Constitutiva o instrumento notarial. "
        "Responde UNICAMENTE con un JSON valido, sin explicaciones:\n"
        '{"razon_social": "", "rfc": "", "fecha_constitucion": "", '
        '"objeto_social": "", "notario": "", "numero_escritura": "", '
        '"socios": [{"nombre": "", "porcentaje": ""}], '
        '"representante_legal": ""}'
    ),
    "identificacion_representante": (
        "Extrae los siguientes datos de esta identificacion oficial. "
        "Responde UNICAMENTE con un JSON valido, sin explicaciones:\n"
        '{"nombre_completo": "", "curp": "", "fecha_nacimiento": "", '
        '"fecha_vencimiento": "", "tipo_identificacion": "", "clave_elector": ""}'
    ),
    "comprobante_domicilio": (
        "Extrae los siguientes datos de este comprobante de domicilio. "
        "Responde UNICAMENTE con un JSON valido, sin explicaciones:\n"
        '{"direccion_completa": "", "codigo_postal": "", '
        '"fecha_emision": "", "tipo_comprobante": ""}'
    ),
    "poder_representacion": (
        "Extrae los siguientes datos de este poder notarial o evidencia de representacion. "
        "Responde UNICAMENTE con un JSON valido, sin explicaciones:\n"
        '{"representante_legal": "", "tipo_poder": "", '
        '"fecha_otorgamiento": "", "notario": "", "numero_escritura": ""}'
    ),
    "manifestacion_protesta": (
        "Extrae los siguientes datos de esta manifestacion bajo protesta de decir verdad. "
        "Responde UNICAMENTE con un JSON valido, sin explicaciones:\n"
        '{"declarante": "", "fecha": "", "contenido_resumen": ""}'
    ),
}

DEFAULT_PROMPT = (
    "Extrae todos los datos relevantes de este documento. "
    "Responde UNICAMENTE con un JSON valido con los campos que identifiques."
)


def _get_prompt(document_type: str) -> str:
    return EXTRACTION_PROMPTS.get(document_type, DEFAULT_PROMPT)


async def extract_document_data(
    db: AsyncSession,
    document: Document,
    file_data: bytes,
) -> dict | None:
    document.extraction_status = ExtractionStatus.PROCESSING.value
    await db.flush()

    extracted = None

    if settings.GEMINI_API_KEY:
        extracted = await _extract_with_gemini(document, file_data)
    elif settings.ANTHROPIC_API_KEY:
        extracted = await _extract_with_anthropic(document, file_data)
    else:
        logger.warning("No AI API key configured, skipping extraction")
        document.extraction_status = ExtractionStatus.FAILED.value
        await db.flush()
        return None

    if extracted:
        document.extracted_data = extracted
        document.extraction_status = ExtractionStatus.COMPLETED.value
        await db.flush()
        await log_action(
            db,
            action="extraction.completed",
            dossier_id=document.dossier_id,
            details={
                "document_id": str(document.id),
                "document_type": document.document_type,
                "fields_extracted": list(extracted.keys()),
                "ai_provider": "gemini" if settings.GEMINI_API_KEY else "anthropic",
            },
        )
    else:
        document.extraction_status = ExtractionStatus.FAILED.value
        await db.flush()

    return extracted


async def _extract_with_gemini(document: Document, file_data: bytes) -> dict | None:
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = _get_prompt(document.document_type)
        mime = document.mime_type or "application/pdf"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                genai.types.Part.from_bytes(data=file_data, mime_type=mime),
                prompt,
            ],
        )

        return _parse_json_response(response.text)

    except Exception as e:
        logger.error("Gemini extraction failed for %s: %s", document.id, e)
        return None


async def _extract_with_anthropic(document: Document, file_data: bytes) -> dict | None:
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        b64_data = base64.standard_b64encode(file_data).decode("utf-8")
        mime = document.mime_type or "application/pdf"
        prompt = _get_prompt(document.document_type)

        media_type_map = {
            "application/pdf": "application/pdf",
            "image/jpeg": "image/jpeg",
            "image/png": "image/png",
            "image/webp": "image/webp",
        }
        media_type = media_type_map.get(mime, "application/pdf")

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document"
                            if media_type == "application/pdf"
                            else "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return _parse_json_response(message.content[0].text.strip())

    except Exception as e:
        logger.error("Anthropic extraction failed for %s: %s", document.id, e)
        return None


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        logger.warning("Failed to parse JSON from AI response: %s", text[:200])
        return None


CLASSIFY_PROMPT = (
    "Analiza este documento y determina su tipo. Responde UNICAMENTE con un JSON:\n"
    '{"document_type": "<tipo>", "confidence": <0-100>}\n\n'
    "Tipos validos:\n"
    "- constancia_situacion_fiscal (CSF del SAT)\n"
    "- acta_constitutiva (acta notarial de constitucion)\n"
    "- identificacion_representante (INE, pasaporte, ID oficial)\n"
    "- comprobante_domicilio (recibo de luz, agua, telefono, estado de cuenta)\n"
    "- poder_representacion (poder notarial)\n"
    "- manifestacion_protesta (declaracion bajo protesta de decir verdad)\n"
    "- rfc_documento (cedula de identificacion fiscal)\n"
    "- otro (si no coincide con ninguno)\n"
)


async def classify_document(file_data: bytes, mime_type: str) -> dict | None:
    if not settings.GEMINI_API_KEY:
        return None
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                genai.types.Part.from_bytes(data=file_data, mime_type=mime_type),
                CLASSIFY_PROMPT,
            ],
        )
        return _parse_json_response(response.text)
    except Exception as e:
        logger.error("Document classification failed: %s", e)
        return None


SUMMARY_PROMPT = (
    "Eres un oficial de cumplimiento de una agencia aduanal mexicana. "
    "Genera un resumen ejecutivo en español (maximo 3 oraciones) del estado de este expediente KYB. "
    "Incluye: nombre de la empresa, estado en listas fiscales, documentos faltantes, "
    "discrepancias encontradas, y tu recomendacion (aprobar, revisar, o rechazar). "
    "Responde UNICAMENTE con un JSON: {\"resumen\": \"<texto>\", \"recomendacion\": \"<aprobar|revisar|rechazar>\"}"
)


async def generate_dossier_summary(dossier_data: dict) -> dict | None:
    if not settings.GEMINI_API_KEY:
        return None
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        context = json.dumps(dossier_data, ensure_ascii=False, default=str)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[f"{SUMMARY_PROMPT}\n\nDatos del expediente:\n{context}"],
        )
        return _parse_json_response(response.text)
    except Exception as e:
        logger.error("Summary generation failed: %s", e)
        return None
