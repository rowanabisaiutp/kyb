# KYB Platform — Agencia Aduanal

Plataforma web KYB (Know Your Business) para agencias aduanales. Determina si una persona moral mexicana es **segura**, **requiere revision** o es **riesgosa** para operar comercio exterior, cumpliendo con la Regla 1.4.14 de las RGCE 2026.

## Stack

| Capa | Tecnologia |
|------|-----------|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| Backend | FastAPI + SQLAlchemy Async + Pydantic v2 |
| Base de Datos | PostgreSQL |
| AI | Gemini 2.5 Flash / Claude API (extraccion de documentos) |
| Deploy | Fly.io (monolito) |
| Listas Fiscales | Datos reales del SAT (8 CSVs publicos) |

## Funcionalidades

### Expediente KYB
- Crear expedientes con datos de persona moral, representante legal y socios
- Cargar documentos: acta constitutiva, CSF, INE, comprobante domicilio, manifestacion bajo protesta, poder de representacion
- Checklist de documentos requeridos (5/5)

### Extraccion AI
- Al subir un documento PDF/imagen, Gemini extrae automaticamente los datos estructurados (RFC, razon social, domicilio, etc.)
- Soporta CSF, actas constitutivas, INE, comprobantes, poderes

### Listas Fiscales del SAT
- Consulta **datos reales** del SAT (no mocks)
- 8 listas: Art. 69 CFF (Cancelados, Exigibles, Firmes, No Localizados, Sentencias, CSD sin efectos) + Art. 69-B + Art. 69-B Bis
- +500,000 RFCs reales cargados en memoria
- Cada consulta guarda: fuente, fecha/hora, RFC buscado, resultado, referencia al listado
- Actualizacion automatica cada 24 horas

### Conciliacion de Datos
- Compara datos entre documentos y formulario: RFC, razon social, domicilio, representante legal, fechas
- Normalizacion de razones sociales (S.A. DE C.V. = SA DE CV)
- Severidad por campo: critical (RFC), warning (razon social, domicilio), info (fechas)

### Score de Riesgo
- **Deterministico, explicable y testeable**
- 30+ reglas con puntos y factores bloqueantes
- Factores: listas fiscales, documentos faltantes/vencidos, CSF fuera de mes, discrepancias, completitud
- Clasificacion: `safe` (<20 pts) | `review_required` (20-49) | `high_risk` (>=50 o bloqueante)
- Ejemplo: +20 por comprobante vencido, +30 por discrepancia de razon social, 0 por listas limpias
- Acciones sugeridas automaticas por cada factor
- Bloquea aprobacion si hay riesgo critico

### Vigencias
- Scheduler automatico cada hora
- Marca expedientes como `needs_update` cuando:
  - Un documento vence
  - La CSF no es del mes vigente
  - La revision fiscal tiene mas de 3 meses

### Audit Log
- Registro de todas las acciones: creacion, uploads, consultas, calculos, aprobaciones
- Timeline visual en la UI

## Arquitectura

```
[Browser] --> [Fly.io: FastAPI]
                 ├── /api/v1/*  --> routers -> services -> models
                 ├── /*         --> React SPA (static files)
                 ├── PostgreSQL (Fly Postgres)
                 ├── Gemini API (extraccion de documentos)
                 └── SAT CSVs (datos reales, en memoria, refresh cada 24h)
```

## Correr Localmente

### Requisitos
- Python 3.13+
- Node.js 22+
- Docker (para PostgreSQL)

### Setup

```bash
# 1. Base de datos
docker run -d --name kyb-dev-db -p 5432:5432 \
  -e POSTGRES_USER=kyb_dev -e POSTGRES_PASSWORD=kyb_dev_pass \
  -e POSTGRES_DB=kyb_dev postgres:17-alpine

# 2. Backend
cd backend
python -m venv venv
venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # configurar GEMINI_API_KEY
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Frontend
cd frontend
npm install
npm run dev
```

### Con Docker (todo junto)
```bash
docker build -t kyb-platform .
docker run -d --name kyb -p 8080:8080 \
  -e GEMINI_API_KEY=tu_key \
  kyb-platform
```

Abrir http://localhost:8080

## Tests

```bash
# Backend (90 unit tests)
cd backend
pytest tests/ --cov=app -q

# Frontend (85 unit + integration tests)
cd frontend
npx vitest run

# E2E (13 tests con Playwright)
npx playwright test
```

**219 tests totales, 0 fallos.**

## API

```
POST/GET  /api/v1/entities
POST/GET  /api/v1/dossiers
POST/GET  /api/v1/dossiers/{id}/documents
POST      /api/v1/dossiers/{id}/fiscal-check
POST/GET  /api/v1/dossiers/{id}/reconciliation
POST      /api/v1/dossiers/{id}/risk-assessment
GET       /api/v1/dossiers/{id}/audit-log
GET       /api/v1/health
```

## Deploy

Desplegado en Fly.io con PostgreSQL managed.

```bash
flyctl secrets set GEMINI_API_KEY=tu_key --app kyb-platform
flyctl deploy
```
