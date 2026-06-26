import { describe, expect, it } from "vitest";
import { FISCAL_LIST_LABELS } from "../fiscalLabels";

describe("FISCAL_LIST_LABELS", () => {
  it("has 8 fiscal lists", () => {
    expect(Object.keys(FISCAL_LIST_LABELS)).toHaveLength(8);
  });

  it("has Art. 69 variants", () => {
    expect(FISCAL_LIST_LABELS.art_69_cancelados).toBe("Art. 69 - Cancelados");
    expect(FISCAL_LIST_LABELS.art_69_firmes).toBe("Art. 69 - Firmes");
    expect(FISCAL_LIST_LABELS.art_69_no_localizados).toBe("Art. 69 - No Localizados");
  });

  it("has Art. 69-B lists", () => {
    expect(FISCAL_LIST_LABELS.art_69b).toBe("Art. 69-B - EFOS");
    expect(FISCAL_LIST_LABELS.art_69b_bis).toBe("Art. 69-B Bis - Perdidas");
  });
});
