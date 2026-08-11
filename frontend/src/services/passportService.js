import { getUser } from "./api";
import { listPassports } from "./talentPassportService";

// professional_profile.overall_level values (junior/mid_level/senior/expert).
const OVERALL_LEVEL_LABELS = {
  junior: "JÚNIOR",
  mid_level: "PLENO",
  senior: "SÊNIOR",
  expert: "ESPECIALISTA",
};

// Stamp proficiency labels. "blocked" is applied by PassportCertificate.jsx
// itself whenever a stamp isn't validated, regardless of the score-derived
// bucket below.
export const PROFICIENCY_LABELS = {
  beginner: "INICIANTE",
  intermediate: "INTERMEDIÁRIO",
  advanced: "AVANÇADO",
  expert: "EXPERT",
  blocked: "A CONQUISTAR",
};

// Must match the number of stamp layouts in PassportCertificate.jsx.
const MAX_CARIMBOS = 6;

// A stamp is only unlocked once the candidate has demonstrated that skill in
// the assessment (dashboard_summary.performance_by_skill), not merely
// claimed it on the resume.
const SKILL_VALIDATION_THRESHOLD = 40;

// dashboard_summary.performance_by_skill score (0-100) -> proficiency bucket
// shown on the stamp when it's validated.
function nivelPorNota(nota) {
  if (nota >= 85) return "expert";
  if (nota >= 70) return "advanced";
  if (nota >= 50) return "intermediate";
  return "beginner";
}

export async function buscarDadosPassaporte() {
  const passportsResponse = await listPassports();
  const passport = (passportsResponse.data || []).find((item) => item.success);

  if (!passport) {
    throw new Error("Nenhum Talent Passport gerado ainda.");
  }

  const userId = localStorage.getItem("user_id");
  const nome = userId ? (await getUser(userId)).data.full_name : "";

  const level = passport.professional_profile?.overall_level;
  const bestArea = passport.dashboard_summary?.best_area || "";

  // Already sorted highest-to-lowest by the backend
  // (assessments/services/score_aggregation.consolidate_skills), so slicing
  // to MAX_CARIMBOS naturally keeps the best-demonstrated skills.
  const performanceBySkill = passport.dashboard_summary?.performance_by_skill || {};
  const carimbos = Object.entries(performanceBySkill)
    .slice(0, MAX_CARIMBOS)
    .map(([skill, nota]) => ({
      skill,
      nivel: nivelPorNota(nota),
      validado: nota >= SKILL_VALIDATION_THRESHOLD,
    }));

  return {
    nome: nome || "",
    role: bestArea.toUpperCase(),
    title: OVERALL_LEVEL_LABELS[level] || level?.toUpperCase() || "",
    carimbos,
  };
}
