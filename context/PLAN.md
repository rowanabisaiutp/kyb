# Plan: Plataforma KYB para Agencia Aduanal

## Contexto

Plataforma web KYB para agencia aduanal. Determina si una persona moral mexicana es segura, requiere revision o es riesgosa para operar comercio exterior (Regla 1.4.14 RGCE 2026).

**Estado actual:** Fases 1-7 completadas. Faltan: Fase 8 (UI + aprobacion), Fase 9 (deploy), Fase 10 (testing).

---

## FASE 1: Fundacion Backend — COMPLETADA

> Config, DB, modelos, CRUD, audit log. Todo verificado con tests.

### Archivos backend creados:

```
backend/
  main.py                              # App factory, lifespan (crea tablas), CORS, monta routers
  requirements.txt                     # fastapi, sqlalchemy[asyncio], aiosqlite, asyncpg, alembic,
                                       # pydantic-settings, python-multipart, boto3, anthropic,
                                       # httpx, python-dateutil, unidecode
  app/
    __init__.py
    config.py                          # Settings via pydantic-settings
                                       #   DATABASE_URL (sqlite dev / postgresql prod)
                                       #   ANTHROPIC_API_KEY, AWS_*, BUCKET_NAME, APP_ENV
                                       #   @property async_database_url: auto-convierte postgres -> asyncpg
    database.py                        # create_async_engine + async_sessionmaker
    dependencies.py                    # get_db() -> AsyncSession (FastAPI Depends)

    models/
      __init__.py                      # Re-exporta todos los modelos + Base
      base.py                          # Base (DeclarativeBase), TimestampMixin, UUIDMixin
      entity.py                        # LegalEntity (rfc unique, razon_social, domicilio, etc.)
                                       # LegalRepresentative (nombre, curp, rfc_pf, cargo, vigente)
                                       # Shareholder (nombre, rfc, porcentaje, tipo)
                                       # Relaciones: entity -> representatives[], shareholders[], dossiers[]
      dossier.py                       # DossierStatus enum (draft|in_review|safe|review_required|
                                       #   high_risk|needs_update|approved|rejected)
                                       # Dossier (entity_id FK, status, risk_score, classification,
                                       #   approved_by/at, notes)
                                       # Relaciones: dossier -> documents[], fiscal_checks[],
                                       #   risk_assessments[], reconciliation_results[]
      document.py                      # DocumentType enum (acta_constitutiva, identificacion_representante,
                                       #   poder_representacion, comprobante_domicilio,
                                       #   constancia_situacion_fiscal, manifestacion_protesta,
                                       #   rfc_documento, otro)
                                       # ExtractionStatus enum (pending|processing|completed|failed)
                                       # Document (dossier_id FK, file_name/key/size/mime, fechas,
                                       #   extracted_data JSON, extraction_status)
      fiscal_check.py                  # FiscalListCheck (dossier_id FK, rfc_searched, list_type,
                                       #   source_url, checked_at, found, result_detail JSON)
      risk.py                          # RiskAssessment (dossier_id FK, total_score, classification,
                                       #   factors JSON, blocks_approval, suggested_actions JSON)
      reconciliation.py                # ReconciliationResult (dossier_id FK, field_name, source_a/b,
                                       #   value_a/b, match, severity)
      audit.py                         # AuditLog (dossier_id FK nullable, entity_id FK nullable,
                                       #   action, actor, details JSON, ip_address)
                                       # Indices: dossier_id, action, created_at

    schemas/
      __init__.py
      common.py                        # UUIDResponse, TimestampResponse, PaginatedRequest,
                                       #   ErrorResponse, MessageResponse
      entity.py                        # EntityCreate (con representatives[] y shareholders[] inline)
                                       # EntityUpdate (campos opcionales)
                                       # EntityResponse (con from_attributes, incluye reps y shareholders)
                                       # EntityListResponse (resumen: id, rfc, razon_social)
                                       # LegalRepresentativeCreate/Response
                                       # ShareholderCreate/Response (tipo validado con regex)
      dossier.py                       # DossierCreate (entity_id, notes)
                                       # DossierStatusUpdate (status validado con regex, approved_by)
                                       # DossierResponse (incluye entity joinada)
                                       # DossierListResponse
      audit.py                         # AuditLogResponse

    services/
      __init__.py
      audit_service.py                 # log_action(db, action, dossier_id?, entity_id?, actor, details)
                                       #   -> crea AuditLog y flush (se commitea con la transaccion padre)

    routers/
      __init__.py
      health.py                        # GET /health -> SELECT 1 contra DB
      entities.py                      # POST /entities (con reps y shareholders inline, RFC unique 409)
                                       # GET /entities (paginado, search por rfc/razon_social)
                                       # GET /entities/{id} (con selectinload reps + shareholders)
                                       # PUT /entities/{id} (update parcial)
                                       # POST /entities/{id}/representatives
                                       # POST /entities/{id}/shareholders
      dossiers.py                      # POST /dossiers (valida entity existe)
                                       # GET /dossiers (paginado, filtro por status, search)
                                       # GET /dossiers/stats (count por status)
                                       # GET /dossiers/{id} (con entity joinada)
                                       # PATCH /dossiers/{id}/status (transiciones validadas,
                                       #   bloquea approve si high_risk)
      audit.py                         # GET /audit-log (global, paginado, filtro por action)
                                       # GET /dossiers/{id}/audit-log (por dossier)

    utils/
      __init__.py
```

### Transiciones de estado validadas:
```
draft -> in_review
in_review -> approved | rejected | needs_update
safe -> approved | needs_update
review_required -> approved | rejected | needs_update
high_risk -> rejected | needs_update (NO puede aprobarse)
needs_update -> in_review
approved -> needs_update
rejected -> in_review | needs_update
```

### Verificacion (completada):
- Health: 200, Entity create: 201 (con reps+shareholders), Dossier create: 201
- Dossier list con entity join, Stats por status, Audit log con entries
- Status transition draft->in_review: 200, RFC duplicado: 409, Transicion invalida: 422

---

## FASE 2: Fundacion Frontend — COMPLETADA

> Layout, routing, paginas, API client, hooks, UI reutilizables. Build verificado.

### Archivos frontend creados:

```
frontend/
  vite.config.ts                         # Vite 6 + react plugin + proxy /api -> localhost:8000
  postcss.config.js                      # @tailwindcss/postcss (Tailwind v4 via PostCSS)

  src/
    main.tsx                             # QueryClientProvider (staleTime: 30s, retry: 1)
                                         # StrictMode + createRoot
    App.tsx                              # BrowserRouter + Routes dentro de AppLayout
                                         #   / -> DashboardPage
                                         #   /dossiers -> DossierListPage
                                         #   /dossiers/new -> DossierCreatePage
                                         #   /dossiers/:id -> DossierDetailPage
                                         #   * -> NotFoundPage
    index.css                            # @import "tailwindcss" + @theme con colores custom
                                         #   primary, safe, warning, danger, neutral,
                                         #   surface, border, text, text-secondary

    types/
      index.ts                           # 14 interfaces + 3 payloads:
                                         #   Entity, EntityListItem, EntityCreatePayload
                                         #   LegalRepresentative, Shareholder
                                         #   Dossier, DossierCreatePayload, DossierStatusUpdatePayload
                                         #   DossierStatus (8 valores), RiskClassification (3 valores)
                                         #   DocumentType (8 valores), ExtractionStatus (4 valores)
                                         #   Document, FiscalListCheck, RiskFactor, RiskAssessment
                                         #   ReconciliationResult, AuditLogEntry

    api/
      client.ts                          # axios.create({ baseURL: "/api/v1" })
      entities.ts                        # listEntities(search?), getEntity(id),
                                         #   createEntity(payload), updateEntity(id, payload)
      dossiers.ts                        # listDossiers({status?, search?}), getDossier(id),
                                         #   createDossier(payload), updateDossierStatus(id, payload),
                                         #   getDossierStats()

    hooks/
      useDossiers.ts                     # useDossiers(params?) - lista con filtros
                                         # useDossierStats() - conteo por status
                                         # useCreateDossier() - mutation + invalidate cache
      useDossier.ts                      # useDossier(id) - detalle con enabled check
                                         # useUpdateDossierStatus(id) - mutation + invalidate

    utils/
      formatDate.ts                      # formatDate(iso) -> dd/MM/yyyy (locale es)
                                         # formatDateTime(iso) -> dd/MM/yyyy HH:mm
                                         # formatRelative(iso) -> "hace 2 horas"
      formatRfc.ts                       # formatRfc(rfc), isValidRfcFormat(rfc) -> regex
      riskColors.ts                      # getRiskColor/getRiskBg/getRiskLabel(classification)
                                         # getScoreColor(score) -> color por umbral
      statusLabels.ts                    # DOSSIER_STATUS_LABELS (8 estados en español)
                                         # DOSSIER_STATUS_COLORS (clases Tailwind por estado)
                                         # DOCUMENT_TYPE_LABELS (8 tipos en español)
                                         # REQUIRED_DOCUMENTS (5 tipos obligatorios)

    components/
      layout/
        AppLayout.tsx                    # flex min-h-screen: Sidebar + <Outlet />
        Sidebar.tsx                      # Logo KYB + nav items con iconos lucide
                                         #   Dashboard (/), Expedientes (/dossiers)
                                         #   Active state con pathname matching
        Header.tsx                       # titulo + descripcion + action slot

      ui/
        Button.tsx                       # variants: primary|secondary|danger|ghost
                                         # sizes: sm|md|lg, loading state con spinner
        Card.tsx                         # Card + CardHeader + CardTitle
        Badge.tsx                        # inline-flex rounded-full con className custom
        Input.tsx                        # label + error + estilos focus/disabled
        Select.tsx                       # label + options[] con estilos consistentes
        StatusBadge.tsx                  # DossierStatus -> Badge con color mapeado
        LoadingSpinner.tsx               # SVG animate-spin, sizes sm|md|lg
        EmptyState.tsx                   # Icono FileX + titulo + descripcion + action slot

    pages/
      DashboardPage.tsx                  # 4 stat cards (draft, in_review, approved, high_risk)
                                         # Lista de expedientes recientes (top 10)
                                         # Boton "Nuevo Expediente" en header
      DossierListPage.tsx                # Buscador por RFC/razon social + filtro por status
                                         # Lista de cards con entidad, score, status, fecha
                                         # EmptyState cuando no hay resultados
      DossierCreatePage.tsx              # Form: datos persona moral (rfc, razon_social, etc.)
                                         # + representante legal (nombre, cargo, curp)
                                         # -> createEntity() + createDossier() + navigate
                                         # Manejo de errores con mensaje visible
      DossierDetailPage.tsx              # Info general: status, score, fechas, aprobacion
                                         # Entidad sidebar: razon social, RFC
                                         # Placeholders para: Documentos (F3), Fiscal (F5)
      NotFoundPage.tsx                   # EmptyState + link al dashboard
```

### Dependencias instaladas:
```
react-router-dom, @tanstack/react-query, axios,
tailwindcss, @tailwindcss/postcss, postcss,
lucide-react, react-dropzone, date-fns
```

### Nota tecnica:
Vite downgradeado de v8 a v6 por incompatibilidad de rolldown con Application Control en Windows.
Tailwind v4 integrado via PostCSS en lugar de `@tailwindcss/vite`.

### Verificacion (completada):
- `npm run build` exitoso (6.29s, 376KB JS + 19KB CSS gzip)
- `npm run dev` arranca en localhost:5173
- Proxy `/api` configurado hacia backend en localhost:8000

---

## FASE 3: Documentos + Storage — COMPLETADA

> Upload de archivos a Tigris S3, metadata en DB, UI de documentos.

### Archivos backend creados:
```
backend/app/
  utils/
    rfc_validator.py                   # is_valid_rfc(rfc) regex, normalize_rfc(rfc)
  services/
    storage_service.py                 # S3/Tigris: upload_file, get_presigned_url, delete_file
                                       # validate_file (MIME: pdf/jpeg/png/webp, max 10MB)
                                       # generate_file_key (dossiers/{id}/{type}/{uuid}.ext)
                                       # Retorna False sin S3 configurado (dev local OK)
    document_service.py                # upload_document (valida + S3 + metadata + audit log)
                                       # list_documents, get_document, delete_document
                                       # get_missing_documents (5 docs requeridos)
  schemas/
    document.py                        # DocumentResponse, DocumentListResponse
                                       # MissingDocumentsResponse (missing[], total_required, total_present)
  routers/
    documents.py                       # POST /dossiers/{id}/documents (upload multipart)
                                       # GET /dossiers/{id}/documents (list)
                                       # GET /dossiers/{id}/documents/checklist (docs faltantes)
                                       # GET /documents/{id} (detalle)
                                       # GET /documents/{id}/download (presigned URL)
                                       # DELETE /documents/{id}
```

### Archivos frontend creados:
```
frontend/src/
  api/documents.ts                     # listDocuments, uploadDocument (FormData),
                                       # getDocument, deleteDocument, getDocumentChecklist
  hooks/useDocuments.ts                # useDocuments, useDocumentChecklist,
                                       # useUploadDocument, useDeleteDocument (cache invalidation)
  components/
    documents/
      DocumentUploadZone.tsx           # Drag-drop react-dropzone, selector tipo, preview archivo
      DocumentCard.tsx                 # Nombre, tipo, tamano, fechas, badge vencido,
                                       # datos extraidos preview, boton eliminar
      ExtractionStatus.tsx             # Badge por estado (pending|processing|completed|failed)
    dossier/
      DocumentChecklist.tsx            # Progress bar + 5 docs requeridos con check/circle
  pages/
    DossierDetailPage.tsx              # Actualizado con tabs funcionales + DocumentsTab integrado
```

### Verificacion (completada):
- Upload 201, list 200, checklist con missing docs, get por id, tipo invalido 400
- Delete 204, audit log con document.uploaded + document.deleted
- Frontend build exitoso

---

## FASE 4: Extraccion con Claude API — COMPLETADA

> Extraccion automatica de datos de documentos con Claude API.

### Archivos creados/modificados:
```
backend/app/
  services/
    extraction_service.py              # extract_document_data(db, document, file_data)
                                       # Prompts por tipo de documento:
                                       #   CSF: rfc, razon_social, domicilio_fiscal, codigo_postal,
                                       #        regimen_fiscal, fecha_emision
                                       #   Acta: razon_social, rfc, fecha_constitucion, objeto_social,
                                       #         socios[], representante_legal, notario
                                       #   ID: nombre_completo, curp, fecha_nacimiento,
                                       #       fecha_vencimiento, tipo_identificacion
                                       #   Comprobante: direccion_completa, fecha_emision, tipo
                                       #   Poder: representante_legal, tipo_poder, fecha, notario
                                       # Modelo: claude-sonnet-4-20250514
                                       # _parse_json_response: maneja markdown fences, JSON parcial
                                       # _media_type_for_api: pdf/jpeg/png/webp
                                       # Falla gracefully sin API key (status: failed, no rompe upload)
  routers/
    documents.py                       # Modificado: trigger extraccion post-upload automatico
                                       # Nuevo: POST /documents/{id}/extract (re-extraccion manual)
```

### Configuracion:
- `.env` con ANTHROPIC_API_KEY configurada
- Extraccion sincrona: se ejecuta durante el upload, resultado inmediato
- Audit log: extraction.completed / extraction.failed

### Verificacion (completada):
- Upload + extraccion sin API key: status failed, upload no se rompe (201)
- Upload con API key: extraccion automatica post-upload
- Re-extraccion manual via POST /documents/{id}/extract
- Audit log registra eventos de extraccion

---

## FASE 5: Listas Fiscales SAT — COMPLETADA

> Descarga de CSVs reales del SAT, parseo en memoria, busqueda O(1) por RFC.

### Archivos backend creados:
```
backend/app/
  utils/
    csv_parser.py                      # SAT_LISTS: 8 listas con URLs reales de Azure Blob
                                       #   art_69: cancelados, exigibles, firmes, no_localizados,
                                       #           sentencias, csd_sin_efectos
                                       #   art_69b: listado completo EFOS
                                       #   art_69b_bis: transmision indebida de perdidas
                                       # download_and_parse_csv(list_key) -> dict[rfc, rows]
                                       # load_all_lists() -> descarga las 8 listas async con httpx
                                       # search_rfc(all_lists, rfc) -> resultados por lista
                                       # _find_rfc_column: busca columna RFC en headers
  services/
    fiscal_service.py                  # Estado global: _fiscal_lists, _last_loaded
                                       # set_loaded_lists / get_loaded_lists / get_lists_status
                                       # check_rfc_in_lists(db, dossier_id, rfc)
                                       #   -> busca en todas las listas, guarda FiscalListCheck por cada una
                                       #   -> audit log con conteo de matches
  schemas/
    fiscal.py                          # FiscalCheckResponse, FiscalCheckSummary (con clean boolean)
                                       # FiscalListsStatus
  routers/
    fiscal.py                          # POST /dossiers/{id}/fiscal-check (busca RFC en 8 listas)
                                       # GET /dossiers/{id}/fiscal-checks (historial)
                                       # GET /fiscal-lists/status (estado de carga)
  main.py                             # Modificado: carga listas en background al iniciar
                                       #   asyncio.create_task(_load_fiscal_lists())
                                       #   No bloquea el startup del servidor
```

### Archivos frontend creados:
```
frontend/src/
  api/fiscal.ts                        # runFiscalCheck, listFiscalChecks, getFiscalListsStatus
  hooks/useFiscalCheck.ts              # useFiscalChecks, useRunFiscalCheck, useFiscalListsStatus
  components/fiscal/
    FiscalCheckResults.tsx             # Resumen limpio/encontrado con icono
                                       # Lista de 8 checks con badge verde/rojo por lista
                                       # Labels en español por tipo de lista
                                       # Boton "Consultar Listas" / "Consultar de Nuevo"
    FiscalListBadge.tsx                # Badge: Encontrado (rojo) / Limpio (verde)
  pages/
    DossierDetailPage.tsx              # Tab Fiscal integrado con FiscalTab funcional
```

### Art. 49 Bis:
No hay CSV publico del SAT. Documentado en SAT_FUENTES.md. Los contribuyentes
sancionados se reflejan en Art. 69-B Definitivos (ya consultado).

### Verificacion (completada):
- Status 200: loaded true, 8 listas
- Fiscal check con RFC en listas: 2 matches (cancelados + 69b), clean: false
- RFC limpio: 0 matches, clean: true
- Historial guardado, audit log con fiscal.checked

---

## FASE 6: Conciliacion de Datos — COMPLETADA

> Cruce de datos extraidos entre documentos y formulario, deteccion de discrepancias.

### Archivos backend creados:
```
backend/app/
  utils/
    text_normalization.py              # normalize_text(text) -> unidecode + upper + strip
                                       # normalize_business_name(name) -> sufijos legales:
                                       #   "S.A. DE C.V." = "SA DE CV" = "SOCIEDAD ANONIMA DE CV"
                                       # normalize_address(address) -> abreviaciones: COL, MUN, NUM
                                       # similarity_ratio(a, b) -> Jaccard sobre palabras
                                       # texts_match(a, b, threshold=0.85)
                                       # business_names_match(a, b, threshold=0.85)
    date_utils.py                      # is_current_month(date) -> bool
                                       # is_expired(date) -> bool
                                       # is_older_than_months(date, months) -> bool
                                       # safe_parse_date(value) -> date (4 formatos)
  services/
    reconciliation_service.py          # FIELD_SEVERITY: rfc=critical, razon_social/domicilio/rep=warning
                                       # FIELD_EXTRACTORS: registro escalable de campos y fuentes
                                       #   rfc: CSF + acta vs formulario
                                       #   razon_social: CSF + acta vs formulario
                                       #   domicilio: CSF + comprobante vs formulario
                                       #   representante_legal: poder + ID vs formulario
                                       # run_reconciliation(db, dossier_id, entity, documents)
                                       #   -> borra resultados previos, compara todas las combinaciones
                                       #   -> guarda ReconciliationResult por cada par
                                       # get_reconciliation_results(db, dossier_id)
  schemas/
    reconciliation.py                  # ReconciliationResultResponse
                                       # ReconciliationSummary (con has_critical boolean)
  routers/
    reconciliation.py                  # POST /dossiers/{id}/reconciliation (ejecutar)
                                       # GET /dossiers/{id}/reconciliation (resultados)
```

### Archivos frontend creados:
```
frontend/src/
  api/reconciliation.ts                # runReconciliation, getReconciliation
  hooks/useReconciliation.ts           # useReconciliation, useRunReconciliation
  components/reconciliation/
    ReconciliationTable.tsx            # Cards por comparacion: campo, fuente A vs B
                                       # Valores lado a lado con font-mono
                                       # Colores: rojo (critical), amarillo (warning), verde (match)
                                       # Resumen global: todo coincide / N discrepancias
    DiscrepancyAlert.tsx               # Alerta con conteo + flag critico
                                       # SeverityBadge (critical/warning/info/coincide)
  pages/
    DossierDetailPage.tsx              # Tab Conciliacion integrado con ReconciliationTab funcional
```

### Verificacion (completada):
- 7 comparaciones: RFC 3 pares (match), razon social 3 pares (1 match + 2 mismatch warning),
  domicilio 1 par (match)
- Discrepancia detectada: "RECONCILIACION SA DE CV" vs "RECONCILIACION GLOBAL SA DE CV" -> warning
- has_critical: false (RFC coincide en todas las fuentes)
- Audit log con reconciliation.run
- Frontend build exitoso

---

## FASE 7: Motor de Riesgo — COMPLETADA

> Score determinístico, explicable, testeable. La pieza central de la prueba.

### Archivos backend creados:
```
backend/app/
  services/
    validity_service.py                # check_document_expiration(doc) -> bool
                                       # check_csf_current_month(documents) -> bool
                                       #   (busca en extracted_data.fecha_emision y doc.fecha_emision)
                                       # check_fiscal_staleness(fiscal_checks) -> bool (>3 meses)
                                       # get_expired_documents(documents) -> list
                                       # needs_update(documents, fiscal_checks) -> bool
    risk_engine.py                     # calculate_risk(entity, documents, fiscal_checks, recon) -> Result
                                       # Funcion pura, sin side effects, sin DB
                                       #
                                       # REGLAS FISCALES (7 tipos Art.69 + Art.69-B con situacion + 69-B Bis):
                                       #   art_69_firmes: +40 blocking
                                       #   art_69_no_localizados: +50 blocking
                                       #   art_69_csd_sin_efectos: +40 blocking
                                       #   art_69b Definitivo: +50 blocking
                                       #   art_69b Presunto: +40 blocking
                                       #   art_69b_bis: +45 blocking
                                       #   + exigibles +35, sentencias +30, cancelados +25, desvirtuado +5
                                       #   + FISCAL_CHECK_STALE +15, FISCAL_NEVER_CHECKED +25
                                       #
                                       # REGLAS DOCUMENTOS:
                                       #   5 docs faltantes: acta +15, id_rep +15, comprobante +10,
                                       #     csf +20, manifestacion +10
                                       #   Docs vencidos: comprobante/id +20, otros +15
                                       #   CSF fuera de mes: +15
                                       #
                                       # REGLAS CONCILIACION:
                                       #   RFC mismatch: +35 blocking
                                       #   Razon social: +30, domicilio: +15, rep legal: +25
                                       #
                                       # REGLAS COMPLETITUD:
                                       #   Sin RFC: +25 blocking
                                       #   Sin rep legal: +20, sin socios: +10
                                       #
                                       # classify(score, blocking):
                                       #   blocking -> high_risk
                                       #   >=50 -> high_risk
                                       #   >=20 -> review_required
                                       #   <20 -> safe
                                       #
                                       # SUGGESTED_ACTIONS: 25+ acciones en español por codigo
  schemas/
    risk.py                            # RiskFactorResponse (code, points, desc, category, blocking, details)
                                       # RiskAssessmentResponse (score, classification, factors[], actions[])
  routers/
    risk.py                            # POST /dossiers/{id}/risk-assessment
                                       #   -> calcula score, guarda RiskAssessment, actualiza dossier
                                       #      (current_risk_score, classification, status)
                                       # GET /dossiers/{id}/risk-assessments (historial)
                                       # GET /dossiers/{id}/risk-assessment/latest
```

### Archivos frontend creados:
```
frontend/src/
  api/risk.ts                          # calculateRisk, listRiskAssessments, getLatestRiskAssessment
  hooks/useRiskAssessment.ts           # useLatestRiskAssessment, useCalculateRisk (mutation + invalidate)
  components/risk/
    RiskScoreGauge.tsx                 # Gauge circular SVG animado (0-100)
                                       # Colores: verde (safe), amarillo (review), rojo (high_risk)
                                       # Label de clasificacion + "Aprobacion bloqueada" si blocking
    RiskFactorList.tsx                 # Factores ordenados por puntos (mayor primero)
                                       # Iconos por categoria (fiscal/docs/recon/completitud)
                                       # Badge "Bloqueante" en rojo, colores por severidad
                                       # Codigo del factor visible
    SuggestedActions.tsx               # Lista de acciones con flechas
                                       # "CRITICO:" en rojo para acciones urgentes
  pages/
    DossierDetailPage.tsx              # Tab Riesgo integrado con RiskTab funcional
                                       # Boton "Calcular Score" / "Recalcular"
```

### Verificacion (completada — 3 escenarios):
- **Safe:** score=15, classification=safe, 1 factor (sin socios +10)
- **High risk por docs:** score=95, 7 factores (4 docs faltantes + CSF mes + sin rep + sin socios)
- **High risk por EFOS:** score=150, blocks_approval=true, FISCAL_69B_DEFINITIVO +50 blocking
  - Dossier status actualizado a high_risk, 8 acciones sugeridas
- Frontend build exitoso (461KB JS)

---

## FASE 8: UI Completa + Flujo de Aprobacion (medio)

> DossierDetailPage con tabs, dashboard, audit log, flujo approve/reject.

### Que se hace:
1. **DossierDetailPage completa** - Tabs: Overview, Documentos, Fiscal, Conciliacion, Riesgo, Auditoria
2. **Overview tab** - StatusBadge, RiskScoreGauge, DocumentChecklist, botones Aprobar/Rechazar
3. **Flujo de aprobacion** - Bloquear si high_risk o blocking factor. PATCH status.
4. **DossierStatusTimeline** - Progresion visual del estado
5. **Audit log** - `app/routers/audit.py`, AuditTimeline component
6. **Dashboard** - Stats (total por status), alertas (docs vencidos, fiscal stale), recientes
7. **DossierCard** - Card en lista con resumen
8. **Dossier service** - `app/services/dossier_service.py` con transiciones de estado + auto needs_update

### Archivos a crear:
```
backend/app/services/dossier_service.py    (audit.py ya creado en Fase 1)
frontend/src/api/audit.ts
frontend/src/hooks/useAuditLog.ts
frontend/src/components/audit/AuditTimeline.tsx
frontend/src/components/dossier/DossierCard.tsx
frontend/src/components/dossier/DossierStatusTimeline.tsx
frontend/src/components/ui/Modal.tsx
frontend/src/components/ui/DataTable.tsx
frontend/src/components/ui/Toast.tsx
```

### Verificacion Fase 8:
- DossierDetailPage muestra todas las tabs con datos
- Aprobar expediente safe -> funciona
- Intentar aprobar high_risk -> bloqueado con mensaje
- Dashboard muestra stats correctos
- Audit log registra todas las acciones

---

## FASE 9: Deploy (medio)

> Dockerfile, fly.toml, Postgres, Tigris, primer deploy.

### Que se hace:
1. **Dockerfile** multi-stage (node build frontend + python backend + static)
2. **fly.toml** - App config
3. **.dockerignore** - Excluir node_modules, venv, __pycache__
4. **Crear servicios Fly.io** - App, Postgres, Tigris, secrets
5. **Correr migraciones en deploy**
6. **Verificar URL publica**

### Archivos a crear:
```
Dockerfile           (raiz)
fly.toml             (raiz)
.dockerignore        (raiz)
```

### Verificacion Fase 9:
- `flyctl deploy` exitoso
- URL publica responde
- Crear expediente desde URL publica
- Subir documento -> extraccion funciona
- Consultar SAT -> resultados reales

---

## FASE 10: Testing (dificil)

> Unit tests, integration tests, cobertura 90%, E2E.

### Que se hace:
1. **Unit tests backend** - risk_engine (puro, facil de testear), text_normalization, rfc_validator, date_utils, classify()
2. **Integration tests backend** - API endpoints con TestClient + DB de test
3. **Unit tests frontend** - Hooks, utils, componentes con React Testing Library
4. **E2E tests** - Flujo completo: crear entidad -> crear expediente -> subir docs -> fiscal check -> conciliacion -> score -> aprobar/rechazar
5. **Cobertura** - pytest-cov al 90%

### Archivos a crear:
```
backend/tests/
  conftest.py
  test_risk_engine.py
  test_text_normalization.py
  test_rfc_validator.py
  test_date_utils.py
  test_entities_api.py
  test_dossiers_api.py
  test_documents_api.py
  test_fiscal_api.py
  test_reconciliation_api.py
  test_risk_api.py
frontend/src/__tests__/
  (tests por componente/hook)
```

### Verificacion Fase 10:
- `pytest --cov=app --cov-report=term-missing` >= 90%
- Todos los tests pasan en CI
- E2E cubre el golden path completo

---

## Referencia Rapida

### Stack
Frontend: React 19 + TS + Vite + Tailwind + React Query | Backend: FastAPI + SQLAlchemy async + Alembic | DB: PostgreSQL | AI: Claude API | Storage: Tigris S3 | Deploy: Fly.io

### Arquitectura
```
[Browser] --> [Fly.io: FastAPI]
                 ├── /api/v1/*  --> routers -> services -> models
                 ├── /*         --> React SPA (static)
                 ├── PostgreSQL
                 ├── Tigris S3
                 ├── Claude API
                 └── SAT CSVs (en memoria)
```

### API Routes (prefijo /api/v1)
```
POST/GET /entities          GET/PUT /entities/{id}
POST/GET /dossiers          GET /dossiers/{id}       PATCH /dossiers/{id}/status
POST/GET /dossiers/{id}/documents    GET/DELETE /documents/{id}
POST /dossiers/{id}/fiscal-check     GET /dossiers/{id}/fiscal-checks
POST /dossiers/{id}/risk-assessment  GET /dossiers/{id}/risk-assessment/latest
POST/GET /dossiers/{id}/reconciliation
GET /dossiers/{id}/audit-log         GET /audit-log
GET /health
```
