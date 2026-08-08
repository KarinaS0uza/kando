import "./HomePage.css";
import { Link } from "react-router-dom";
import logo from "../assets/logo-indigo.svg";
import heroPhoto from "../assets/Man_holding_certificate_in_office.jpeg";
import joinBackground from "../assets/join-background.png";
import stampHomepage from "../assets/stamp_homepage.png";
import StepperHomePage from "../components/layout/StepperHomePage";

export default function HomePage() {
  return (
    <div className="homepage">
      <header className="homepage__header">
        <Link to="/" className="homepage__logo">
          <img
            className="homepage__logo-icon"
            src={logo}
            alt="Talent Passport"
          />
          <span className="homepage__logo-title">Talent Passport</span>
        </Link>
        <nav className="homepage__nav">
          <Link
            to="/login"
            className="homepage__nav-button homepage__nav-button--outline"
          >
            Entrar
          </Link>
          <Link
            to="/signup"
            className="homepage__nav-button homepage__nav-button--solid"
          >
            Cadastre-se
          </Link>
        </nav>
      </header>
      <main className="homepage__main">
        <section className="homepage__hero">
          <div className="homepage__hero-content">
            <h1 className="homepage__headline">
              Pare de adivinhar se você está pronto.
            </h1>
            <p className="homepage__subtext">
              Seu currículo. A vaga. <br></br>A diferença entre os dois.
            </p>
            <Link to="/signup" className="homepage__cta">
              Começar agora
            </Link>
          </div>
          <img className="homepage__hero-photo" src={heroPhoto} alt="" />
        </section>
        <section className="homepage__description">
          <div className="homepage__description-gradient" />
          <div className="homepage__stepper">
            <StepperHomePage />
          </div>
        </section>
        <div className="homepage__enter">
          <div
            className="login__form-background"
            style={{ backgroundImage: `url(${joinBackground})` }}
          />
          <div className="homepage__enter-title">
            <h2>Estou pronto para a próxima vaga?</h2>
            <img className="homepage__enter-stamp" src={stampHomepage} alt="" />
          </div>
          <Link to="/signup" className="homepage__enter-cta">
            Descobrir agora
          </Link>
        </div>
      </main>
      <footer className="homepage__footer">
        <div className="homepage__footer-team">
          <span className="homepage__footer-team-label">Construído por:</span>
          <a
            href="https://www.linkedin.com/in/andreia-lima-4a8747168/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Andreia Lima
          </a>
          <a
            href="https://www.linkedin.com/in/kar1na-souza/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Karina Souza
          </a>
          <a
            href="https://www.linkedin.com/in/nicolas-sg-br/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Nícolas Gomes
          </a>
        </div>
        <hr className="homepage__footer-divider" />
        <div className="homepage__footer_description">
          <p>Time KANdo</p>
          <p>|</p>
          <p>Projeto Talent Passport</p>
          <p>|</p>
          <p>Hackathon Comunidade Juninhos &amp; Nortjobs</p>
          <p>|</p>
          <p>©2026</p>
        </div>
      </footer>
    </div>
  );
}
