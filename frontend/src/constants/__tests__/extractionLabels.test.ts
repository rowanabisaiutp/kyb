import { describe, expect, it } from "vitest";
import { EXTRACTION_STATUS_CONFIG } from "../extractionLabels";

describe("EXTRACTION_STATUS_CONFIG", () => {
  it("has 4 statuses", () => {
    expect(Object.keys(EXTRACTION_STATUS_CONFIG)).toHaveLength(4);
  });

  it("each status has label, className and tooltip", () => {
    for (const config of Object.values(EXTRACTION_STATUS_CONFIG)) {
      expect(config.label).toBeTruthy();
      expect(config.className).toContain("bg-");
      expect(config.tooltip).toBeTruthy();
    }
  });

  it("has correct spanish labels", () => {
    expect(EXTRACTION_STATUS_CONFIG.pending.label).toBe("Pendiente");
    expect(EXTRACTION_STATUS_CONFIG.processing.label).toBe("Procesando...");
    expect(EXTRACTION_STATUS_CONFIG.completed.label).toBe("Extraido");
    expect(EXTRACTION_STATUS_CONFIG.failed.label).toBe("Extraccion no disponible");
  });
});
