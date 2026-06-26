import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, ExtractionStatus
from app.services.ai_providers import (
    call_text_ai,
    extract_with_anthropic,
    extract_with_gemini,
    extract_with_groq,
)
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)

# EXTRACCION AI: prompts por tipo de documento.
# La AI devuelve JSON con campos clave.
# Alimentan la conciliacion (RFC, razon social, domicilio, etc).
EXTRACTION_PROMPTS: dict[str, str] = {
    "constancia_situacion_fiscal": (
        "Extrae los siguientes datos de esta Constancia de"
        " Situacion Fiscal (CSF) del SAT. "
        "Responde UNICAMENTE con un JSON valido,"
        " sin explicaciones:\n"
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
        "Extrae los siguientes datos de este poder notarial"
        " o evidencia de representacion. "
        "Responde UNICAMENTE con un JSON valido,"
        " sin explicaciones:\n"
        '{"representante_legal": "", "tipo_poder": "", '
        '"fecha_otorgamiento": "", "notario": "", "numero_escritura": ""}'
    ),
    "manifestacion_protesta": (
        "Extrae los siguientes datos de esta manifestacion"
        " bajo protesta de decir verdad. "
        "Responde UNICAMENTE con un JSON valido,"
        " sin explicaciones:\n"
        '{"declarante": "", "fecha": "", "contenido_resumen": ""}'
    ),
}

DEFAULT_PROMPT = (
    "Extrae todos los datos relevantes de este documento. "
    "Responde UNICAMENTE con un JSON valido con los campos que identifiques."
)


def _get_prompt(document_type: str) -> str:
    return EXTRACTION_PROMPTS.get(document_type, DEFAULT_PROMPT)


# FALLBACK MULTI-MODELO: Gemini -> Groq -> Claude. Si uno falla, el siguiente responde.
_PROVIDERS: list[tuple[str, object]] = []


def _init_providers():
    global _PROVIDERS
    _PROVIDERS = []
    if settings.GEMINI_API_KEY:
        _PROVIDERS.append(("gemini", extract_with_gemini))
    if settings.GROQ_API_KEY:
        _PROVIDERS.append(("groq", extract_with_groq))
    if settings.ANTHROPIC_API_KEY:
        _PROVIDERS.append(("anthropic", extract_with_anthropic))


def _extract_pdf_text(file_data: bytes, mime: str) -> str | None:
    from app.utils.pdf_extractor import extract_text_from_pdf

    if mime != "application/pdf":
        return None
    text = extract_text_from_pdf(file_data)
    if text:
        logger.info(
            "PDF text extracted locally (%d chars), sending text to AI",
            len(text),
        )
    return text


async def _try_providers(
    prompt: str, file_data: bytes, mime: str, pdf_text: str | None
):
    for provider_name, provider_fn in _PROVIDERS:
        try:
            if pdf_text:
                full_prompt = f"{prompt}\n\nTexto del documento:\n{pdf_text[:4000]}"
                extracted = await call_text_ai(full_prompt)
            else:
                extracted = await provider_fn(prompt, file_data, mime)
            if extracted:
                return extracted, provider_name
            logger.warning("Provider %s returned no data, trying next", provider_name)
        except Exception as e:
            logger.warning("Provider %s failed: %s, trying next", provider_name, e)
    return None, None


async def extract_document_data(
    db: AsyncSession,
    document: Document,
    file_data: bytes,
) -> dict | None:
    document.extraction_status = ExtractionStatus.PROCESSING.value
    await db.flush()

    if not _PROVIDERS:
        _init_providers()
    if not _PROVIDERS:
        logger.warning("No AI API key configured, skipping extraction")
        document.extraction_status = ExtractionStatus.FAILED.value
        await db.flush()
        return None

    mime = document.mime_type or "application/pdf"
    pdf_text = _extract_pdf_text(file_data, mime)
    prompt = _get_prompt(document.document_type)

    extracted, provider_used = await _try_providers(prompt, file_data, mime, pdf_text)

    if extracted and provider_used:
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
                "ai_provider": provider_used,
                "used_local_text": bool(pdf_text),
            },
        )
    else:
        document.extraction_status = ExtractionStatus.FAILED.value
        await db.flush()

    return extracted
