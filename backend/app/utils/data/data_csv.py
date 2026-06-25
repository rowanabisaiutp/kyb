# LISTAS FISCALES del SAT: URLs reales de Azure Blob. Sin mocks.
# 9 listas cubriendo Art. 69 (6 tipos), Art. 69-B (EFOS), Art. 69-B Bis, Art. 49 Bis CFF.
# Se descargan al iniciar la app y se indexan en memoria para busqueda O(1) por RFC.
#
# Fuentes oficiales:
#   - Datos abiertos SAT: https://www.sat.gob.mx/minisitio/DatosAbiertos/contribuyentes_publicados.html
#   - Incumplidos (Art. 69): https://wwwmat.sat.gob.mx/consultas/11981/consulta-la-relacion-de-contribuyentes-incumplidos
#   - EFOS (Art. 69-B): https://wwwmat.sat.gob.mx/consultas/76674/consulta-la-relacion-de-contribuyentes-con-operaciones-presuntamente-inexistentes
#   - Regla 1.4.14 RGCE 2026: https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/rgce/1raRMRGCEpara2026.pdf
#   - Portal SAT PLD: https://sppld.sat.gob.mx/pld/interiores/obligaciones.html
SAT_LISTS = {
    # --- Art. 69 CFF (excepto fraccion VI) - 6 listados ---
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
    # --- Art. 69-B CFF - EFOS (Definitivo/Presunto/Desvirtuado/Sentencia Favorable) ---
    "art_69b": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv",
        "article": "69-B CFF",
        "description": "Operaciones presuntamente inexistentes (EFOS) - listado completo",
    },
    # --- Art. 69-B Bis CFF - transmision indebida de perdidas fiscales ---
    "art_69b_bis": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_Completo.csv",
        "article": "69-B Bis CFF",
        "description": "Transmision indebida de perdidas fiscales",
    },
    # --- Art. 49 Bis CFF - no hay CSV propio; usa fuente 69-B (justificado en SAT_FUENTES.md) ---
    "art_49bis": {
        "url": "https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv",
        "article": "49 Bis CFF",
        "description": "Operaciones con EFOS (fuente: listado Art. 69-B, unica base publica disponible del SAT)",
    },
}
