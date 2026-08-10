import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-hot-toast";
import { Timeline } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { PathIcon, CheckCircleIcon, StampIcon } from "@phosphor-icons/react";
import Header from "../components/layout/Header";
import LoadingOverlay from "../components/ui/LoadingOverlay";
import { listMatches } from "../services/api";
import { listPassports, createPassport } from "../services/talentPassportService";
import { buildStudySteps } from "../utils/studyPath";
import certificatePhoto from "../assets/TP-image_homepage.png";
import "./StudyPath.css";

const DEFAULT_TRACK_INFO = {
  titulo: "Sua trilha de estudo",
  introducao: "Passos sugeridos com base na comparação com a vaga",
};

const RESOURCE_LABELS = {
  curso: "Curso sugerido",
  certification: "Certificação sugerida",
  documentation: "Documentação",
  project_practice: "Prática de projeto sugerida",
};

export default function StudyPath() {
  const useAlternatingTimeline = useMediaQuery("(min-width: 701px)");
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [steps, setSteps] = useState([]);
  const [developedSkills, setDevelopedSkills] = useState([]);
  const [trackInfo, setTrackInfo] = useState(DEFAULT_TRACK_INFO);

  useEffect(() => {
    let cancelled = false;

    async function fetchStudyPath() {
      try {
        const matchesResponse = await listMatches();
        if (cancelled) return;

        const results = matchesResponse.data || [];
        if (results.length === 0) {
          setLoadError("empty");
          return;
        }

        const latest = results[0];
        if (!latest.success) {
          setLoadError("failed");
          return;
        }

        setDevelopedSkills(latest.matches || []);

        // The latest match defines "the current comparison" - find its
        // Talent Passport (generating one if it doesn't exist yet) rather
        // than trusting whichever passport happens to be most recent.
        const passportsResponse = await listPassports();
        if (cancelled) return;
        let passport = (passportsResponse.data || []).find(
          (item) =>
            item.resume === latest.resume &&
            item.job_posting === latest.job_posting,
        );

        if (!passport) {
          const createResponse = await createPassport(
            latest.resume,
            latest.job_posting,
          );
          if (cancelled) return;
          passport = createResponse.data;
        }

        const studyTrack = passport.study_track;
        if (!passport.success || !studyTrack?.success) {
          setLoadError("failed");
          return;
        }

        setSteps(buildStudySteps(studyTrack));
        if (studyTrack.title) {
          setTrackInfo({
            titulo: studyTrack.title,
            introducao: studyTrack.introduction || "",
          });
        }
      } catch (error) {
        console.log(error);
        if (!cancelled) {
          toast.error("Algo deu errado ao carregar sua trilha de estudo.");
          setLoadError("failed");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchStudyPath();

    return () => {
      cancelled = true;
    };
  }, []);

  const timelineItems = useMemo(() => {
    const items = [];
    let side = 0;
    if (developedSkills.length > 0) {
      const headerSide = side++;
      items.push({
        id: "skills-header",
        type: "skillsHeader",
        side: headerSide,
      });
      developedSkills.forEach((skill, i) =>
        items.push({
          id: `skill-${i}`,
          type: "skill",
          skill,
          side: headerSide,
        }),
      );
    }
    steps.forEach((step) =>
      items.push({ ...step, type: "step", side: side++ }),
    );
    if (items.length > 0) {
      items.push({ id: "final-stage", type: "finalStage", side: side++ });
    }
    return items;
  }, [developedSkills, steps]);

  if (isLoading) {
    return (
      <>
        <Header menuActive={true} />
        <LoadingOverlay />
      </>
    );
  }

  if (loadError === "empty") {
    return (
      <>
        <Header menuActive={true} />
        <div className="studyPath">
          <div className="studyPath__empty">
            <PathIcon size={48} color="#26215c" />
            <p className="studyPath__emptyText">
              Você ainda não comparou seu currículo com nenhuma vaga. Envie um
              currículo e uma vaga pra gerar sua trilha de estudo.
            </p>
            <Link to="/upload" className="studyPath__emptyButton">
              Comparar vaga
            </Link>
          </div>
        </div>
      </>
    );
  }

  if (loadError === "failed" || timelineItems.length === 0) {
    return (
      <>
        <Header menuActive={true} />
        <div className="studyPath">
          <div className="studyPath__empty">
            <PathIcon size={48} color="#26215c" />
            <p className="studyPath__emptyText">
              Não conseguimos montar sua trilha de estudo a partir da última
              análise. Tente rodar a comparação de novo.
            </p>
            <Link to="/dashboard" className="studyPath__emptyButton">
              Voltar ao dashboard
            </Link>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header menuActive={true} />
      <div className="studyPath">
        <h1 className="studyPath__title">{trackInfo.titulo}</h1>
        {trackInfo.introducao && (
          <p className="studyPath__subtitle">{trackInfo.introducao}</p>
        )}

        <Timeline
          className="studyPath__timeline"
          active={timelineItems.length}
          bulletSize={34}
          lineWidth={2}
          mt="md"
        >
          {timelineItems.map((item) => {
            if (item.type === "skillsHeader") {
              return (
                <Timeline.Item
                  key={item.id}
                  bullet={<CheckCircleIcon size={20} />}
                  title="Habilidades que você já tem"
                  color="green"
                  opposite={useAlternatingTimeline ? "" : undefined}
                  alternate={useAlternatingTimeline && item.side % 2 === 1}
                  classNames={{
                    itemBody: `studyPath__mainCard studyPath__skillsHeaderCard${
                      useAlternatingTimeline && item.side % 2 === 1
                        ? " studyPath__mainCard--left"
                        : ""
                    }`,
                    itemTitle:
                      "studyPath__skillsHeaderTitle studyPath__mainCardTitle",
                  }}
                />
              );
            }

            if (item.type === "skill") {
              return (
                <Timeline.Item
                  key={item.id}
                  title={item.skill}
                  color="green"
                  opposite={useAlternatingTimeline ? "" : undefined}
                  alternate={useAlternatingTimeline && item.side % 2 === 1}
                  style={{ "--tl-bullet-size": "14px" }}
                  classNames={{ itemTitle: "studyPath__skillTitle" }}
                />
              );
            }

            if (item.type === "finalStage") {
              return (
                <Timeline.Item
                  key={item.id}
                  bullet={<StampIcon size={18} />}
                  title="Passaporte carimbado"
                  color="green"
                  opposite={useAlternatingTimeline ? "" : undefined}
                  alternate={useAlternatingTimeline && item.side % 2 === 1}
                  classNames={{
                    itemBody: `studyPath__mainCard studyPath__finalCard${
                      useAlternatingTimeline && item.side % 2 === 1
                        ? " studyPath__mainCard--left"
                        : ""
                    }`,
                    itemTitle: "studyPath__mainCardTitle",
                  }}
                >
                  <img
                    className="studyPath__finalImage"
                    src={certificatePhoto}
                    alt="Passaporte de talento carimbado"
                  />
                  <p className="timeline__cardDescription">
                    Complete os passos acima e garanta seus carimbos.
                  </p>
                </Timeline.Item>
              );
            }

            return (
              <Timeline.Item
                key={item.id}
                bullet={<item.Icon size={17} />}
                title={item.title}
                opposite={useAlternatingTimeline ? "" : undefined}
                alternate={useAlternatingTimeline && item.side % 2 === 1}
                classNames={{
                  itemBody: `studyPath__mainCard${
                    useAlternatingTimeline && item.side % 2 === 1
                      ? " studyPath__mainCard--left"
                      : ""
                  }`,
                  itemTitle: "studyPath__mainCardTitle",
                }}
              >
                {item.description && (
                  <p className="timeline__cardDescription">
                    {item.description}
                  </p>
                )}
                {item.recurso && (
                  <p className="timeline__cardResource">
                    <strong>
                      {RESOURCE_LABELS[item.recurso.tipo] || "Recurso sugerido"}
                      :
                    </strong>{" "}
                    {item.recurso.sugestao}
                  </p>
                )}
              </Timeline.Item>
            );
          })}
        </Timeline>
      </div>
    </>
  );
}
