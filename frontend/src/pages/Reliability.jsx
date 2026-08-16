import Header from "../components/layout/Header";
import Slider from "../components/layout/Slider";
import { useNavigate } from "react-router-dom";
import LoadingOverlay from "../components/ui/LoadingOverlay";
import "./Reliability.css";
import { useEffect, useState } from "react";
import {
  waitForUploads,
  startMatch,
  startQuestions,
} from "../utils/uploadTracker";
import { submitReadinessSelfAssessment } from "../services/talentPassportService";
import { Toaster, toast } from "react-hot-toast";
import { extractErrorMessage } from "../utils/errors";

function getUploadError(result, fallback) {
  if (result.status !== "rejected") return null;
  return extractErrorMessage(result.reason) || fallback;
}

function getUploadErrors(jobResult, resumeResult) {
  return [
    getUploadError(jobResult, "Não foi possível processar a vaga."),
    getUploadError(resumeResult, "Não foi possível processar o currículo."),
  ].filter(Boolean);
}

export default function Reliability() {
  const [isLoading, setIsLoading] = useState(false);
  const [perceivedPreparation, setPerceivedPreparation] = useState(50);
  const [applicationThreshold, setApplicationThreshold] = useState(50);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    waitForUploads().then(([jobResult, resumeResult]) => {
      if (cancelled) return;

      const uploadErrors = getUploadErrors(jobResult, resumeResult);
      if (uploadErrors.length > 0) {
        navigate("/upload", {
          replace: true,
          state: { uploadError: uploadErrors.join("\n") },
        });
      }
    });

    return () => {
      cancelled = true;
    };
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const [jobResult, resumeResult] = await waitForUploads();
      const uploadErrors = getUploadErrors(jobResult, resumeResult);
      if (uploadErrors.length > 0) {
        navigate("/upload", {
          replace: true,
          state: { uploadError: uploadErrors.join("\n") },
        });
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
      <Toaster
        position="top-right"
        containerStyle={{
          top: 64,
          left: 12,
          right: 12,
          zIndex: 11000,
        }}
        toastOptions={{
          style: {
            maxWidth: "min(420px, calc(100vw - 24px))",
            overflowWrap: "anywhere",
          },
        }}
      />
      <Header />
      <div className="rely">
        <h1 className="rely__title">Compare suas habilidades</h1>
        <form className="rely__form" onSubmit={handleSubmit}>
          <div className="rely__question--1">
            <p className="rely__question-title">
              1. O quão preparado você se sente para essa vaga?
            </p>
            <Slider
              value={perceivedPreparation}
              onChange={setPerceivedPreparation}
            />
          </div>
          <div className="rely__question--2">
            <p className="rely__question-title">
              2. Qual o percentual de requisitos da vaga você acha que deve
              alcançar antes de aplicar?
            </p>
            <Slider
              value={applicationThreshold}
              onChange={setApplicationThreshold}
            />
          </div>
          <button className="rely__compare-button">Comparar</button>
        </form>
      </div>
      {isLoading && <LoadingOverlay />}
    </>
  );
}
