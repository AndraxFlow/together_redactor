import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/useAuth";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <main className="page">
        <div className="card">
          <p>Загрузка...</p>
        </div>
      </main>
    );
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/"
        element={user ? <HomePage /> : <Navigate to="/login" replace />}
      />
      <Route path="*" element={<Navigate to={user ? "/documents" : "/login"} replace />} />
    </Routes>
  );
}

export function App() {
  return <AppContent />;
}