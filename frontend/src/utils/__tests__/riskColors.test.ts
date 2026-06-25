import { describe, expect, it } from "vitest";
import { getRiskBg, getRiskColor, getRiskLabel, getScoreColor } from "../riskColors";

describe("getRiskColor", () => {
  it("returns green for safe", () => {
    expect(getRiskColor("safe")).toBe("text-safe");
  });
  it("returns warning for review_required", () => {
    expect(getRiskColor("review_required")).toBe("text-warning");
  });
  it("returns danger for high_risk", () => {
    expect(getRiskColor("high_risk")).toBe("text-danger");
  });
});

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

describe("getScoreColor", () => {
  it("returns danger for >= 50", () => {
    expect(getScoreColor(50)).toBe("text-danger");
    expect(getScoreColor(100)).toBe("text-danger");
  });
  it("returns warning for 20-49", () => {
    expect(getScoreColor(20)).toBe("text-warning");
    expect(getScoreColor(49)).toBe("text-warning");
  });
  it("returns safe for < 20", () => {
    expect(getScoreColor(0)).toBe("text-safe");
    expect(getScoreColor(19)).toBe("text-safe");
  });
});
