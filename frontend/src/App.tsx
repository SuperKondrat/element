import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { TransportProvider } from "./context/TransportContext";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { Header } from "./components/Header";
import { LotsPage } from "./pages/public/LotsPage";
import { LotDetailPage } from "./pages/public/LotDetailPage";
import { AdminLoginPage } from "./pages/admin/AdminLoginPage";
import { AdminLayout } from "./pages/admin/AdminLayout";
import { FeedsPage } from "./pages/admin/FeedsPage";
import { BookingsPage } from "./pages/admin/BookingsPage";
import { ApplicationsPage } from "./pages/admin/ApplicationsPage";

export default function App() {
  return (
    <ThemeProvider>
      <TransportProvider>
        <AuthProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-slate-50 text-slate-900 transition-colors dark:bg-slate-950 dark:text-slate-100">
              <Header />
              <Routes>
                <Route path="/" element={<LotsPage />} />
                <Route path="/lots/:id" element={<LotDetailPage />} />
                <Route path="/admin/login" element={<AdminLoginPage />} />
                <Route path="/admin" element={<AdminLayout />}>
                  <Route index element={<Navigate to="feeds" replace />} />
                  <Route path="feeds" element={<FeedsPage />} />
                  <Route path="bookings" element={<BookingsPage />} />
                  <Route path="applications" element={<ApplicationsPage />} />
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </BrowserRouter>
        </AuthProvider>
      </TransportProvider>
    </ThemeProvider>
  );
}
