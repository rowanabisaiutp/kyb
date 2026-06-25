import { describe, expect, it } from "vitest";
import { formatRfc, isValidRfcFormat } from "../formatRfc";

describe("formatRfc", () => {
  it("converts to uppercase", () => {
    expect(formatRfc("abc010101aaa")).toBe("ABC010101AAA");
  });

  it("trims whitespace", () => {
    expect(formatRfc("  ABC010101AAA  ")).toBe("ABC010101AAA");
  });
});

describe("isValidRfcFormat", () => {
  it("accepts valid moral RFC", () => {
    expect(isValidRfcFormat("AAA010101AAA")).toBe(true);
  });

  it("accepts valid fisica RFC", () => {
    expect(isValidRfcFormat("AAAA010101BB1")).toBe(true);
  });

  it("accepts lowercase", () => {
    expect(isValidRfcFormat("aaa010101aaa")).toBe(true);
  });

  it("rejects too short", () => {
    expect(isValidRfcFormat("AA0101")).toBe(false);
  });

  it("rejects empty", () => {
    expect(isValidRfcFormat("")).toBe(false);
  });

  it("accepts ampersand", () => {
    expect(isValidRfcFormat("&HI0102165P2")).toBe(true);
  });
});
