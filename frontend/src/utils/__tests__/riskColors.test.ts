import { describe, expect, it } from "vitest";
import { getRiskBg, getRiskLabel } from "../riskColors";

describe("getRiskBg", () => {
  it("returns safe bg", () => {
    expect(getRiskBg("safe")).toContain("safe");
  });
});

describe("getRiskLabel", () => {
  it("returns spanish labels", () => {
    expect(getRiskLabel("safe")).toBe("Seguro");
    expect(getRiskLabel("review_required")).toBe("Requiere Revision");
    expect(getRiskLabel("high_risk")).toBe("Alto Riesgo");
  });
});
