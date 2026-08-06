import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import { useEffect, useState } from "react";
import { toast } from "react-hot-toast";

import "./Score.css";
import ScoreModal from "../components/layout/ScoreModal";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import { waitForMatch } from "../utils/uploadTracker";
import Stack from "@mui/material/Stack";
import CircularProgress from "@mui/material/CircularProgress";

export default function ProfileScore() {
  const [isLoading, setIsLoading] = useState(true);

  const [percent, setPercent] = useState(0);
  const [gaps, setGaps] = useState([]);
  const [matches, setMatches] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    async function fetchMatch() {
      try {
        const response = await waitForMatch();
        if (cancelled) return;

        if (!response.data.success) {
          toast.error(
            response.data.error_message ||
              "Não foi possível calcular a compatibilidade."
          );
          return;
        }

        setPercent(response.data.overall_match_score ?? 0);
        setMatches(response.data.matches || []);
        setGaps(response.data.gaps || []);
      } catch (error) {
        console.log(error);
        toast.error("Algo deu errado ao carregar o resultado.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchMatch();

    return () => {
      cancelled = true;
    };
  }, []);

  function handleOpenModal() {
    setOpenModal(true);
  }

  function handleCloseModal() {
    setOpenModal(false);
  }

  function handleClick() {
    navigate("/simulation/instructions");
  }

  if (isLoading) {
    return (
      <>
        <Header />
        <div className="resultsPage">
          <LoadingSpinner />
        </div>
      </>
    );
  }

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
              value={percent}
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
            <p className="resultsPage__subtitle">{`${percent}%`}</p>
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
                {matches.map((r) => {
                  return <div className="results__skill">{r}</div>;
                })}
              </div>
            </div>
            <div className="results__gaps">
              <h2 className="results__title">A obter</h2>
              <span className="results__divider"></span>
              <div className="results__skills">
                {gaps.map((r) => {
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
