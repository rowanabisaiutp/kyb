import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Input } from "../Input";

describe("Input", () => {
  it("renders with label", () => {
    render(<Input label="Name" id="name" />);
    expect(screen.getByLabelText("Name")).toBeInTheDocument();
  });

  it("shows error message", () => {
    render(<Input label="Email" id="email" error="Invalid email" />);
    expect(screen.getByText("Invalid email")).toBeInTheDocument();
  });

  it("renders without label", () => {
    render(<Input placeholder="Type..." />);
    expect(screen.getByPlaceholderText("Type...")).toBeInTheDocument();
  });
});
