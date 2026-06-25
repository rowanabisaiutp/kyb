import { describe, expect, it } from "vitest";
import { formatDate, formatDateTime } from "../formatDate";

describe("formatDate", () => {
  it("formats ISO date to dd/MM/yyyy", () => {
    expect(formatDate("2026-06-15T10:30:00")).toBe("15/06/2026");
  });
});

describe("formatDateTime", () => {
  it("formats ISO to dd/MM/yyyy HH:mm", () => {
    const result = formatDateTime("2026-06-15T10:30:00");
    expect(result).toContain("15/06/2026");
    expect(result).toContain("10:30");
  });
});
