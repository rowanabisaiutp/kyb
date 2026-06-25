import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FiscalListBadge } from "../FiscalListBadge";

describe("FiscalListBadge", () => {
  it("shows Encontrado when found", () => {
    render(<FiscalListBadge found={true} />);
    expect(screen.getByText("Encontrado")).toBeInTheDocument();
  });

  it("shows Limpio when not found", () => {
    render(<FiscalListBadge found={false} />);
    expect(screen.getByText("Limpio")).toBeInTheDocument();
  });
});
