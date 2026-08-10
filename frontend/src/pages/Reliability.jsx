import Header from "../components/layout/Header";
import Slider from "../components/layout/Slider";
import { useNavigate } from "react-router-dom";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import "./Reliability.css";
import { useState } from "react";
import { waitForUploads, startMatch, startQuestions } from "../utils/uploadTracker";
import { submitReadinessSelfAssessment } from "../services/talentPassportService";
import { toast } from "react-hot-toast";

export default function Reliability() {
  const [isLoading, setIsLoading] = useState(false);
  const [perceivedPreparation, setPerceivedPreparation] = useState(50);
  const [applicationThreshold, setApplicationThreshold] = useState(50);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const [jobResult, resumeResult] = await waitForUploads();
      const hasError = [jobResult, resumeResult].some(
        (r) => r.status === "rejected",
      );

      if (hasError) {
        toast.error("Erro no upload anterior.");
        setIsLoading(false);
        return;
      }

      const resumeId = resumeResult.value.data.id;
      const jobId = jobResult.value.data.id;

      startMatch(resumeId, jobId);
      startQuestions(resumeId, jobId);

      try {
        await submitReadinessSelfAssessment(
          resumeId,
          jobId,
          perceivedPreparation,
          applicationThreshold,
        );
      } catch (error) {
        console.log(error);
      }

      navigate("/score/");
    } catch (error) {
      console.log(error);
      toast.error("Algo deu errado.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="rely">
        <h1 className="rely__title">Compare suas habilidades</h1>
        <form className="rely__form" onSubmit={handleSubmit}>
          <div className="rely__question-1">
            <p className="rely__question_title">
              1. O quão preparado você se sente para essa vaga?
            </p>
            <Slider value={perceivedPreparation} onChange={setPerceivedPreparation} />
          </div>
          <div className="rely__question-2">
            <p className="rely__question_title">
              2. Qual o percentual de requisitos da vaga você acha que deve
              alcançar antes de aplicar?
            </p>
            <Slider value={applicationThreshold} onChange={setApplicationThreshold} />
          </div>
          <button className="rely__compare-button">Comparar</button>
        </form>
      </div>
      {isLoading && (
        <div className="rely__overlay">
          <LoadingSpinner />
        </div>
      )}
    </>
  );
}
