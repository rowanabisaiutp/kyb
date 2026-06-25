import { FileText, LayoutDashboard, Menu, Plus, Shield, X } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/dossiers", label: "Expedientes", icon: FileText },
] as const;

export function Sidebar() {
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);

  const sidebar = (
    <aside className={`w-60 bg-surface-sidebar border-r border-border flex flex-col min-h-screen
      fixed inset-y-0 left-0 z-40 transition-transform duration-200
      ${open ? "translate-x-0" : "-translate-x-full"}
      lg:relative lg:translate-x-0`}>
      <div className="p-5 border-b border-border flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 no-underline" onClick={() => setOpen(false)}>
          <Shield className="h-7 w-7 text-primary" />
          <div>
            <h1 className="text-base font-bold text-text leading-tight">KYB Compliance</h1>
            <p className="text-[10px] text-text-secondary">Plataforma de Cumplimiento</p>
          </div>
        </Link>
        <button type="button" onClick={() => setOpen(false)} className="lg:hidden p-1 text-text-secondary cursor-pointer">
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="flex-1 p-3">
        <ul className="space-y-0.5 list-none p-0 m-0">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
            const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
            return (
              <li key={to}>
                <Link
                  to={to}
                  onClick={() => setOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium no-underline transition-colors
                    ${active ? "bg-primary/10 text-primary" : "text-text-secondary hover:bg-gray-100 hover:text-text"}`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-3 border-t border-border">
        <Link
          to="/dossiers/new"
          onClick={() => setOpen(false)}
          className="flex items-center justify-center gap-2 w-full px-3 py-2 rounded-lg bg-primary text-white text-sm font-medium no-underline hover:bg-primary-dark transition-colors"
        >
          <Plus className="h-4 w-4" />
          Nuevo Expediente
        </Link>
      </div>
    </aside>
  );

  return (
    <>
      <div className="lg:hidden fixed top-0 left-0 z-50 p-3">
        <button type="button" onClick={() => setOpen(true)} className="p-2 rounded-lg bg-white border border-border shadow-sm cursor-pointer">
          <Menu className="h-5 w-5 text-text" />
        </button>
      </div>

      {open && (
        <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={() => setOpen(false)} />
      )}

      {sidebar}
    </>
  );
}
