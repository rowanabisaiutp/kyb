import { FileText, LayoutDashboard, Shield } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/dossiers", label: "Expedientes", icon: FileText },
] as const;

export function Sidebar() {
  const { pathname } = useLocation();

  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col min-h-screen">
      <div className="p-6 border-b border-border">
        <Link to="/" className="flex items-center gap-2 no-underline">
          <Shield className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-lg font-bold text-text leading-tight">KYB Platform</h1>
            <p className="text-xs text-text-secondary">Agencia Aduanal</p>
          </div>
        </Link>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-1 list-none p-0 m-0">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
            const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
            return (
              <li key={to}>
                <Link
                  to={to}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium no-underline transition-colors
                    ${active ? "bg-primary/10 text-primary" : "text-text-secondary hover:bg-gray-100 hover:text-text"}`}
                >
                  <Icon className="h-5 w-5" />
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
