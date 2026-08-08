import { useEffect, useState } from "react";
import "./Header.css";
import { useLocation, useNavigate, Link } from "react-router-dom";
import logo from "../../assets/logo.svg";
import logoffIcon from "../../assets/logoff-icon.svg";
import { listMatches } from "../../services/api";

export default function Header({ menuActive }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [hasCompletedMatch, setHasCompletedMatch] = useState(false);

  useEffect(() => {
    if (menuActive) return;

    let cancelled = false;

    listMatches()
      .then((response) => {
        if (cancelled) return;
        const results = response.data || [];
        setHasCompletedMatch(results.some((match) => match.success));
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [menuActive]);

  const showMenu = menuActive || hasCompletedMatch;

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("kando_user");
    navigate("/", { replace: true });
  };

  return (
    <header className="header">
      <Link to="/dashboard" className="header__logo-link">
        <img className="header__tp-icon" src={logo} alt="Kando" />
      </Link>
      {showMenu && (
        <nav className="header__links">
          <Link
            to="/dashboard"
            className={`header__link ${pathname === "/dashboard" ? "header__link--active" : ""}`}
          >
            Dashboard
          </Link>
          <Link
            to="/upload"
            className={`header__link ${pathname === "/upload" ? "header__link--active" : ""}`}
          >
            Comparar vaga
          </Link>
          <Link
            to="/simulation/instructions"
            className={`header__link ${pathname === "/simulation/instructions" ? "header__link--active" : ""}`}
          >
            Simulado
          </Link>
          <Link
            to="/study-path"
            className={`header__link ${pathname === "/study-path" ? "header__link--active" : ""}`}
          >
            Trilha de estudo
          </Link>
          <Link
            to="/talent-passport"
            className={`header__link ${pathname === "/talent-passport" ? "header__link--active" : ""}`}
          >
            Talent Passport
          </Link>
        </nav>
      )}
      <button className="header__logoff-button" onClick={handleLogout}>
        <img className="header__logoff-icon" src={logoffIcon} alt="" />
        Sair
      </button>
    </header>
  );
}
