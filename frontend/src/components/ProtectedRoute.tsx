/**
 * Route guard for authenticated pages.
 */

import { Navigate } from "react-router-dom";
import type { ReactElement } from "react";
import { useAuthStore } from "../store/authStore";

type ProtectedRouteProps = {
  children: ReactElement;
};

export default function ProtectedRoute({ children }: ProtectedRouteProps): ReactElement {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
