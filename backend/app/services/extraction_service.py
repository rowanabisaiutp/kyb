import base64
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, ExtractionStatus
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)

# EXTRACCION AI: prompts por tipo de documento. La AI devuelve JSON con campos clave.
# Los datos extraidos alimentan la conciliacion (RFC, razon social, domicilio, rep legal, fechas).
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


# FALLBACK MULTI-MODELO: Gemini -> Groq -> Claude. Si uno falla, el siguiente responde.
AI_PROVIDERS = []


def _init_providers():
    global AI_PROVIDERS
    AI_PROVIDERS = []
    if settings.GEMINI_API_KEY:
        AI_PROVIDERS.append(("gemini", _extract_with_gemini))
    if settings.GROQ_API_KEY:
        AI_PROVIDERS.append(("groq", _extract_with_groq))
    if settings.ANTHROPIC_API_KEY:
        AI_PROVIDERS.append(("anthropic", _extract_with_anthropic))


async def extract_document_data(
    db: AsyncSession,
    document: Document,
    file_data: bytes,
) -> dict | None:
    document.extraction_status = ExtractionStatus.PROCESSING.value
    await db.flush()

    if not AI_PROVIDERS:
        _init_providers()

    if not AI_PROVIDERS:
        logger.warning("No AI API key configured, skipping extraction")
        document.extraction_status = ExtractionStatus.FAILED.value
        await db.flush()
        return None

    # Paso 1: extrae texto del PDF localmente con PyMuPDF (gratis, sin quota AI).
    from app.utils.pdf_extractor import extract_text_from_pdf

    pdf_text = None
    mime = document.mime_type or "application/pdf"
    if mime == "application/pdf":
        pdf_text = extract_text_from_pdf(file_data)
        if pdf_text:
            logger.info(
                "PDF text extracted locally (%d chars), sending text to AI",
                len(pdf_text),
            )

    # Paso 2: envia texto (o archivo completo) a AI con fallback entre proveedores.
    extracted = None
    provider_used = None

    for provider_name, provider_fn in AI_PROVIDERS:
        try:
            if pdf_text:
                extracted = await _extract_from_text(
                    provider_name, document.document_type, pdf_text
                )
            else:
                extracted = await provider_fn(document, file_data)
            if extracted:
                provider_used = provider_name
                break
            logger.warning("Provider %s returned no data, trying next", provider_name)
        except Exception as e:
            logger.warning("Provider %s failed: %s, trying next", provider_name, e)
            continue

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


async def _extract_from_text(
    provider_name: str, document_type: str, text: str
) -> dict | None:
    prompt = _get_prompt(document_type)
    full_prompt = f"{prompt}\n\nTexto del documento:\n{text[:4000]}"
    return await _call_text_ai_with_fallback(full_prompt)


async def _extract_with_gemini(document: Document, file_data: bytes) -> dict | None:
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = _get_prompt(document.document_type)
        mime = document.mime_type or "application/pdf"

        response = client.models.generate_content(
            model="gemini-2.0-flash",
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


async def _extract_with_groq(document: Document, file_data: bytes) -> dict | None:
    try:
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        prompt = _get_prompt(document.document_type)
        b64_data = base64.standard_b64encode(file_data).decode("utf-8")
        mime = document.mime_type or "application/pdf"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64_data}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        response = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=messages,
            max_tokens=2048,
        )

        return _parse_json_response(response.choices[0].message.content)

    except Exception as e:
        logger.error("Groq extraction failed for %s: %s", document.id, e)
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
    from app.utils.pdf_extractor import extract_text_from_pdf

    if mime_type == "application/pdf":
        text = extract_text_from_pdf(file_data)
        if text:
            return await _call_text_ai_with_fallback(
                f"{CLASSIFY_PROMPT}\n\nTexto del documento:\n{text[:2000]}"
            )

    return await _call_text_ai_with_fallback(
        CLASSIFY_PROMPT, file_data=file_data, mime_type=mime_type
    )


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
    return await _call_text_ai_with_fallback(prompt)


async def _call_text_ai_with_fallback(
    prompt: str,
    file_data: bytes | None = None,
    mime_type: str = "application/pdf",
) -> dict | None:
    providers = []
    if settings.GEMINI_API_KEY:
        providers.append(("gemini", _gemini_text_call))
    if settings.GROQ_API_KEY:
        providers.append(("groq", _groq_text_call))

    for name, fn in providers:
        try:
            result = await fn(prompt, file_data, mime_type)
            if result:
                return result
        except Exception as e:
            logger.warning("Text AI provider %s failed: %s, trying next", name, e)
            continue

    return None


async def _gemini_text_call(
    prompt: str, file_data: bytes | None, mime_type: str
) -> dict | None:
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    contents = []
    if file_data:
        contents.append(
            genai.types.Part.from_bytes(data=file_data, mime_type=mime_type)
        )
    contents.append(prompt)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=contents
    )
    return _parse_json_response(response.text)


async def _groq_text_call(
    prompt: str, file_data: bytes | None, mime_type: str
) -> dict | None:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    messages_content = []

    if file_data:
        b64 = base64.standard_b64encode(file_data).decode("utf-8")
        messages_content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
            }
        )
    messages_content.append({"type": "text", "text": prompt})

    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview"
        if file_data
        else "llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": messages_content}],
        max_tokens=2048,
    )
    return _parse_json_response(response.choices[0].message.content)
