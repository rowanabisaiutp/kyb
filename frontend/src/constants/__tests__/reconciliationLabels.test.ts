import { describe, expect, it } from "vitest";
import { FIELD_LABELS, SEVERITY_COLORS, SOURCE_LABELS } from "../reconciliationLabels";

describe("FIELD_LABELS", () => {
  it("has 4 fields", () => {
    expect(Object.keys(FIELD_LABELS)).toHaveLength(4);
  });

  it("maps field keys to spanish labels", () => {
    expect(FIELD_LABELS.rfc).toBe("RFC");
    expect(FIELD_LABELS.razon_social).toBe("Razon Social");
    expect(FIELD_LABELS.domicilio).toBe("Domicilio");
    expect(FIELD_LABELS.representante_legal).toBe("Representante Legal");
  });
});

describe("SOURCE_LABELS", () => {
  it("has 6 sources", () => {
    expect(Object.keys(SOURCE_LABELS)).toHaveLength(6);
  });

  it("abbreviates CSF", () => {
    expect(SOURCE_LABELS.constancia_situacion_fiscal).toBe("CSF");
  });
});

describe("SEVERITY_COLORS", () => {
  it("has 3 severity levels", () => {
    expect(Object.keys(SEVERITY_COLORS)).toHaveLength(3);
  });

  it("has tailwind classes", () => {
    expect(SEVERITY_COLORS.critical).toContain("bg-red");
    expect(SEVERITY_COLORS.warning).toContain("bg-yellow");
    expect(SEVERITY_COLORS.info).toContain("bg-blue");
  });
});
