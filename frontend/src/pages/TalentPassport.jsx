import { Award, Share2 } from "lucide-react";
import "./TalentPassport.css";

const DEFAULT_SKILLS = [
  { name: "React", adjective: "specialist" },
  { name: "Git", adjective: "confident" },
  { name: "Lógica", adjective: "sharp" },
  { name: "APIs", adjective: "fluent" },
  { name: "SQL", adjective: "expert" },
];

const imageModules = import.meta.glob("../assets/*.{png,jpg,jpeg,svg}", {
  eager: true,
});
const images = Object.values(imageModules).map((mod) => mod.default);

export default function TalentPassport({
  candidateName = "Nícolas Silva Gomes",
  roleTitle = "Frontend Developer — pronto para entrevistas",
  overallScore = 87,
  skills = DEFAULT_SKILLS,
  issueDate = "16/08/2026",
  verificationCode = "#KND-2026-0417",
}) {
  return (
    <div className="tp-wrapper">
      <div className="tp-card">
        <p className="tp-label">TALENT PASSPORT</p>

        <div className="tp-medallion">
          <Award size={32} />
        </div>

        <div className="tp-header">
          <p className="tp-name">{candidateName}</p>
          <p className="tp-role">{roleTitle}</p>
        </div>

        <div className="tp-stats">
          <div className="tp-stat">
            <p className="tp-stat-value">{overallScore}</p>
            <p className="tp-stat-label">score geral</p>
          </div>
          <div className="tp-stat">
            <p className="tp-stat-value">{skills.length}</p>
            <p className="tp-stat-label">habilidades validadas</p>
          </div>
        </div>

        <p className="tp-skills-label">selos de habilidade</p>

        <div className="tp-skills-grid">
          <div
            key={skills[0].name}
            className="tp-skill-badge"
            style={{ backgroundImage: `url(${images[0]})` }}
          >
            <div className="tp-skill-text">
              <p className="tp-skill-name">{skills[1].name}</p>
              <p className="tp-skill-adjective">{skills[1].adjective}</p>
            </div>
          </div>
          <div
            key={skills[0].name}
            className="tp-skill-badge tp-skill-badge-larger"
            style={{ backgroundImage: `url(${images[1]})` }}
          >
            <div className="tp-skill-text tp-skill-text-2">
              <p className="tp-skill-name">{skills[0].name}</p>
              <p className="tp-skill-adjective">{skills[0].adjective}</p>
            </div>
          </div>
          <div
            key={skills[0].name}
            className="tp-skill-badge tp-skill-badge-golden"
            style={{ backgroundImage: `url(${images[3]})` }}
          >
            <div className="tp-skill-text tp-skill-text-black">
              <p className="tp-skill-name">{skills[3].name}</p>
              <p className="tp-skill-adjective">{skills[4].adjective}</p>
            </div>
          </div>
        </div>

        <div className="tp-footer">
          <p className="tp-footer-date">emitido em {issueDate}</p>
          <p className="tp-footer-code">{verificationCode}</p>
        </div>
      </div>

      <button className="tp-share-button">
        <Share2 size={16} />
        Compartilhar passaporte
      </button>
    </div>
  );
}
