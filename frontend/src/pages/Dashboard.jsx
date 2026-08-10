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

// Surfaces DRF's actual validation message (e.g. "A avaliação técnica ainda
// não foi gerada com sucesso.") instead of a generic fallback, since
// passport generation can legitimately fail while upstream steps (match,
// assessment) haven't been completed yet for the latest comparison.
function extractErrorMessage(error) {
  const data = error.response?.data;
  if (!data) return null;
  if (typeof data.detail === "string") return data.detail;
  const firstValue = Object.values(data)[0];
  if (Array.isArray(firstValue)) return firstValue[0];
  return typeof firstValue === "string" ? firstValue : null;
}

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
          <div className="metric-card">
            <p className="metric-card__label">Score do teste</p>
            <p className="metric-card__value">
              {technicalScore === null ? "—" : `${technicalScore}%`}
            </p>
          </div>
          <div className="metric-card">
            <p className="metric-card__label">Compatibilidade da última vaga</p>
            <p className="metric-card__value">
              {matchScore === null ? "—" : `${matchScore}%`}
            </p>
          </div>
          <div className="metric-card">
            <p className="metric-card__label">Nível</p>
            <p className="metric-card__value">{level || "—"}</p>
          </div>
          <div className="metric-card">
            <p className="metric-card__label">Melhor área</p>
            <p className="metric-card__value">{bestArea || "—"}</p>
          </div>
        </div>

        {summary && (
          <div className="dashboard__summary">
            <p>{summary}</p>
          </div>
        )}

        <div className="dashboard__grid">
          <div className="dashboard__column">
            <div className="panel__area">
              <h3 className="panel__title">Desempenho por área</h3>
              {areaPerformance.map((skill) => (
                <ScoreBar
                  key={skill.label}
                  label={skill.label}
                  value={skill.value}
                />
              ))}
            </div>

            <div className="panel">
              <h3 className="panel__title">Cargos recomendados</h3>
              {suggestedRoles.map((role, i) => (
                <div
                  key={role.title}
                  className={`role-row ${i < suggestedRoles.length - 1 ? "role-row--divider" : ""}`}
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
              {developmentAreas.map((item) => (
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
