# KYB Platform — Agencia Aduanal

Plataforma web KYB (Know Your Business) para agencias aduanales mexicanas. Determina si una persona moral es **segura**, **requiere revision** o es **riesgosa** para operar comercio exterior, cumpliendo con la Regla 1.4.14 de las RGCE 2026.

**URL:** https://kyb-platform.fly.dev  
**Repo:** https://github.com/rowanabisaiutp/kyb

---

## Requisitos de la Prueba Tecnica

### 1. Expediente KYB

| Requisito | Estado | Implementacion |
|-----------|:---:|---|
| Crear expediente KYB | Hecho | `POST /api/v1/dossiers` → modelo Dossier vinculado a LegalEntity |
| Cargar documentos con metadata auditable | Hecho | Upload con validacion MIME/tamano, storage S3, audit log automatico |
| Validar documentos, vigencias y datos obligatorios | Hecho | `validity_service.py` — 3 triggers de `needs_update` + checklist 5 docs |
| Consultar listas fiscales publicas del SAT | Hecho | 9 CSVs reales descargados del SAT, busqueda O(1) por RFC |
| Conciliar datos entre documentos | Hecho | Cruce de RFC, razon social, domicilio, rep legal, fechas |
| Calcular score de riesgo explicable | Hecho | Funcion pura con 30+ reglas, determinístico y testeable |
| Clasificar safe / review_required / high_risk | Hecho | `classify()`: safe (<20), review_required (20-49), high_risk (>=50 o bloqueante) |
| Bloquear aprobacion con riesgo critico | Hecho | high_risk no puede aprobarse, validado en transiciones de estado |
| Registrar evidencia y audit log | Hecho | `audit_service.log_action()` en cada operacion del expediente |

### 2. Documentos del Expediente (Regla 1.4.14)

| Documento | Tipo en sistema | Riesgo si falta |
|-----------|----------------|:---:|
| Acta constitutiva | `acta_constitutiva` | +15 |
| Identificacion del representante | `identificacion_representante` | +15 |
| Poder de representacion | `poder_representacion` | Opcional |
| Comprobante de domicilio | `comprobante_domicilio` | +10 |
| Constancia de situacion fiscal | `constancia_situacion_fiscal` | +20 |
| Manifestacion bajo protesta | `manifestacion_protesta` | +10 |
| RFC | Campo obligatorio en LegalEntity | +25 bloqueante |
| Socios/accionistas | Modelo Shareholder | +10 |

### 3. Score de Riesgo

Motor determinístico, explicable y testeable (`risk_engine.py`). Cada factor muestra puntos, descripcion y si bloquea:

| Categoria | Factores | Puntos |
|-----------|---------|--------|
| Fiscal | EFOS Definitivo, No Localizado, CSD sin efectos, Firmes, 69-B Bis, etc. | 5-50 (varios bloqueantes) |
| Documentos | Faltantes, vencidos, CSF fuera de mes | 10-20 |
| Conciliacion | Discrepancia RFC (bloqueante), razon social, domicilio, rep legal, fechas | 5-35 |
| Completitud | Sin RFC (bloqueante), sin rep legal, sin socios | 10-25 |

### 4. Listas Fiscales (Datos Reales, Sin Mocks)

| Articulo | Listas | Fuente |
|----------|--------|--------|
| Art. 69 CFF (excepto fr. VI) | 6 listados: Cancelados, Exigibles, Firmes, No localizados, Sentencias, CSD sin efectos | CSVs publicos del SAT |
| Art. 69-B CFF | Listado completo EFOS (Definitivo/Presunto/Desvirtuado/Sentencia) | CSV publico del SAT |
| Art. 69-B Bis CFF | Transmision indebida de perdidas | CSV publico del SAT |
| Art. 49 Bis CFF | Fuente: listado 69-B (unica base publica, justificado en SAT_FUENTES.md) | CSV publico del SAT |

Cada consulta guarda: fuente (`source_url`), fecha/hora (`checked_at`), RFC buscado, resultado (`found`), referencia al listado (`list_reference`).

### 5. Conciliacion de Datos

| Campo | Fuentes comparadas | Severidad |
|-------|-------------------|-----------|
| RFC | CSF + Acta + Formulario | critical (+35 bloqueante) |
| Razon social | CSF + Acta + Formulario | warning (+30) |
| Domicilio | CSF + Comprobante + Formulario | warning (+15) |
| Representante legal | Poder + ID + Formulario | warning (+25) |
| Fechas | CSF + Comprobante + Acta | info (+5-10) |

### 6. Vigencias

El expediente pasa a `needs_update` automaticamente cuando:
- Un documento vence (`fecha_vencimiento < hoy`)
- La CSF no es del mes vigente
- La revision fiscal tiene mas de 3 meses
- Scheduler automatico cada hora (`main.py`)

### 7. Fuentes Oficiales

| Fuente | Uso |
|--------|-----|
| [Regla 1.4.14 RGCE 2026](https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/rgce/1raRMRGCEpara2026.pdf) | Marco normativo del expediente KYB |
| [Datos abiertos SAT](https://www.sat.gob.mx/minisitio/DatosAbiertos/contribuyentes_publicados.html) | CSVs descargados para consulta fiscal |
| [Contribuyentes incumplidos](https://wwwmat.sat.gob.mx/consultas/11981/consulta-la-relacion-de-contribuyentes-incumplidos) | Referencia Art. 69 CFF |
| [Operaciones presuntamente inexistentes](https://wwwmat.sat.gob.mx/consultas/76674/consulta-la-relacion-de-contribuyentes-con-operaciones-presuntamente-inexistentes) | Referencia Art. 69-B CFF |
| [Portal SAT PLD](https://sppld.sat.gob.mx/pld/interiores/obligaciones.html) | Obligaciones PLD/FT (informativo, sin datos descargables) |

---

## Stack Tecnologico

| Capa | Tecnologia |
|------|-----------|
| Frontend | React 19 + TypeScript + Vite 6 + Tailwind CSS v4 |
| Backend | FastAPI + SQLAlchemy Async + Pydantic v2 |
| Base de Datos | PostgreSQL (Fly Postgres) |
| AI Multi-modelo | Gemini 2.0 Flash → Groq Llama 3.3 → Claude (fallback automatico) |
| Listas Fiscales | 9 CSVs reales del SAT (500K+ RFCs) |
| Deploy | Fly.io (monolito, Docker multi-stage) |
| CI | GitHub Actions (lint, tests, build) |

---

## Arquitectura

```
[Browser] → [Fly.io: FastAPI + React SPA]
                ├── /api/v1/*  → routers → services → models
                ├── /*         → React SPA (static files)
                ├── PostgreSQL (Fly Postgres)
                ├── AI (Gemini → Groq → Claude, fallback)
                └── SAT CSVs (datos reales, en memoria)
```

Documentacion detallada de la estructura de archivos:
- [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) — modelos, servicios, routers, flujo del score
- [frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md) — componentes, hooks, wizard, rutas

---

## Proceso KYB (Wizard de 6 Pasos)

1. **Datos de la Empresa** — RFC y razon social para iniciar, datos adicionales opcionales
2. **Documentos** — Carga con clasificacion automatica por AI y extraccion de datos
3. **Verificacion SAT** — Consulta automatica del RFC en 9 listas fiscales publicas reales
4. **Conciliacion** — Comparacion automatica de datos entre documentos y formulario
5. **Evaluacion de Riesgo** — Score determinístico con 30+ reglas explicables
6. **Decision Final** — Resumen ejecutivo AI + aprobacion/rechazo con bloqueo si hay riesgo critico

---

## AI Multi-Modelo con Fallback

3 proveedores con fallback automatico. Si uno falla, el siguiente responde:

- **Gemini 2.0 Flash** (Google) — principal, vision + texto
- **Groq Llama 3.3 70B** — fallback rapido
- **Claude Sonnet** (Anthropic) — fallback final

Funciones: clasificacion de documentos, extraccion de datos, resumen ejecutivo.

---

## Correr Localmente

### Requisitos
- Python 3.13+, Node.js 22+, Docker

### Setup

```bash
# 1. Base de datos
docker run -d --name kyb-dev-db -p 5432:5432 \
  -e POSTGRES_USER=kyb_dev -e POSTGRES_PASSWORD=kyb_dev_pass \
  -e POSTGRES_DB=kyb_dev postgres:17-alpine

# 2. Backend
cd backend
python -m venv venv && venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env  # configurar API keys
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Frontend
cd frontend
npm install && npm run dev
```

### Con Docker
```bash
docker build -t kyb-platform .
docker run -d -p 8080:8080 -e GEMINI_API_KEY=key -e GROQ_API_KEY=key kyb-platform
```

---

## Tests

```bash
# Backend (121 tests)
cd backend && pytest tests/ --cov=app -q

# Frontend (79 tests, 19 archivos)
cd frontend && npx vitest run

# E2E (Playwright)
cd frontend && npx playwright test
```

---

## API

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST/GET | /api/v1/entities | CRUD personas morales |
| POST/GET | /api/v1/dossiers | CRUD expedientes |
| POST/GET | /api/v1/dossiers/{id}/documents | Upload y gestion de documentos |
| POST | /api/v1/documents/classify | Clasificacion AI de documentos |
| POST | /api/v1/dossiers/{id}/fiscal-check | Consulta listas SAT |
| POST/GET | /api/v1/dossiers/{id}/reconciliation | Conciliacion de datos |
| POST | /api/v1/dossiers/{id}/risk-assessment | Calculo de riesgo |
| GET | /api/v1/dossiers/{id}/summary | Resumen ejecutivo AI |
| GET | /api/v1/dossiers/{id}/audit-log | Registro de auditoria |
| GET | /api/v1/health | Health check |

---

## Deploy

Desplegado en Fly.io con PostgreSQL managed.

```bash
flyctl secrets set GEMINI_API_KEY=key GROQ_API_KEY=key --app kyb-platform
flyctl deploy --app kyb-platform --local-only
```
