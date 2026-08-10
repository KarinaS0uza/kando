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

export function buildStudySteps(studyTrack) {
  const items = Array.isArray(studyTrack?.items) ? studyTrack.items : [];

  return items.map((item, i) => ({
    id: item.position ?? i,
    title: item.skill,
    description: item.motivation ?? "",
    recurso:
      item.resource_suggestion && item.resource_type
        ? { tipo: item.resource_type, sugestao: item.resource_suggestion }
        : null,
    Icon: STEP_ICONS[i % STEP_ICONS.length],
  }));
}
