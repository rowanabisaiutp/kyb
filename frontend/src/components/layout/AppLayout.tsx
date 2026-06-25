import { Outlet, useMatch } from "react-router-dom";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  const isDossierDetail = useMatch("/dossiers/:id");

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      <Sidebar />
      <main className={`flex-1 ${isDossierDetail ? "overflow-hidden" : "overflow-y-auto pt-14 px-4 pb-6 lg:pt-6 lg:px-8 lg:pb-8"}`}>
        <div className={isDossierDetail ? "h-full" : "max-w-7xl mx-auto"}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
