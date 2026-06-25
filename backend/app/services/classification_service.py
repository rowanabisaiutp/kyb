from app.services.ai_providers import call_text_ai

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
            return await call_text_ai(
                f"{CLASSIFY_PROMPT}\n\nTexto del documento:\n{text[:2000]}"
            )

    return await call_text_ai(CLASSIFY_PROMPT, file_data=file_data, mime_type=mime_type)
