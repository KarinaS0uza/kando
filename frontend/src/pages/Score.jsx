import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import { useState } from "react";

import "./Score.css";
import ScoreModal from "../components/layout/ScoreModal";
import Stack from "@mui/material/Stack";
import CircularProgress from "@mui/material/CircularProgress";

export default function ProfileScore() {
  const [isLoading, setIsLoading] = useState(false);

  const [percent, setPercent] = useState();
  const [gaps, setGaps] = useState([]);
  const [matches, setMatches] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  function handleOpenModal() {
    setOpenModal(true);
  }

  function handleCloseModal() {
    setOpenModal(false);
  }

  const getUserInfo = async (e) => {
    e.preventDefault();
    try {
      console.log();
    } catch (error) {
      console.log(error);
    }
  };
  const navigate = useNavigate();

  function handleClick() {
    navigate("/simulation/instructions");
  }

  const skills_test = ["HTML", "CSS", "React.js", "Node.js", "Next.js"];
  const percent__test = "56";

  return (
    <>
      <Header />
      <div className="resultsPage">
        <h1 className="resultsPage__title">Estou pronto para essa vaga?</h1>
        <div className="resultsPage__correspondence">
          <Stack spacing={2} direction="row">
            <CircularProgress
              enableTrackSlot
              variant="determinate"
              value={percent__test}
              aria-label="Export data"
              size={62}
              thickness={5}
              sx={{
                color: "#26215c",
                "& .MuiCircularProgress-circleTrack": {
                  color: "#26215c8e",
                },
              }}
            />
          </Stack>
          <div className="resultsPage__texts">
            <p className="resultsPage__subtitle">{`${percent__test}%`}</p>
            <p className="resultsPage__subtitle">
              de correspondência com a vaga
            </p>
          </div>
        </div>
        <section className="resultsPage__section">
          <div className="results">
            <div className="results__matches">
              <h2 className="results__title">Correspondências</h2>
              <span className="results__divider"></span>
              <div className="results__skills">
                {skills_test.map((r) => {
                  return <div className="results__skill">{r}</div>;
                })}
              </div>
            </div>
            <div className="results__gaps">
              <h2 className="results__title">A obter</h2>
              <span className="results__divider"></span>
              <div className="results__skills">
                {skills_test.map((r) => {
                  return (
                    <div className="results__skill results__skill_gaps">
                      {r}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          <button className="results__viewMore" onClick={handleOpenModal}>
            Ver mais
          </button>
        </section>
        {openModal && (
          <ScoreModal
            openModal={handleOpenModal}
            closeModal={handleCloseModal}
            beginTest={handleClick}
          />
        )}
      </div>
      <footer className="footer">
        <p className="footer__text">
          Faça o teste para um resultado mais preciso e desbloquear outros
          recursos
        </p>
        <button className="footer__button" onClick={handleClick}>
          Começar teste
        </button>
      </footer>
    </>
  );
}
