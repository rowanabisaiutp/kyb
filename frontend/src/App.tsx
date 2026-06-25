import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { DossierCreatePage } from "./pages/DossierCreatePage";
import { DossierDetailPage } from "./pages/DossierDetailPage";
import { DossierListPage } from "./pages/DossierListPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dossiers" element={<DossierListPage />} />
          <Route path="/dossiers/new" element={<DossierCreatePage />} />
          <Route path="/dossiers/:id" element={<DossierDetailPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
