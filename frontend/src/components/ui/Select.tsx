import type { SelectHTMLAttributes } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
}

export function Select({ label, options, id, className = "", ...props }: SelectProps) {
  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-text mb-1">
          {label}
        </label>
      )}
      <select
        id={id}
        className={`w-full rounded-lg border border-border px-3 py-2 text-sm text-text
          focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-light
          ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
