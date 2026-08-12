import * as React from "react";
import PropTypes from "prop-types";
import Backdrop from "@mui/material/Backdrop";
import Box from "@mui/material/Box";
import Modal from "@mui/material/Modal";
import { useSpring, animated } from "@react-spring/web";
import "./SimulationModal.css";
import CertificateIcon from "@mui/icons-material/CardMembership";
import RouteIcon from "@mui/icons-material/Route";
import LeaderboardIcon from "@mui/icons-material/Leaderboard";
import CloseIcon from "@mui/icons-material/Close";

const Fade = React.forwardRef(function Fade(props, ref) {
  const { children, in: open, onClick, onEnter, onExited, ...other } = props;
  const style = useSpring({
    from: { opacity: 0 },
    to: { opacity: open ? 1 : 0 },
    onStart: () => {
      if (open && onEnter) {
        onEnter(null, true);
      }
    },
    onRest: () => {
      if (!open && onExited) {
        onExited(null, true);
      }
    },
  });

  return (
    <animated.div ref={ref} style={style} {...other}>
      {React.cloneElement(children, { onClick })}
    </animated.div>
  );
});

Fade.propTypes = {
  children: PropTypes.element.isRequired,
  in: PropTypes.bool,
  onClick: PropTypes.any,
  onEnter: PropTypes.func,
  onExited: PropTypes.func,
  ownerState: PropTypes.any,
};

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  boxSizing: "border-box",
  width: { xs: "calc(100% - 32px)", sm: 350 },
  maxHeight: "calc(100dvh - 32px)",
  overflowY: "auto",
  bgcolor: "background.paper",
  border: "none",
  boxShadow: 24,
  p: { xs: 2, sm: 4 },
  "padding-top": 0,
};

export default function TestCompleteModal({
  openModal,
  closeModal,
  viewResults,
}) {
  return (
    <div>
      <Modal
        className="modal"
        aria-labelledby="spring-modal-title"
        aria-describedby="spring-modal-description"
        open={openModal}
        onClose={closeModal}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: { slots: { transition: Fade } },
        }}
      >
        <Fade in={openModal}>
          <Box sx={style}>
            <div className="simulation-modal">
              <button
                className="simulation-modal__close-button"
                onClick={closeModal}
              >
                <CloseIcon sx={{ width: "20px" }} />
              </button>

              <h2 className="simulation-modal__title">Parabéns!</h2>
              <p className="simulation-modal__subtitle">
                Agora você tem acesso à:
              </p>
              <ul className="simulation-modal__list">
                <li className="simulation-modal__item">
                  <LeaderboardIcon sx={{ color: "#26215c" }} />
                  Análise aprofundada
                </li>
                <li className="simulation-modal__item">
                  <RouteIcon sx={{ color: "#26215c" }} />
                  Trilha de estudo
                </li>
                <li className="simulation-modal__item">
                  <CertificateIcon sx={{ color: "#26215c" }} />
                  Talent Passport
                </li>
              </ul>
              <p className="simulation-modal__footer">
                Aproveite ao máximo os novos recursos. Boa sorte!
              </p>
              <button className="simulation-modal__button" onClick={viewResults}>
                Ver resultados
              </button>
            </div>
          </Box>
        </Fade>
      </Modal>
    </div>
  );
}
