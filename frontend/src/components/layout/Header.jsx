import { useEffect, useState } from "react";
import "./Header.css";
import { useLocation, useNavigate, Link } from "react-router-dom";
import logo from "../../assets/logo.svg";
import logoffIcon from "../../assets/logoff-icon.svg";
import { listMatches } from "../../services/api";
import SimulationGateModal from "./SimulationGateModal";

const SIMULATION_COMPLETED_KEY = "kando_simulation_completed";
const MATCH_COMPLETED_KEY = "kando_has_match";

export default function Header({ menuActive }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [hasCompletedMatch, setHasCompletedMatch] = useState(
    () => localStorage.getItem(MATCH_COMPLETED_KEY) === "true",
  );
  const [hasCompletedSimulation, setHasCompletedSimulation] = useState(
    () => localStorage.getItem(SIMULATION_COMPLETED_KEY) === "true",
  );
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showSimulationGateModal, setShowSimulationGateModal] = useState(false);

  useEffect(() => {
    // Once a match is known to exist (from this check or from Score/StudyPath
    // reporting one via "match-completed"), skip re-fetching it on every
    // page navigation - it never goes back to false.
    if (menuActive || hasCompletedMatch) return;

    let cancelled = false;

    listMatches()
      .then((response) => {
        if (cancelled) return;
        const results = response.data || [];
        if (results.some((match) => match.success)) {
          localStorage.setItem(MATCH_COMPLETED_KEY, "true");
          setHasCompletedMatch(true);
        }
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [menuActive, hasCompletedMatch]);

  const showMenu = menuActive || hasCompletedMatch;

  useEffect(() => {
    const updateSimulationStatus = () => {
      setHasCompletedSimulation(
        localStorage.getItem(SIMULATION_COMPLETED_KEY) === "true",
      );
    };
    const updateMatchStatus = () => {
      if (localStorage.getItem(MATCH_COMPLETED_KEY) === "true") {
        setHasCompletedMatch(true);
      }
    };

    window.addEventListener("simulation-completed", updateSimulationStatus);
    window.addEventListener("match-completed", updateMatchStatus);
    window.addEventListener("storage", updateSimulationStatus);
    window.addEventListener("storage", updateMatchStatus);

    return () => {
      window.removeEventListener(
        "simulation-completed",
        updateSimulationStatus,
      );
      window.removeEventListener("match-completed", updateMatchStatus);
      window.removeEventListener("storage", updateSimulationStatus);
      window.removeEventListener("storage", updateMatchStatus);
    };
  }, []);

  useEffect(() => {
    if (!isMenuOpen) return;

    const closeOnEscape = (event) => {
      if (event.key === "Escape") setIsMenuOpen(false);
    };

    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [isMenuOpen]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("kando_user");
    localStorage.removeItem(SIMULATION_COMPLETED_KEY);
    localStorage.removeItem(MATCH_COMPLETED_KEY);
    navigate("/", { replace: true });
  };

  const handleSimulationClick = (event) => {
    if (hasCompletedSimulation) {
      event.preventDefault();
      setShowSimulationGateModal(true);
    }
  };

  const handleNewComparison = () => {
    setShowSimulationGateModal(false);
    navigate("/upload");
  };

  return (
    <header className="header">
      <Link
        to={hasCompletedSimulation ? "/dashboard" : "/upload"}
        className="header__logo-link"
      >
        <img className="header__tp-icon" src={logo} alt="Kando" />
      </Link>
      {showMenu && (
        <button
          className={`header__menu-button ${isMenuOpen ? "header__menu-button--open" : ""}`}
          type="button"
          aria-label={isMenuOpen ? "Fechar menu" : "Abrir menu"}
          aria-controls="header-navigation"
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((open) => !open)}
        >
          <span />
          <span />
          <span />
        </button>
      )}
      {showMenu && (
        <nav
          id="header-navigation"
          className={`header__links ${isMenuOpen ? "header__links--open" : ""}`}
          aria-label="Navegação principal"
          onClick={() => setIsMenuOpen(false)}
        >
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
            onClick={handleSimulationClick}
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
      <button className="header__logoff-button" type="button" onClick={handleLogout}>
        <img className="header__logoff-icon" src={logoffIcon} alt="" />
        Sair
      </button>
      <SimulationGateModal
        openModal={showSimulationGateModal}
        closeModal={() => setShowSimulationGateModal(false)}
        newComparison={handleNewComparison}
      />
    </header>
  );
}
