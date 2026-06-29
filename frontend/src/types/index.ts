export interface LegalRepresentative {
  id: string;
  entity_id: string;
  nombre_completo: string;
  curp: string | null;
  rfc_persona_fisica: string | null;
  cargo: string | null;
  vigente: boolean;
  created_at: string;
}

export interface Shareholder {
  id: string;
  entity_id: string;
  nombre_completo: string;
  rfc: string | null;
  porcentaje_participacion: number | null;
  tipo: "socio" | "accionista" | "beneficiario_controlador";
  created_at: string;
}

export interface Entity {
  id: string;
  rfc: string;
  razon_social: string;
  nombre_comercial: string | null;
  domicilio_fiscal: string | null;
  codigo_postal: string | null;
  regimen_fiscal: string | null;
  fecha_constitucion: string | null;
  objeto_social: string | null;
  created_at: string;
  updated_at: string;
  representatives: LegalRepresentative[];
  shareholders: Shareholder[];
}

export interface EntityListItem {
  id: string;
  rfc: string;
  razon_social: string;
  nombre_comercial: string | null;
  created_at: string;
}

export type DossierStatus =
  | "draft"
  | "in_review"
  | "safe"
  | "review_required"
  | "high_risk"
  | "needs_update"
  | "approved"
  | "rejected";

export type RiskClassification = "safe" | "review_required" | "high_risk";

export interface Dossier {
  id: string;
  entity_id: string;
  status: DossierStatus;
  current_risk_score: number | null;
  current_risk_classification: RiskClassification | null;
  approved_by: string | null;
  approved_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  entity: Entity | null;
}

export type DocumentType =
  | "acta_constitutiva"
  | "identificacion_representante"
  | "poder_representacion"
  | "comprobante_domicilio"
  | "constancia_situacion_fiscal"
  | "manifestacion_protesta"
  | "rfc_documento"
  | "otro";

export type ExtractionStatus = "pending" | "processing" | "completed" | "failed";

export interface Document {
  id: string;
  dossier_id: string;
  document_type: DocumentType;
  file_name: string | null;
  file_key: string | null;
  file_size: number | null;
  mime_type: string | null;
  fecha_emision: string | null;
  fecha_vencimiento: string | null;
  is_expired: boolean;
  extracted_data: Record<string, unknown> | null;
  extraction_status: ExtractionStatus;
  created_at: string;
  updated_at: string;
}

export interface FiscalListCheck {
  id: string;
  dossier_id: string;
  rfc_searched: string;
  list_type: string;
  source_url: string;
  checked_at: string;
  found: boolean;
  result_detail: Record<string, unknown> | null;
  list_reference: string | null;
  created_at: string;
}

export interface RiskFactor {
  code: string;
  points: number;
  description: string;
  category: string;
  blocking: boolean;
  details: Record<string, unknown> | null;
}

export interface RiskAssessment {
  id: string;
  dossier_id: string;
  total_score: number;
  classification: RiskClassification;
  factors: RiskFactor[];
  blocks_approval: boolean;
  suggested_actions: string[];
  calculated_at: string;
}

export interface ReconciliationResult {
  id: string;
  dossier_id: string;
  field_name: string;
  source_a: string;
  source_b: string;
  value_a: string | null;
  value_b: string | null;
  match: boolean;
  severity: "info" | "warning" | "critical" | null;
  checked_at: string;
}

export interface AuditLogEntry {
  id: string;
  dossier_id: string | null;
  entity_id: string | null;
  action: string;
  actor: string;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface EntityCreatePayload {
  rfc: string;
  razon_social: string;
  nombre_comercial?: string;
  domicilio_fiscal?: string;
  codigo_postal?: string;
  regimen_fiscal?: string;
  fecha_constitucion?: string;
  objeto_social?: string;
  representatives?: { nombre_completo: string; curp?: string; rfc_persona_fisica?: string; cargo?: string }[];
  shareholders?: { nombre_completo: string; rfc?: string; porcentaje_participacion?: number; tipo: string }[];
}

export interface DossierCreatePayload {
  entity_id: string;
  notes?: string;
}

export interface DossierStatusUpdatePayload {
  status: "in_review" | "approved" | "rejected" | "needs_update";
  approved_by?: string;
  notes?: string;
}
