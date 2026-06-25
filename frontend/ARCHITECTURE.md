# Frontend — Arquitectura y Estructura

React 19 + TypeScript + Vite 6 + Tailwind CSS v4 + React Query.

## Flujo de datos

```
Usuario interactua con Page/Component
  → hook (useQuery/useMutation via React Query)
  → api/ (axios, tipado con interfaces TypeScript)
  → Backend REST API (/api/v1/*)
  → React Query cache (invalidacion automatica)
  → Re-render del componente
```

## Estructura de archivos

```
frontend/src/
  main.tsx                             # QueryClientProvider + StrictMode + createRoot
  App.tsx                              # BrowserRouter + Routes dentro de AppLayout
  index.css                            # Tailwind v4 + tema custom + utilidad scrollbar-hide

  types/
    index.ts                           # 14 interfaces + 3 payloads + 3 enums
                                       # Entity, Dossier, Document, FiscalListCheck,
                                       # RiskAssessment, ReconciliationResult, AuditLogEntry

  api/                                 # Capa HTTP (axios, tipado)
    client.ts                          # axios.create({ baseURL: "/api/v1" })
    entities.ts                        # createEntity, updateEntity
    dossiers.ts                        # listDossiers, getDossier, createDossier, updateStatus
    documents.ts                       # listDocuments, uploadDocument, deleteDocument, checklist
    fiscal.ts                          # runFiscalCheck, listFiscalChecks
    reconciliation.ts                  # runReconciliation, getReconciliation
    risk.ts                            # calculateRisk, getLatestRiskAssessment
    audit.ts                           # listDossierAuditLog
    ai.ts                              # getDossierSummary (resumen ejecutivo AI)

  hooks/                               # React Query hooks (cache + mutations)
    useDossiers.ts                     # useDossiers, useDossierStats, useCreateDossier
    useDossier.ts                      # useDossier, useUpdateDossierStatus
    useDocuments.ts                    # useDocuments, useDocumentChecklist, useUploadDocument
    useFiscalCheck.ts                  # useFiscalChecks, useRunFiscalCheck
    useReconciliation.ts               # useReconciliation, useRunReconciliation
    useRiskAssessment.ts               # useLatestRiskAssessment, useCalculateRisk
    useAuditLog.ts                     # useDossierAuditLog
    useStepCompletion.ts               # Logica de completitud de pasos del wizard

  pages/                               # Paginas (1 por ruta)
    DashboardPage.tsx                  # Stats, expedientes recientes, alertas
    DossierListPage.tsx                # Busqueda, filtros, lista de expedientes
    DossierCreatePage.tsx              # Formulario: RFC + razon social → crear expediente
    DossierDetailPage.tsx              # Wizard de 6 pasos (StepSidebar + contenido)
    NotFoundPage.tsx                   # 404

  components/
    layout/                            # Estructura general
      AppLayout.tsx                    # Sidebar global + main (scroll condicional)
      Sidebar.tsx                      # Nav: Dashboard, Expedientes, Nuevo Expediente
      Header.tsx                       # Titulo + descripcion + acciones

    ui/                                # Componentes reutilizables (sin logica de negocio)
      Button.tsx                       # Variantes: primary, secondary, danger, ghost + loading
      Card.tsx                         # Card + CardTitle
      Badge.tsx                        # Pill con className custom
      Input.tsx                        # Label + error + estilos focus
      Select.tsx                       # Label + options
      StatusBadge.tsx                  # DossierStatus → Badge con color
      LoadingSpinner.tsx               # SVG animate-spin, 3 tamanos
      EmptyState.tsx                   # Icono + titulo + descripcion + action
      FadeIn.tsx                       # Animacion de entrada (opacity + translateY)

    dossier/                           # Componentes del expediente
      StepSidebar.tsx                  # Pasos del wizard con checks, score de riesgo
      StepNavigation.tsx               # Botones Anterior/Continuar
      DocumentChecklist.tsx            # Progress bar + 5 docs requeridos
      steps/                           # Un componente por paso del wizard
        StepDatosEmpresa.tsx           # Paso 1: RFC, razon social, datos adicionales
        StepDocumentos.tsx             # Paso 2: upload drag-drop, cards, extraccion AI
        StepVerificacionSAT.tsx        # Paso 3: consulta automatica en 8 listas SAT
        StepConciliacion.tsx           # Paso 4: cruce de datos entre documentos
        StepEvaluacionRiesgo.tsx       # Paso 5: gauge, factores, acciones sugeridas
        StepDecision.tsx               # Paso 6: resumen AI, aprobar/rechazar, audit log
        SummaryCard.tsx                # Card ok/no-ok reutilizable

    documents/                         # Documentos
      DocumentUploadZone.tsx           # Drag-drop con clasificacion AI automatica
      DocumentCard.tsx                 # Card con tipo, tamano, datos extraidos, eliminar
      ExtractionStatus.tsx             # Badge: pending, processing, completed, failed

    fiscal/                            # Listas fiscales
      FiscalCheckResults.tsx           # Resumen + lista de 8 checks con badge verde/rojo
      FiscalListBadge.tsx              # Encontrado (rojo) / Limpio (verde)

    reconciliation/                    # Conciliacion
      ReconciliationTable.tsx          # Cards por comparacion, valores lado a lado
      DiscrepancyAlert.tsx             # Alerta con conteo + flag critico

    risk/                              # Riesgo
      RiskScoreGauge.tsx               # Gauge circular SVG animado (0-100)
      RiskFactorList.tsx               # Factores ordenados, iconos, badges bloqueante
      SuggestedActions.tsx             # Lista de acciones correctivas

    audit/                             # Auditoria
      AuditTimeline.tsx                # Timeline visual de acciones del expediente

  utils/                               # Funciones puras
    formatDate.ts                      # formatDate, formatDateTime, formatRelative (date-fns)
    formatRfc.ts                       # formatRfc (uppercase+trim), isValidRfcFormat
    riskColors.ts                      # getRiskBg, getRiskLabel por clasificacion
    statusLabels.ts                    # Labels en español para estados, tipos de doc, pasos
```

## Rutas

| Ruta | Pagina | Descripcion |
|------|--------|-------------|
| `/` | DashboardPage | Stats por estado, recientes, alertas |
| `/dossiers` | DossierListPage | Busqueda y filtros de expedientes |
| `/dossiers/new` | DossierCreatePage | Crear expediente (RFC + razon social) |
| `/dossiers/:id` | DossierDetailPage | Wizard de 6 pasos |
| `*` | NotFoundPage | 404 |

## Patron del wizard (DossierDetailPage)

```
DossierDetailPage
  ├── StepSidebar (fijo, no scrollea)     # Pasos + score de riesgo
  └── Contenido (scrollea independiente)
       ├── Header (breadcrumb + progress bar)
       ├── Step actual (1 de 6 componentes)
       └── StepNavigation (anterior/continuar)
```

Cada paso se auto-ejecuta al montar si no hay datos previos (useRef para evitar re-trigger).
