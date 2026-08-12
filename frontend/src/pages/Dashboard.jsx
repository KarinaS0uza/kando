import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import Header from "../components/layout/Header";
import LoadingOverlay from "../components/ui/LoadingOverlay";
import { listMatches } from "../services/api";
import {
  createPassport,
  listPassports,
} from "../services/talentPassportService";
import { extractErrorMessage } from "../utils/errors";
import "./Dashboard.css";

const LEVEL_LABELS = {
  beginner: "Iniciante",
  intermediate: "Intermediário",
  advanced: "Avançado",
  expert: "Especialista",
  mid_level: "Pleno",
};

// A role's fit is highlighted once its match crosses the same "alta
// compatibilidade" threshold used for the overall score elsewhere in the app.
const ROLE_HIGHLIGHT_THRESHOLD = 70;

function ScoreBar({ label, value }) {
  return (
    <div className="dashboard__score-bar">
      <span className="dashboard__score-bar-label">{label}</span>
      <div className="dashboard__score-bar-track">
        <div className="dashboard__score-bar-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [technicalScore, setTechnicalScore] = useState(null);
  const [matchScore, setMatchScore] = useState(null);
  const [level, setLevel] = useState(null);
  const [bestArea, setBestArea] = useState(null);
  const [summary, setSummary] = useState("");
  const [areaPerformance, setAreaPerformance] = useState([]);
  const [suggestedRoles, setSuggestedRoles] = useState([]);
  const [strengths, setStrengths] = useState([]);
  const [developmentAreas, setDevelopmentAreas] = useState([]);

  useEffect(() => {
    let cancelled = false;

    async function fetchDashboard() {
      try {
        // The latest match defines "the current comparison" - not whichever
        // passport happens to be most recent, since an older comparison may
        // already have one while this one doesn't yet.
        const matchesResponse = await listMatches();
        if (cancelled) return;
        const latestMatch = (matchesResponse.data || [])[0];
        if (!latestMatch || !latestMatch.success) return;

        const passportsResponse = await listPassports();
        if (cancelled) return;
        let passport = (passportsResponse.data || []).find(
          (item) =>
            item.resume === latestMatch.resume &&
            item.job_posting === latestMatch.job_posting,
        );

        if (!passport) {
          // No Talent Passport yet for this specific comparison - generate
          // one, since nothing else in the app triggers this generation.
          const createResponse = await createPassport(
            latestMatch.resume,
            latestMatch.job_posting,
          );
          if (cancelled) return;
          passport = createResponse.data;
        }

        if (!passport.success) {
          toast.error(
            passport.error_message ||
              "Não foi possível gerar seu Talent Passport.",
          );
          return;
        }

        const dashboardSummary = passport.dashboard_summary || {};
        const profile = passport.professional_profile || {};
        const recommendations = passport.career_recommendations || {};

        setTechnicalScore(dashboardSummary.technical_performance ?? null);
        setMatchScore(dashboardSummary.job_compatibility ?? null);
        setBestArea(dashboardSummary.best_area || null);
        setSummary(dashboardSummary.summary_feedback || "");
        setAreaPerformance(
          Object.entries(dashboardSummary.performance_by_area || {}).map(
            ([label, value]) => ({ label, value }),
          ),
        );
        setLevel(
          LEVEL_LABELS[profile.overall_level] || profile.overall_level || null,
        );
        setStrengths(profile.strengths || []);
        setDevelopmentAreas(profile.development_areas || []);
        setSuggestedRoles(
          (recommendations.suggested_roles || []).map((role) => ({
            title: role.job_title,
            fit: role.rationale,
            highlight: (role.match_percentage ?? 0) >= ROLE_HIGHLIGHT_THRESHOLD,
          })),
        );
      } catch (error) {
        console.log(error);
        toast.error(
          extractErrorMessage(error) ||
            "Algo deu errado ao carregar seu dashboard.",
        );
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  if (isLoading) {
    return (
      <>
        <Header menuActive={true} />
        <LoadingOverlay />
      </>
    );
  }

  return (
    <>
      <Header menuActive={true} />
      <div className="dashboard">
        <h1 className="dashboard__title">Dashboard</h1>

        <div className="dashboard__metrics">
          <div className="dashboard__metric-card">
            <p className="dashboard__metric-card-label">Score do teste</p>
            <p className="dashboard__metric-card-value">
              {technicalScore === null ? "—" : `${technicalScore}%`}
            </p>
          </div>
          <div className="dashboard__metric-card">
            <p className="dashboard__metric-card-label">Compatibilidade da última vaga</p>
            <p className="dashboard__metric-card-value">
              {matchScore === null ? "—" : `${matchScore}%`}
            </p>
          </div>
          <div className="dashboard__metric-card">
            <p className="dashboard__metric-card-label">Nível</p>
            <p className="dashboard__metric-card-value">{level || "—"}</p>
          </div>
          <div className="dashboard__metric-card">
            <p className="dashboard__metric-card-label">Melhor área</p>
            <p className="dashboard__metric-card-value">{bestArea || "—"}</p>
          </div>
        </div>

        {summary && (
          <div className="dashboard__summary">
            <p>{summary}</p>
          </div>
        )}

        <div className="dashboard__grid">
          <div className="dashboard__column">
            <div className="dashboard__panel-area">
              <h3 className="dashboard__panel-title">Desempenho por área</h3>
              {areaPerformance.map((skill) => (
                <ScoreBar
                  key={skill.label}
                  label={skill.label}
                  value={skill.value}
                />
              ))}
            </div>

            <div className="dashboard__panel">
              <h3 className="dashboard__panel-title">Cargos recomendados</h3>
              <div className="dashboard__role-list">
                {suggestedRoles.map((role, i) => (
                  <div
                    key={role.title}
                    className={`dashboard__role-row ${i < suggestedRoles.length - 1 ? "dashboard__role-row--divider" : ""}`}
                  >
                    <span className="dashboard__role-row-title">{role.title}</span>
                    <span
                      className={`dashboard__role-row-fit ${role.highlight ? "dashboard__role-row-fit--highlight" : ""}`}
                    >
                      {role.fit}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="dashboard__column">
            <div className="dashboard__panel dashboard__panel--compact">
              <h3 className="dashboard__panel-title">
                <i
                  className="ti ti-check dashboard__panel-icon dashboard__panel-icon--positive"
                  aria-hidden="true"
                />
                Pontos fortes
              </h3>
              {strengths.map((item) => (
                <p key={item} className="dashboard__panel-item dashboard__panel-item--positive">
                  {item}
                </p>
              ))}
            </div>

            <div className="dashboard__panel dashboard__panel--compact">
              <h3 className="dashboard__panel-title">
                <i
                  className="ti ti-alert-triangle dashboard__panel-icon dashboard__panel-icon--warning"
                  aria-hidden="true"
                />
                Pra estudar
              </h3>
              {developmentAreas.map((item) => (
                <p key={item} className="dashboard__panel-item dashboard__panel-item--warning">
                  {item}
                </p>
              ))}
            </div>
          </div>
        </div>

        <div className="dashboard__actions">
          <button className="dashboard__btn" onClick={() => navigate("/study-path")}>
            Ver trilha de estudo
            <i className="ti ti-arrow-right" aria-hidden="true" />
          </button>
          <button className="dashboard__btn" onClick={() => navigate("/talent-passport")}>
            <i className="ti ti-stamp" aria-hidden="true" />
            Ver passaporte
          </button>
        </div>
      </div>
    </>
  );
}
