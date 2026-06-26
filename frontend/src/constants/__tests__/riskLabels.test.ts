import { describe, expect, it } from "vitest";
import { RISK_CATEGORY_CONFIG, RISK_GAUGE_COLORS } from "../riskLabels";

describe("RISK_CATEGORY_CONFIG", () => {
  it("has 4 categories", () => {
    expect(Object.keys(RISK_CATEGORY_CONFIG)).toHaveLength(4);
  });

  it("has spanish labels", () => {
    expect(RISK_CATEGORY_CONFIG.fiscal.label).toBe("Fiscal");
    expect(RISK_CATEGORY_CONFIG.documents.label).toBe("Documentos");
    expect(RISK_CATEGORY_CONFIG.reconciliation.label).toBe("Conciliacion");
    expect(RISK_CATEGORY_CONFIG.completeness.label).toBe("Completitud");
  });

  it("has icon components", () => {
    expect(RISK_CATEGORY_CONFIG.fiscal.icon).toBeDefined();
    expect(RISK_CATEGORY_CONFIG.documents.icon).toBeDefined();
  });
});

describe("RISK_GAUGE_COLORS", () => {
  it("has 3 classifications", () => {
    expect(Object.keys(RISK_GAUGE_COLORS)).toHaveLength(3);
  });

  it("has hex color values", () => {
    expect(RISK_GAUGE_COLORS.safe).toMatch(/^#[0-9a-f]{6}$/);
    expect(RISK_GAUGE_COLORS.review_required).toMatch(/^#[0-9a-f]{6}$/);
    expect(RISK_GAUGE_COLORS.high_risk).toMatch(/^#[0-9a-f]{6}$/);
  });
});
