# Fuentes SAT — Listas Fiscales Públicas

Archivos CSV descargables directamente desde el portal de datos abiertos del SAT.
Actualizados entre marzo y abril de 2026.

---

## Art. 69 CFF — Contribuyentes con créditos fiscales

Contribuyentes con adeudos firmes, exigibles, no localizados, cancelados o con sentencia condenatoria por delito fiscal.

| Listado | Link |
|---|---|
| Cancelados | [Cancelados.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Cancelados.csv) |
| Exigibles | [Exigibles.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Exigibles.csv) |
| Firmes | [Firmes.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Firmes.csv) |
| No localizados | [No_localizados.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/No_localizados.csv) |
| Sentencias | [Sentencias.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/Sentencias.csv) |
| CSD sin efectos | [CSDsinefectos.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/CSDsinefectos.csv) |
| Entes públicos omisos | [EntespublicosydeGobiernoomisos.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/EntespublicosydeGobiernoomisos.csv) |
| Reducción de multas (Art. 74) | [ReduccionArt74CFF.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGR/ReduccionArt74CFF.csv) |

---

## Art. 69-B CFF — Empresas Fantasma (EFOS)

Contribuyentes que emitieron comprobantes sin contar con activos, personal o infraestructura real para respaldar las operaciones facturadas.

| Listado | Link |
|---|---|
| Listado completo | [Listado_completo_69-B.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Listado_completo_69-B.csv) |
| Definitivos | [Definitivos.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Definitivos.csv) |
| Presuntos | [Presuntos.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Presuntos.csv) |
| Desvirtuados | [Desvirtuados.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/Desvirtuados.csv) |
| Sentencias favorables | [SentenciasFavorables.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGAFF/SentenciasFavorables.csv) |

---

## Art. 69-B Bis CFF — Transmisión Indebida de Pérdidas

Contribuyentes que transmitieron el derecho a disminuir pérdidas fiscales mediante reestructuras, escisiones, fusiones o cambios de accionistas de forma irregular.

| Listado | Link |
|---|---|
| Listado completo | [Listado_69_B_Bis_Completo.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_Completo.csv) |
| Definitivos | [Listado_69_B_Bis_Definitivo.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_Definitivo.csv) |
| Sentencias favorables | [Listado_69_B_Bis_SentenciaFa.csv](https://wu1agsprosta001.blob.core.windows.net/agsc-publicaciones/Datos_abiertos/Documents_AGGC/Listado_69_B_Bis_SentenciaFa.csv) |

---

## Art. 49 Bis CFF — Verificación Exprés

No existe lista pública descargable. Este artículo define un procedimiento de auditoría interna del SAT (visita domiciliaria exprés en 24 días hábiles). Los contribuyentes sancionados son publicados en el DOF y quedan reflejados en las listas de Art. 69-B definitivos.

Consulta manual: [DOF — Diario Oficial de la Federación](https://www.dof.gob.mx)

---

## Fuentes oficiales

| Fuente | URL |
|---|---|
| Regla 1.4.14 RGCE 2026 | https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/rgce/1raRMRGCEpara2026.pdf |
| Datos abiertos SAT (CSVs) | https://www.sat.gob.mx/minisitio/DatosAbiertos/contribuyentes_publicados.html |
| Contribuyentes incumplidos (Art. 69 CFF) | https://wwwmat.sat.gob.mx/consultas/11981/consulta-la-relacion-de-contribuyentes-incumplidos |
| Operaciones presuntamente inexistentes (Art. 69-B CFF) | https://wwwmat.sat.gob.mx/consultas/76674/consulta-la-relacion-de-contribuyentes-con-operaciones-presuntamente-inexistentes |
| Portal SAT PLD (obligaciones) | https://sppld.sat.gob.mx/pld/interiores/obligaciones.html |

### Nota sobre Portal SAT PLD

El portal PLD no ofrece CSVs, APIs ni listas descargables. Es un portal informativo que define
las obligaciones de Actividades Vulnerables bajo la Ley Federal PLD/FT:

1. **Alta/Registro** ante el SAT previo al primer Aviso.
2. **Identificacion de clientes** — verificar identidad con documentos oficiales y obtener informacion
   sobre actividad y beneficiarios reales (implementado en el expediente KYB de esta plataforma).
3. **Reportes a la UIF** — proporcionar informacion de operaciones a mas tardar el dia 17 del mes siguiente.
4. **Custodia de registros** — conservar documentacion fisica o electronica por 5 años
   (implementado via audit log y almacenamiento persistente de documentos).

Tambien publica las Evaluaciones Nacionales de Riesgos (2016, 2020, 2023) en PDF.
| DOF — Diario Oficial de la Federación | https://www.dof.gob.mx |
