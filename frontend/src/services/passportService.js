import { getUser, listMatches } from "./api";
import { listPassports } from "./talentPassportService";

// professional_profile.overall_level values (junior/mid_level/senior/expert).
const OVERALL_LEVEL_LABELS = {
  junior: "JÚNIOR",
  mid_level: "PLENO",
  senior: "SÊNIOR",
  expert: "ESPECIALISTA",
};

// professional_profile.competencies[].proficiency_level values, computed by
// the backend from the resume's confidence_level (beginner/intermediate/advanced/expert).
export const PROFICIENCY_LABELS = {
  beginner: "INICIANTE",
  intermediate: "INTERMEDIÁRIO",
  advanced: "AVANÇADO",
  expert: "EXPERT",
};

// Must match the number of stamp layouts in PassportCertificate.jsx.
const MAX_CARIMBOS = 6;

// Splits `total` stamps into (unlocked, locked) proportional to how many of
// the job's required skills the candidate matches vs. is missing, rounding
// so the two counts always add up to `total` (e.g. 8 matches / 2 gaps over 6
// stamps -> 5 unlocked, 1 locked).
function calcularDesbloqueados(total, quantidadeCompletas, quantidadeFaltantes) {
  const totalSkills = quantidadeCompletas + quantidadeFaltantes;
  if (totalSkills === 0) return total;
  return Math.round(total * (quantidadeCompletas / totalSkills));
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
  const competencias = (
    passport.professional_profile?.competencies || []
  ).slice(0, MAX_CARIMBOS);

  const matchesResponse = await listMatches();
  const match = (matchesResponse.data || []).find(
    (item) =>
      item.resume === passport.resume && item.job_posting === passport.job_posting,
  );
  const desbloqueados = calcularDesbloqueados(
    competencias.length,
    match?.matches?.length || 0,
    match?.gaps?.length || 0,
  );

  return {
    nome: nome || "",
    role: bestArea.toUpperCase(),
    title: OVERALL_LEVEL_LABELS[level] || level?.toUpperCase() || "",
    carimbos: competencias.map((competencia, index) => ({
      skill: competencia.skill,
      nivel: competencia.proficiency_level,
      validado: index < desbloqueados,
    })),
  };
}
