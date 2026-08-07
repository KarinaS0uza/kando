import {
  GraduationCapIcon,
  CodeIcon,
  WrenchIcon,
  BookOpenIcon,
  LightbulbIcon,
} from "@phosphor-icons/react";

const STEP_ICONS = [
  GraduationCapIcon,
  CodeIcon,
  WrenchIcon,
  BookOpenIcon,
  LightbulbIcon,
];

export function buildStudySteps(trackData) {
  const itens = Array.isArray(trackData?.itens) ? trackData.itens : [];

  return itens.map((item, i) => ({
    id: item.posicao ?? i,
    title: item.skill,
    description: item.motivacao ?? "",
    recurso:
      item.sugestao_recurso && item.tipo_recurso
        ? { tipo: item.tipo_recurso, sugestao: item.sugestao_recurso }
        : null,
    Icon: STEP_ICONS[i % STEP_ICONS.length],
  }));
}
