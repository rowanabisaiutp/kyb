import type { ReactNode } from "react";

interface HeaderProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function Header({ title, description, action }: HeaderProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-text">{title}</h1>
        {description && <p className="text-sm text-text-secondary mt-1">{description}</p>}
      </div>
      {action}
    </div>
  );
}
