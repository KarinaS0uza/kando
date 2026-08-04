import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import simulationService from "../services/simulationService";
import "./SimulationQuestions.css";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import SimulationModal from "../components/layout/SimulationModal";

const MIN_LENGTH = 120;
const MAX_LENGTH = 1700;

export default function SimulationQuestions() {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [questionText, setQuestionText] = useState("");
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
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
    simulationService.getQuestions().then((data) => {
      setQuestions(data);
      setLoading(false);
    });
  }, []);

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

  const handleClickNext = async () => {
    if (getTextError(questionText)) return;

    const updatedAnswers = { ...answers, [currentQuestion.id]: questionText };
    setAnswers(updatedAnswers);

    if (isLastQuestion) {
      const formattedAnswers = Object.entries(updatedAnswers).map(
        ([questionId, resposta]) => ({
          questionId,
          resposta,
        }),
      );
      await simulationService.submitAnswers(formattedAnswers);
      setShowCompleteModal(true);
      return;
    }

    const nextIndex = currentIndex + 1;
    setCurrentIndex(nextIndex);
    setQuestionText(answers[questions[nextIndex].id] || "");
  };

  if (loading || !currentQuestion) {
    return (
      <>
        <Header />
        <div className="rely__overlay">
          <LoadingSpinner />
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="simulation">
        <h1 className="simulation__title">Simulado</h1>
        <h2 className="simulation__question">Questão {currentIndex + 1}</h2>
        <p className="simulation__text">{currentQuestion.enunciado}</p>
        <div className="simulation__input">
          <textarea
            className="simulation__input-txt"
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
          ></textarea>
          <p className="simulation__input-error">
            {getTextError(questionText)}
          </p>
        </div>
        <div className="simulation__buttons">
          <button className="simulation__button_back" onClick={handleClickBack}>
            Voltar
          </button>
          <p className="simulation__progress_counter">
            {currentIndex + 1}/{questions.length}
          </p>
          <button
            className="simulation__button_foward"
            onClick={handleClickNext}
            disabled={!isTextValid(questionText)}
          >
            {isLastQuestion ? "Finalizar" : "Avançar"}
          </button>
        </div>
      </div>
      <SimulationModal
        openModal={showCompleteModal}
        closeModal={() => setShowCompleteModal(false)}
        viewResults={() => navigate("/report")}
      />
    </>
  );
}
