# Req: Listas fiscales publicas del SAT (Art. 69, 69-B, 69-B Bis, 49 Bis CFF). Datos reales, sin mocks.
SAT_LISTS = {
    # Art. 69 CFF (excepto fraccion VI) - contribuyentes incumplidos
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
    # Art. 69-B CFF - EFOS (operaciones presuntamente inexistentes)
    "art_69b": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv",
        "article": "69-B CFF",
        "description": "Operaciones presuntamente inexistentes (EFOS) - listado completo",
    },
    # Art. 69-B Bis CFF - transmision indebida de perdidas fiscales
    "art_69b_bis": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_Completo.csv",
        "article": "69-B Bis CFF",
        "description": "Transmision indebida de perdidas fiscales",
    },
    # Art. 49 Bis CFF - usa misma fuente 69-B (unica base publica SAT disponible)
    "art_49bis": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv",
        "article": "49 Bis CFF",
        "description": "Operaciones con EFOS (fuente: listado Art. 69-B, unica base publica disponible del SAT)",
    },
}
