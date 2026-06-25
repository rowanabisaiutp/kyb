import { describe, expect, it } from "vitest";
import {
  DOCUMENT_TYPE_LABELS,
  DOSSIER_STATUS_COLORS,
  DOSSIER_STATUS_LABELS,
  REQUIRED_DOCUMENTS,
} from "../statusLabels";

describe("DOSSIER_STATUS_LABELS", () => {
  it("has all 8 statuses", () => {
    expect(Object.keys(DOSSIER_STATUS_LABELS)).toHaveLength(8);
  });

  it("has spanish labels", () => {
    expect(DOSSIER_STATUS_LABELS.draft).toBe("Borrador");
    expect(DOSSIER_STATUS_LABELS.approved).toBe("Aprobado");
    expect(DOSSIER_STATUS_LABELS.high_risk).toBe("Alto Riesgo");
  });
});

describe("DOSSIER_STATUS_COLORS", () => {
  it("has all 8 statuses", () => {
    expect(Object.keys(DOSSIER_STATUS_COLORS)).toHaveLength(8);
  });

  it("has tailwind classes", () => {
    expect(DOSSIER_STATUS_COLORS.draft).toContain("bg-");
    expect(DOSSIER_STATUS_COLORS.approved).toContain("text-");
  });
});

describe("DOCUMENT_TYPE_LABELS", () => {
  it("has all 8 types", () => {
    expect(Object.keys(DOCUMENT_TYPE_LABELS)).toHaveLength(8);
  });

  it("has spanish labels", () => {
    expect(DOCUMENT_TYPE_LABELS.acta_constitutiva).toBe("Acta Constitutiva");
    expect(DOCUMENT_TYPE_LABELS.constancia_situacion_fiscal).toBe("Constancia de Situacion Fiscal");
  });
});

describe("REQUIRED_DOCUMENTS", () => {
  it("has 5 required documents", () => {
    expect(REQUIRED_DOCUMENTS).toHaveLength(5);
  });

  it("includes acta and csf", () => {
    expect(REQUIRED_DOCUMENTS).toContain("acta_constitutiva");
    expect(REQUIRED_DOCUMENTS).toContain("constancia_situacion_fiscal");
  });
});
