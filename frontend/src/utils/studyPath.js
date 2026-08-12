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

/**
 * Maps a backend study-track payload into the step list StudyPath.jsx
 * renders in its Mantine Timeline.
 * @param {{items?: Array<{position?: number, skill: string, motivation?: string, resource_suggestion?: string, resource_type?: string}>}} studyTrack
 * @returns {Array<{id: number, title: string, description: string, recurso: {tipo: string, sugestao: string}|null, Icon: React.ComponentType}>}
 *   `Icon` cycles round-robin through a fixed 5-icon set by position in the
 *   list - it has no semantic link to the skill/step type.
 */
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
