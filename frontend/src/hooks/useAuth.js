import { useState, useEffect } from "react";

export default function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem("kando_user"),
  );

  useEffect(() => {
    setIsAuthenticated(!!localStorage.getItem("kando_user"));
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
