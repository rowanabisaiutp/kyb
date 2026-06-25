# Backend — Arquitectura y Estructura

FastAPI + SQLAlchemy Async + Pydantic v2. Monolito modular con separacion por capas.

## Flujo de una peticion

```
HTTP Request
  → routers/     (validacion de entrada, HTTP status codes)
  → services/    (logica de negocio, sin dependencia de HTTP)
  → models/      (entidades SQLAlchemy, escritura a DB)
  → schemas/     (serializacion de respuesta Pydantic)
HTTP Response
```

## Estructura de archivos

```
backend/
  main.py                              # App factory, lifespan, CORS, monta routers
                                       # Scheduler de vigencias cada hora
                                       # Carga inicial de listas SAT en background

  app/
    config.py                          # Settings via pydantic-settings (.env)
    database.py                        # async engine + async_sessionmaker
    dependencies.py                    # get_db() con rollback en excepcion

    models/                            # SQLAlchemy ORM (DeclarativeBase)
      base.py                          # Base, TimestampMixin, UUIDMixin
      entity.py                        # LegalEntity, LegalRepresentative, Shareholder
      dossier.py                       # Dossier, DossierStatus (8 estados)
      document.py                      # Document, DocumentType (8 tipos), ExtractionStatus
      fiscal_check.py                  # FiscalListCheck (fuente, RFC, resultado, referencia)
      reconciliation.py                # ReconciliationResult (campo, fuentes, match, severidad)
      risk.py                          # RiskAssessment (score, clasificacion, factores JSON)
      audit.py                         # AuditLog (accion, actor, detalles, IP, timestamp)

    schemas/                           # Pydantic v2 (validacion entrada/salida)
      entity.py                        # EntityCreate, EntityUpdate, EntityResponse
      dossier.py                       # DossierCreate, DossierStatusUpdate, DossierResponse
      document.py                      # DocumentResponse, MissingDocumentsResponse
      fiscal.py                        # FiscalCheckResponse, FiscalCheckSummary
      reconciliation.py                # ReconciliationResultResponse, ReconciliationSummary
      risk.py                          # RiskFactorResponse, RiskAssessmentResponse
      audit.py                         # AuditLogResponse

    routers/                           # Endpoints REST (prefijo /api/v1)
      health.py                        # GET /health
      entities.py                      # CRUD personas morales + representantes + socios
      dossiers.py                      # CRUD expedientes + transiciones de estado
      documents.py                     # Upload, checklist, download, delete, clasificacion AI
      fiscal.py                        # Consulta listas SAT, historial
      reconciliation.py                # Ejecutar y consultar conciliacion
      risk.py                          # Calcular score, historial, resumen AI
      audit.py                         # Audit log global y por dossier

    services/                          # Logica de negocio (sin HTTP)
      audit_service.py                 # log_action() — registro central de todas las acciones
      document_service.py              # Upload con validacion, checklist de 5 docs obligatorios
      dossier_service.py               # Vigencias automaticas (check_and_update_validity)
      extraction_service.py            # Extraccion de datos de documentos con AI multi-modelo
      ai_providers.py                  # Gemini, Groq, Claude — SDKs + fallback + JSON parser
      classification_service.py        # Clasificacion automatica de tipo de documento por AI
      summary_service.py               # Resumen ejecutivo AI del expediente
      fiscal_service.py                # Carga CSVs del SAT en memoria, busqueda O(1) por RFC
      reconciliation_service.py        # Cruce de datos entre documentos y formulario
      risk_engine.py                   # Motor de riesgo: 30+ reglas, funcion pura, sin DB
      validity_service.py              # 3 triggers de needs_update (vencimiento, CSF, fiscal)
      storage_service.py               # S3/Tigris: upload, download, presigned URL, delete

    utils/                             # Funciones puras reutilizables
      rfc_validator.py                 # Validacion de formato RFC (regex)
      text_normalization.py            # Normalizacion de razon social, domicilio, similitud
      date_utils.py                    # is_expired, is_current_month, is_older_than_months
      csv_parser.py                    # Descarga y parseo de CSVs del SAT
      pdf_extractor.py                 # Extraccion local de texto PDF con PyMuPDF
      data/
        data_csv.py                    # URLs de las 9 listas fiscales del SAT
```

## Modelos de datos

```
LegalEntity (1) ──→ (N) Dossier
                          ├── (N) Document          → extracted_data JSON (AI)
                          ├── (N) FiscalListCheck    → resultado por lista SAT
                          ├── (N) ReconciliationResult → comparacion por campo
                          ├── (N) RiskAssessment     → snapshot de evaluacion
                          └── (N) AuditLog           → timeline de acciones

LegalEntity (1) ──→ (N) LegalRepresentative
LegalEntity (1) ──→ (N) Shareholder
```

## Score de riesgo — flujo

```
calculate_risk()                    # Funcion pura, sin DB
  ├── _evaluate_fiscal_rules()      # Art. 69, 69-B, 69-B Bis, 49 Bis CFF
  ├── _evaluate_document_rules()    # Faltantes, vencidos, CSF fuera de mes
  ├── _evaluate_reconciliation_rules()  # Discrepancias entre documentos
  └── _evaluate_completeness_rules()    # RFC, rep legal, socios
  → classify(score, blocking)       # safe | review_required | high_risk
```

## Transiciones de estado del expediente

```
draft → in_review
in_review → approved | rejected | needs_update
safe → approved | needs_update
review_required → approved | rejected | needs_update
high_risk → rejected | needs_update  (NO puede aprobarse)
needs_update → in_review
approved → needs_update
rejected → in_review | needs_update
```
