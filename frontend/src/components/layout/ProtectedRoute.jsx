import { Navigate } from "react-router-dom";
import useAuth from "../../hooks/useAuth";

// Route guard wrapping every authenticated route in AppRoutes.jsx.
// Props: children (the route's element). Redirects to /login when
// useAuth().isAuthenticated is false.
export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}
