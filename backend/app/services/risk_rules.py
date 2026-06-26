FISCAL_RULES: dict[str, tuple[int, bool, str]] = {
    "art_69_firmes": (40, True, "Creditos fiscales firmes (Art. 69 CFF)"),
    "art_69_exigibles": (35, False, "Creditos fiscales exigibles (Art. 69 CFF)"),
    "art_69_no_localizados": (50, True, "Contribuyente no localizado (Art. 69 CFF)"),
    "art_69_sentencias": (
        30,
        False,
        "Sentencia condenatoria por delito fiscal (Art. 69 CFF)",
    ),
    "art_69_cancelados": (25, False, "Creditos fiscales cancelados (Art. 69 CFF)"),
    "art_69_csd_sin_efectos": (40, True, "CSD sin efectos (Art. 69 CFF)"),
    "art_69b_bis": (45, True, "Transmision indebida de perdidas (Art. 69-B Bis CFF)"),
}

ART_69B_SITUATION_RULES: dict[str, tuple[str, int, bool, str]] = {
    "Definitivo": (
        "FISCAL_69B_DEFINITIVO",
        50,
        True,
        "EFOS definitivo (Art. 69-B CFF)",
    ),
    "Presunto": ("FISCAL_69B_PRESUNTO", 40, True, "EFOS presunto (Art. 69-B CFF)"),
    "Desvirtuado": (
        "FISCAL_69B_DESVIRTUADO",
        5,
        False,
        "EFOS desvirtuado (Art. 69-B CFF)",
    ),
    "Sentencia Favorable": (
        "FISCAL_69B_SENTENCIA_FAV",
        0,
        False,
        "EFOS con sentencia favorable (Art. 69-B CFF)",
    ),
}

DOC_MISSING_RULES: dict[str, tuple[str, int, str]] = {
    "acta_constitutiva": ("DOC_MISSING_ACTA", 15, "Acta constitutiva faltante"),
    "identificacion_representante": (
        "DOC_MISSING_ID_REP",
        15,
        "Identificacion del representante faltante",
    ),
    "comprobante_domicilio": (
        "DOC_MISSING_COMPROBANTE",
        10,
        "Comprobante de domicilio faltante",
    ),
    "constancia_situacion_fiscal": (
        "DOC_MISSING_CSF",
        20,
        "Constancia de situacion fiscal faltante",
    ),
    "manifestacion_protesta": (
        "DOC_MISSING_MANIFESTACION",
        10,
        "Manifestacion bajo protesta faltante",
    ),
}

DOC_EXPIRED_POINTS: dict[str, int] = {
    "comprobante_domicilio": 20,
    "identificacion_representante": 20,
}

RECON_RULES: dict[str, tuple[str, int, bool, str]] = {
    "rfc": ("RECON_RFC_MISMATCH", 35, True, "Discrepancia de RFC entre documentos"),
    "razon_social": (
        "RECON_RAZON_SOCIAL_MISMATCH",
        30,
        False,
        "Discrepancia de razon social entre documentos",
    ),
    "domicilio": (
        "RECON_DOMICILIO_MISMATCH",
        15,
        False,
        "Discrepancia de domicilio entre documentos",
    ),
    "representante_legal": (
        "RECON_REP_LEGAL_MISMATCH",
        25,
        False,
        "Discrepancia de representante legal entre documentos",
    ),
    "fecha_emision": (
        "RECON_FECHA_EMISION_MISMATCH",
        10,
        False,
        "Discrepancia de fecha de emision entre documentos",
    ),
    "fecha_constitucion": (
        "RECON_FECHA_CONSTITUCION_MISMATCH",
        5,
        False,
        "Discrepancia de fecha de constitucion entre documentos",
    ),
}

SUGGESTED_ACTIONS: dict[str, str] = {
    "FISCAL_69_FIRMES": "Resolver creditos fiscales firmes ante el SAT",
    "FISCAL_69_EXIGIBLES": "Atender creditos fiscales exigibles",
    "FISCAL_69_NO_LOCALIZADOS": "Actualizar domicilio fiscal ante el SAT",
    "FISCAL_69_SENTENCIAS": "Revisar situacion legal del contribuyente",
    "FISCAL_69_CANCELADOS": "Verificar estado de creditos cancelados",
    "FISCAL_69_CSD_SIN_EFECTOS": "Regularizar CSD ante el SAT",
    "FISCAL_69B_DEFINITIVO": "CRITICO: Contribuyente en lista de EFOS definitivos. No operar.",
    "FISCAL_69B_PRESUNTO": "Verificar situacion de EFOS presunto urgentemente",
    "FISCAL_69B_DESVIRTUADO": "Documentar evidencia de desvirtuacion de EFOS",
    "FISCAL_69B_BIS": "Revisar operacion por transmision indebida de perdidas",
    "FISCAL_49BIS": "Verificar operaciones con contribuyentes EFOS (Art. 49 Bis CFF)",
    "FISCAL_CHECK_STALE": "Actualizar consulta de listas fiscales del SAT",
    "FISCAL_NEVER_CHECKED": "Ejecutar consulta de listas fiscales del SAT",
    "DOC_MISSING_ACTA": "Cargar acta constitutiva",
    "DOC_MISSING_ID_REP": "Cargar identificacion del representante legal",
    "DOC_MISSING_COMPROBANTE": "Cargar comprobante de domicilio vigente",
    "DOC_MISSING_CSF": "Cargar constancia de situacion fiscal del mes actual",
    "DOC_MISSING_MANIFESTACION": "Cargar manifestacion bajo protesta de decir verdad",
    "DOC_EXPIRED": "Actualizar documento vencido",
    "CSF_NOT_CURRENT_MONTH": "Obtener constancia de situacion fiscal del mes vigente",
    "RECON_RFC_MISMATCH": "CRITICO: Corregir discrepancia de RFC entre documentos",
    "RECON_RAZON_SOCIAL_MISMATCH": "Corregir razon social para que coincida entre documentos",
    "RECON_DOMICILIO_MISMATCH": "Verificar y corregir domicilio entre documentos",
    "RECON_REP_LEGAL_MISMATCH": "Verificar datos del representante legal entre documentos",
    "COMP_NO_REP_LEGAL": "Registrar representante legal del expediente",
    "COMP_NO_SHAREHOLDERS": "Registrar socios o accionistas",
    "COMP_RFC_MISSING": "Registrar RFC de la persona moral",
    "RECON_FECHA_EMISION_MISMATCH": "Verificar fechas de emision entre documentos",
    "RECON_FECHA_CONSTITUCION_MISMATCH": "Verificar fecha de constitucion en el acta",
}
