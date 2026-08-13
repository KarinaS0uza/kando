import { useState, useEffect } from "react";

// "token" is set directly by JoinForm.jsx on email/password login (via
// services/api.js).
function hasSession() {
  return !!localStorage.getItem("token");
}

/**
 * Session-state hook backed by localStorage.
 * @returns {{ isAuthenticated: boolean }}
 */
export default function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(hasSession);

  useEffect(() => {
    setIsAuthenticated(hasSession());
  }, []);

  return { isAuthenticated };
}
