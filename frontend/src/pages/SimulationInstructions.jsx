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
        <p className="instructions__text">
          Assessment Instruction. Lorem ipsum dolor sit amet, consectetur
          adipiscing elit. Quisque eu lacinia nibh. Vivamus cursus vestibulum
          mauris, vel fermentum ex sollicitudin at. Quisque at nunc arcu.
          Aliquam tempus metus nec quam congue pharetra. Aliquam posuere quam
          nisi, rutrum lacinia sapien congue a. Aliquam congue, nibh a ornare
          sagittis, tellus libero gravida elit, vel porttitor nulla purus a
          erat. Etiam blandit metus nec luctus lacinia.
        </p>
        <div className="instructions__buttons">
          <button
            className="instructions__button_back"
            onClick={handleClickBack}
          >
            Voltar
          </button>
          <button
            className="instructions__button_foward"
            onClick={handleClickNext}
          >
            Começar
          </button>
        </div>
      </div>
    </>
  );
}
