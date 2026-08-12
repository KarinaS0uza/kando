import { useState, useEffect } from "react";

// True if either session key is present. The two keys come from different
// login paths that don't otherwise interact: "token" is set directly by
// JoinForm.jsx on real email/password login (via services/api.js), while
// "kando_user" is set by this hook's own `login()`, called only from the
// mock Google-login path (GoogleButton.jsx). Checking both here is what
// lets ProtectedRoute treat either path as authenticated.
function hasSession() {
  return !!localStorage.getItem("token") || !!localStorage.getItem("kando_user");
}

/**
 * Session-state hook backed by localStorage.
 * @returns {{ isAuthenticated: boolean, login: (userData: object) => void, logout: () => void }}
 *   `login`/`logout` only read/write the "kando_user" key (see hasSession
 *   above) - the real email/password flow never calls them, it writes
 *   "token"/"user_id" directly instead.
 */
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
