import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import { gradeAnswers, listAssessments } from "../services/simulationService";
import { waitForQuestions } from "../utils/uploadTracker";
import { toast } from "react-hot-toast";
import "./SimulationQuestions.css";
import LoadingOverlay from "../components/ui/LoadingOverlay";
import SimulationModal from "../components/layout/SimulationModal";

const MIN_LENGTH = 120;
const MAX_LENGTH = 1700;

export default function SimulationQuestions() {
  const [assessmentId, setAssessmentId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [questionText, setQuestionText] = useState("");
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const navigate = useNavigate();

  function getTextError(value) {
    if (value.trim() === "") {
      return "";
    } else if (value.trim().length < MIN_LENGTH) {
      return `Resposta muito curta. Mínimo de ${MIN_LENGTH} caracteres.`;
    } else if (value.length > MAX_LENGTH) {
      return `Resposta muito longa. Máximo de ${MAX_LENGTH} caracteres.`;
    }
    return "";
  }

  function isTextValid(value) {
    const trimmedLength = value.trim().length;
    return trimmedLength >= MIN_LENGTH && value.length <= MAX_LENGTH;
  }

  useEffect(() => {
    let cancelled = false;

    async function fetchQuestions() {
      try {
        // If Reliability already kicked off the assessment generation, await
        // that same in-flight request instead of firing a new one.
        const pending = waitForQuestions();
        let assessmentData;

        if (pending) {
          const response = await pending;
          if (cancelled) return;
          assessmentData = response.data;
        } else {
          // Otherwise (direct link, refresh, nav from the header) fall back
          // to the most recently generated assessment on record.
          const response = await listAssessments();
          if (cancelled) return;
          const results = response.data || [];
          if (results.length === 0) {
            toast.error("Nenhum teste disponível ainda.");
            navigate("/simulation/instructions");
            return;
          }
          assessmentData = results[0];
        }

        if (!assessmentData.success) {
          toast.error(
            assessmentData.error_message || "Não foi possível gerar o teste.",
          );
          navigate("/simulation/instructions");
          return;
        }

        setAssessmentId(assessmentData.id);
        setQuestions(assessmentData.questions || []);
      } catch (error) {
        console.log(error);
        toast.error("Algo deu errado ao carregar as questões.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchQuestions();
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  const currentQuestion = questions[currentIndex];
  const isLastQuestion = currentIndex === questions.length - 1;
  const isFirstQuestion = currentIndex === 0;

  const handleClickBack = () => {
    if (isFirstQuestion) {
      navigate("/simulation/instructions");
      return;
    }

    const updatedAnswers = { ...answers, [currentQuestion.id]: questionText };
    setAnswers(updatedAnswers);

    const prevIndex = currentIndex - 1;
    setCurrentIndex(prevIndex);
    setQuestionText(answers[questions[prevIndex].id] || "");
  };

  const saveAnswerAndContinue = async (answer) => {
    const updatedAnswers = { ...answers, [currentQuestion.id]: answer };
    setAnswers(updatedAnswers);

    if (isLastQuestion) {
      const formattedAnswers = Object.entries(updatedAnswers).map(
        ([questionId, answer]) => ({
          id: questionId,
          answer,
        }),
      );

      setSubmitting(true);
      try {
        await gradeAnswers(assessmentId, formattedAnswers);
      } catch (error) {
        console.log(error);
        toast.error("Algo deu errado ao enviar suas respostas.");
        return;
      } finally {
        setSubmitting(false);
      }

      localStorage.setItem("kando_simulation_completed", "true");
      window.dispatchEvent(new Event("simulation-completed"));
      setShowCompleteModal(true);
      return;
    }

    const nextIndex = currentIndex + 1;
    setCurrentIndex(nextIndex);
    setQuestionText(answers[questions[nextIndex].id] || "");
  };

  const handleClickNext = async () => {
    if (!isTextValid(questionText)) return;
    await saveAnswerAndContinue(questionText);
  };

  const handleSkipQuestion = async () => {
    await saveAnswerAndContinue("");
  };

  if (loading || !currentQuestion) {
    return (
      <>
        <Header />
        <LoadingOverlay />
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="simulation">
        <h1 className="simulation__title">Simulado</h1>
        <h2 className="simulation__question">Questão {currentIndex + 1}</h2>
        <p className="simulation__text">{currentQuestion.prompt}</p>
        <div className="simulation__input">
          <textarea
            className="simulation__input-txt"
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
          ></textarea>
          <div className="simulation__input-footer">
            <p className="simulation__input-error">
              {getTextError(questionText)}
            </p>
            <button
              type="button"
              className="simulation__skip-button"
              onClick={handleSkipQuestion}
              disabled={submitting}
            >
              Pular pergunta
            </button>
          </div>
        </div>
        <div className="simulation__buttons">
          <button className="simulation__button--back" onClick={handleClickBack}>
            Voltar
          </button>
          <p className="simulation__progress-counter">
            {currentIndex + 1}/{questions.length}
          </p>
          <button
            className="simulation__button--forward"
            onClick={handleClickNext}
            disabled={!isTextValid(questionText) || submitting}
          >
            {isLastQuestion ? "Finalizar" : "Avançar"}
          </button>
        </div>
      </div>
      {submitting && <LoadingOverlay />}
      <SimulationModal
        openModal={showCompleteModal}
        viewResults={() => navigate("/dashboard")}
      />
    </>
  );
}
