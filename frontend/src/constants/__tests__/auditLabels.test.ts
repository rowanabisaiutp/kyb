import { describe, expect, it } from "vitest";
import { ACTION_LABELS } from "../auditLabels";

describe("ACTION_LABELS", () => {
  it("has all 16 audit actions", () => {
    expect(Object.keys(ACTION_LABELS)).toHaveLength(16);
  });

  it("has spanish labels", () => {
    expect(ACTION_LABELS["dossier.created"]).toBe("Expediente creado");
    expect(ACTION_LABELS["fiscal.checked"]).toBe("Listas fiscales consultadas");
    expect(ACTION_LABELS["risk.calculated"]).toBe("Score de riesgo calculado");
  });

  it("covers entity actions", () => {
    expect(ACTION_LABELS["entity.created"]).toBeDefined();
    expect(ACTION_LABELS["entity.updated"]).toBeDefined();
  });

  it("covers document actions", () => {
    expect(ACTION_LABELS["document.uploaded"]).toBeDefined();
    expect(ACTION_LABELS["document.deleted"]).toBeDefined();
  });
});
