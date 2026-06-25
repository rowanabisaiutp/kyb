import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  className?: string;
  title?: string;
}

export function Badge({
  children,
  className = "bg-gray-100 text-gray-700",
  title,
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}
      title={title}
    >
      {children}
    </span>
  );
}
