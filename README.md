# KYB Platform — Agencia Aduanal

Plataforma web KYB (Know Your Business) para agencias aduanales mexicanas. Determina si una persona moral es **segura**, **requiere revision** o es **riesgosa** para operar comercio exterior, cumpliendo con la Regla 1.4.14 de las RGCE 2026.

**URL:** https://kyb-platform.fly.dev  
**Repo:** https://github.com/rowanabisaiutp/kyb

---

## Stack Tecnologico

| Capa | Tecnologia |
|------|-----------|
| Frontend | React 19 + TypeScript + Vite 6 + Tailwind CSS v4 |
| Backend | FastAPI + SQLAlchemy Async + Pydantic v2 |
| Base de Datos | PostgreSQL (Fly Postgres) |
| AI Multi-modelo | Gemini 2.0 Flash → Groq Llama 3.3 → Claude (fallback automatico) |
| Listas Fiscales | 8 CSVs reales del SAT (500K+ RFCs) |
| Deploy | Fly.io (monolito, Docker multi-stage) |
| CI | GitHub Actions (lint, tests, build) |

---

## Funcionalidades

### Proceso KYB Guiado (Wizard de 6 Pasos)

La plataforma guia al usuario paso a paso a traves del proceso KYB:

1. **Datos de la Empresa** — RFC y razon social para iniciar, datos adicionales opcionales
2. **Documentos** — Carga de documentos con clasificacion automatica por AI y extraccion de datos
3. **Verificacion SAT** — Consulta automatica del RFC en 8 listas fiscales publicas reales
4. **Conciliacion** — Comparacion automatica de datos entre documentos y formulario
5. **Evaluacion de Riesgo** — Score determinístico con 30+ reglas explicables
6. **Decision Final** — Resumen ejecutivo AI + aprobacion/rechazo con bloqueo si hay riesgo critico

### AI Multi-Modelo con Fallback

La plataforma usa 3 proveedores de AI con fallback automatico. Si uno falla por quota o error, el siguiente responde sin que el usuario lo note:

- **Gemini 2.0 Flash** (Google) — principal, vision + texto
- **Groq Llama 3.3 70B** — fallback rapido, alto limite gratis
- **Claude Sonnet** (Anthropic) — fallback final

Funciones AI:
- **Clasificacion automatica de documentos** — sube un PDF y la AI detecta si es CSF, acta, INE, comprobante, etc.
- **Extraccion de datos** — AI lee el documento y extrae RFC, razon social, domicilio, fechas, socios
- **Resumen ejecutivo** — AI genera un parrafo explicando el estado del expediente y su recomendacion

### Listas Fiscales del SAT (Datos Reales)

Consulta directa a los CSVs publicos del SAT — no mocks:

| Lista | Articulo | RFCs |
|-------|----------|------|
| Cancelados | Art. 69 CFF | ~181,000 |
| Exigibles | Art. 69 CFF | ~5,800 |
| Firmes | Art. 69 CFF | ~258,000 |
| No Localizados | Art. 69 CFF | ~53,000 |
| Sentencias | Art. 69 CFF | ~572 |
| CSD Sin Efectos | Art. 69 CFF | ~57,500 |
| EFOS | Art. 69-B CFF | ~14,300 |
| Perdidas Indebidas | Art. 69-B Bis CFF | ~3 |

Cada consulta guarda: fuente, fecha/hora, RFC buscado, resultado y referencia al listado.

### Fuentes Oficiales

| Fuente | Uso en la plataforma |
|--------|---------------------|
| [Regla 1.4.14 RGCE 2026](https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rgce/rgce/1raRMRGCEpara2026.pdf) | Marco normativo del expediente KYB |
| [Datos abiertos SAT](https://www.sat.gob.mx/minisitio/DatosAbiertos/contribuyentes_publicados.html) | CSVs descargados para consulta de listas fiscales |
| [Contribuyentes incumplidos](https://wwwmat.sat.gob.mx/consultas/11981/consulta-la-relacion-de-contribuyentes-incumplidos) | Referencia Art. 69 CFF (6 listados) |
| [Operaciones presuntamente inexistentes](https://wwwmat.sat.gob.mx/consultas/76674/consulta-la-relacion-de-contribuyentes-con-operaciones-presuntamente-inexistentes) | Referencia Art. 69-B CFF (EFOS) |
| [Portal SAT PLD](https://sppld.sat.gob.mx/pld/interiores/obligaciones.html) | Obligaciones PLD/FT: identificacion de clientes y custodia de registros (no ofrece datos descargables; la plataforma implementa estas obligaciones via expediente KYB y audit log) |

### Score de Riesgo Explicable

Motor determinístico con 30+ reglas. Cada factor muestra puntos, descripcion y si bloquea la aprobacion:

| Categoria | Ejemplo | Puntos |
|-----------|---------|--------|
| Fiscal | EFOS Definitivo (Art. 69-B) | +50 (bloqueante) |
| Fiscal | No Localizado (Art. 69) | +50 (bloqueante) |
| Documentos | CSF faltante | +20 |
| Documentos | Comprobante vencido | +20 |
| Conciliacion | Discrepancia de RFC | +35 (bloqueante) |
| Conciliacion | Discrepancia razon social | +30 |
| Completitud | Sin representante legal | +20 |

Clasificacion: `safe` (<20) · `review_required` (20-49) · `high_risk` (>=50 o bloqueante)

### Conciliacion de Datos

Compara automaticamente entre documentos y formulario:
- RFC y razon social (CSF vs acta vs formulario)
- Domicilio (CSF vs comprobante vs formulario)
- Representante legal (poder vs ID vs formulario)
- Fechas de emision y constitucion

### Vigencias Automaticas

Scheduler cada hora que marca expedientes como `needs_update` cuando:
- Un documento vence
- La CSF no es del mes vigente
- La revision fiscal tiene mas de 3 meses

### Audit Log

Registro completo de todas las acciones con timeline visual: creacion, uploads, extracciones AI, consultas SAT, calculos de riesgo, aprobaciones/rechazos.

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
# Backend unit tests
cd backend && pytest tests/ --cov=app -q

# Frontend unit + integration
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
