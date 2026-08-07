import "./Header.css";
import { useNavigate, useLocation, Link } from "react-router-dom";
import logo from "../../assets/logo.svg";
import logoffIcon from "../../assets/logoff-icon.svg";

export default function Header({ menuActive }) {
  const { pathname } = useLocation();

  return (
    <header className="header">
      <Link to="/dashboard" className="header__logo-link">
        <img className="header__tp-icon" src={logo} alt="Kando" />
      </Link>
      {menuActive && (
        <nav className="header__links">
          <Link
            to="/dashboard"
            className={`header__link ${pathname === "/dashboard" ? "header__link--active" : ""}`}
          >
            Dashboard
          </Link>
          <Link className="header__link">Comparar vaga</Link>
          <Link className="header__link">Simulado</Link>
          <Link
            to="/study-path"
            className={`header__link ${pathname === "/study-path" ? "header__link--active" : ""}`}
          >
            Trilha de estudo
          </Link>
          <Link className="header__link">Talent Passport</Link>
        </nav>
      )}
      <button className="header__logoff-button">
        <img className="header__logoff-icon" src={logoffIcon} alt="" />
        Sair
      </button>
    </header>
  );
}
