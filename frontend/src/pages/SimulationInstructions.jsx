import Header from "../components/layout/Header";
import { useNavigate } from "react-router-dom";
import "./SimulationInstructions.css";

export default function SimulationInstructions() {
  const navigate = useNavigate();

  function handleClickNext() {
    navigate("/simulation/questions");
  }

  function handleClickBack() {
    navigate("/score");
  }

  return (
    <>
      <Header />
      <div className="instructions">
        <h1 className="instructions__title">Instruções do teste</h1>
        <div className="instructions__text">
          <p>Antes de começar</p>
          <p>
            Você está prestes a fazer um desafio técnico personalizado, criado a
            partir do seu currículo e da vaga que você indicou.
          </p>
          <br></br>
          <p>Como funciona:</p>
          <p>
            10 perguntas conceituais, baseadas no seu currículo e na vaga que
            você indicou. Nenhuma pede código, o foco é testar seu entendimento
            real, não sintaxe.
          </p>
          <br></br>
          <p>
            Responda com suas palavras. Não deixe em branco, isso conta como
            "não sei".
          </p>
          <br></br>
          <p>
            No final, você recebe seu score por habilidade, pontos fortes e de
            melhoria, e uma trilha de estudo priorizada pelas suas lacunas
            reais. Pronto pra começar?
          </p>
        </div>
        <div className="instructions__buttons">
          <button
            className="instructions__button--back"
            onClick={handleClickBack}
          >
            Voltar
          </button>
          <button
            className="instructions__button--forward"
            onClick={handleClickNext}
          >
            Começar
          </button>
        </div>
      </div>
    </>
  );
}
