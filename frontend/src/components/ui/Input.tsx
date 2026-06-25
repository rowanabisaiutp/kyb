import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, className = "", ...props }: InputProps) {
  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-text mb-1">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`w-full rounded-lg border border-border px-3 py-2 text-sm text-text
          placeholder:text-text-secondary
          focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-light
          disabled:bg-gray-50 disabled:text-text-secondary
          ${error ? "border-danger" : ""} ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-danger">{error}</p>}
    </div>
  );
}
