import type { DocumentType, DossierStatus } from "../types";

export const DOSSIER_STATUS_LABELS: Record<DossierStatus, string> = {
  draft: "Borrador",
  in_review: "En Revision",
  safe: "Seguro",
  review_required: "Requiere Revision",
  high_risk: "Alto Riesgo",
  needs_update: "Requiere Actualizacion",
  approved: "Aprobado",
  rejected: "Rechazado",
};

export const DOSSIER_STATUS_COLORS: Record<DossierStatus, string> = {
  draft: "bg-gray-100 text-gray-700",
  in_review: "bg-blue-100 text-blue-700",
  safe: "bg-green-100 text-green-700",
  review_required: "bg-yellow-100 text-yellow-700",
  high_risk: "bg-red-100 text-red-700",
  needs_update: "bg-orange-100 text-orange-700",
  approved: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-200 text-red-800",
};

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  acta_constitutiva: "Acta Constitutiva",
  identificacion_representante: "Identificacion del Representante Legal",
  poder_representacion: "Poder de Representacion",
  comprobante_domicilio: "Comprobante de Domicilio",
  constancia_situacion_fiscal: "Constancia de Situacion Fiscal",
  manifestacion_protesta: "Manifestacion Bajo Protesta",
  rfc_documento: "Documento RFC",
  otro: "Otro",
};

export const STEP_LABELS = [
  { label: "Datos de la Empresa", description: "Informacion basica de la persona moral" },
  { label: "Documentos", description: "Carga de documentos requeridos" },
  { label: "Verificacion SAT", description: "Consulta de listas fiscales" },
  { label: "Conciliacion", description: "Comparacion de datos entre fuentes" },
  { label: "Evaluacion de Riesgo", description: "Calculo del score de riesgo" },
  { label: "Decision Final", description: "Aprobacion o rechazo del expediente" },
] as const;

export const REQUIRED_DOCUMENTS: DocumentType[] = [
  "acta_constitutiva",
  "identificacion_representante",
  "comprobante_domicilio",
  "constancia_situacion_fiscal",
  "manifestacion_protesta",
];
