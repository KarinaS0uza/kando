import Header from "../components/layout/Header";
import Slider from "../components/layout/Slider";
import { useNavigate } from "react-router-dom";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import "./Reliability.css";
import { useState } from "react";
import { waitForUploads, startMatch } from "../utils/uploadTracker";
import { toast } from "react-hot-toast";

export default function Reliability() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      console.log("Valor do slider 1:", e.target[0].value);
      console.log("Valor do slider 2:", e.target[1].value);

      const [jobResult, resumeResult] = await waitForUploads();
      const hasError = [jobResult, resumeResult].some(
        (r) => r.status === "rejected"
      );

      if (hasError) {
        toast.error("Erro no upload anterior.");
        setIsLoading(false);
        return;
      }

      startMatch(resumeResult.value.data.id, jobResult.value.data.id);

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
            <Slider />
          </div>
          <div className="rely__question-2">
            <p className="rely__question_title">
              2. Qual o percentual de requisitos da vaga você acha que deve
              alcançar antes de aplicar?
            </p>
            <Slider />
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
