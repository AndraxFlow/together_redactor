import { createBrowserRouter } from "react-router-dom"
import { Navigate } from "react-router-dom"

import { LoginPage } from "./pages/LoginPage"
import DocumentsPage from "./pages/DocumentsPage"
import EditorPage from "./pages/EditorPage"
import { HomePage } from "./pages/HomePage"

import ProtectedRoute from "./routes/ProtectedRoute"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/documents" />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/documents",
    element: (
      <ProtectedRoute>
        <DocumentsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/editor/:id",
    element: (
      <ProtectedRoute>
        <EditorPage />
      </ProtectedRoute>
    ),
  },
])