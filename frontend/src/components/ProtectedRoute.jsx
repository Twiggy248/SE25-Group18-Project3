//ProtectedRoute.jsx
import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import apiClient from "../api/client";

export default function ProtectedRoute({ children }) {
  const [auth, setAuth] = useState(null);

  useEffect(() => {
    apiClient
      .get("/auth/me", {withCredentials: true})
      .then((res) => setAuth(res.data.authenticated))
      .catch(() => setAuth(false));
  }, []);

  if (auth === null) return <div>Loading...</div>;

  if (!auth) return <Navigate to="/login" replace />;

  return children;
}