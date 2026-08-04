import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import "./Dashboard.css";

const skillScores = [
  { label: "Front end", value: 75 },
  { label: "Back end", value: 60 },
  { label: "Lógica", value: 85 },
  { label: "SQL", value: 30 },
];

const strengths = ["Lógica de programação", "Componentização em React"];
const gaps = ["Consultas SQL com joins", "Otimização de queries"];

const recommendedRoles = [
  { title: "Front-end júnior", fit: "alta aderência", highlight: true },
  { title: "Back-end júnior", fit: "precisa evoluir em SQL", highlight: false },
];

function ScoreBar({ label, value }) {
  return (
    <div className="score-bar">
      <span className="score-bar__label">{label}</span>
      <div className="score-bar__track">
        <div className="score-bar__fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default function AssessmentDashboard({
  score = 62,
  level = "Intermediário",
  bestArea = "Lógica",
  summary = "Você foi bem em lógica e front end, mas errou a maioria das questões de SQL — isso puxou sua média pra baixo.",
}) {
  const navigate = useNavigate();

  return (
    <>
      <Header menuActive={true} />
      <div className="dashboard">
        <h1 className="dashboard__title">Dashboard</h1>

        <div className="dashboard__metrics">
          <div className="metric-card">
            <p className="metric-card__label">Score do teste</p>
            <p className="metric-card__value">{score}%</p>
          </div>
          <div className="metric-card">
            <p className="metric-card__label">Nível</p>
            <p className="metric-card__value">{level}</p>
          </div>
          <div className="metric-card">
            <p className="metric-card__label">Melhor área</p>
            <p className="metric-card__value">{bestArea}</p>
          </div>
        </div>

        <div className="dashboard__summary">
          <p>{summary}</p>
        </div>

        <div className="dashboard__grid">
          <div className="dashboard__column">
            <div className="panel__area">
              <h3 className="panel__title">Desempenho por área</h3>
              {skillScores.map((skill) => (
                <ScoreBar
                  key={skill.label}
                  label={skill.label}
                  value={skill.value}
                />
              ))}
            </div>

            <div className="panel">
              <h3 className="panel__title">Cargos recomendados</h3>
              {recommendedRoles.map((role, i) => (
                <div
                  key={role.title}
                  className={`role-row ${i < recommendedRoles.length - 1 ? "role-row--divider" : ""}`}
                >
                  <span className="role-row__title">{role.title}</span>
                  <span
                    className={`role-row__fit ${role.highlight ? "role-row__fit--highlight" : ""}`}
                  >
                    {role.fit}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="dashboard__column">
            <div className="panel panel--compact">
              <h3 className="panel__title">
                <i
                  className="ti ti-check panel__icon panel__icon--positive"
                  aria-hidden="true"
                />
                Pontos fortes
              </h3>
              {strengths.map((item) => (
                <p key={item} className="panel__item panel__item--positive">
                  {item}
                </p>
              ))}
            </div>

            <div className="panel panel--compact">
              <h3 className="panel__title">
                <i
                  className="ti ti-alert-triangle panel__icon panel__icon--warning"
                  aria-hidden="true"
                />
                Pra estudar
              </h3>
              {gaps.map((item) => (
                <p key={item} className="panel__item panel__item--warning">
                  {item}
                </p>
              ))}
            </div>
          </div>
        </div>

        <div className="dashboard__actions">
          <button className="btn" onClick={() => navigate("/study-path")}>
            Ver trilha de estudo
            <i className="ti ti-arrow-right" aria-hidden="true" />
          </button>
          <button className="btn" onClick={() => navigate("/talent-passport")}>
            <i className="ti ti-stamp" aria-hidden="true" />
            Ver passaporte
          </button>
        </div>
      </div>
    </>
  );
}
