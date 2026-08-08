import { useState, useEffect } from "react";

function hasSession() {
  return !!localStorage.getItem("token") || !!localStorage.getItem("kando_user");
}

export default function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(hasSession);

  useEffect(() => {
    setIsAuthenticated(hasSession());
  }, []);

  const login = (userData) => {
    localStorage.setItem("kando_user", JSON.stringify(userData));
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("kando_user");
    setIsAuthenticated(false);
  };

  return { isAuthenticated, login, logout };
}
