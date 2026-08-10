import * as React from "react";
import PropTypes from "prop-types";
import Backdrop from "@mui/material/Backdrop";
import Box from "@mui/material/Box";
import Modal from "@mui/material/Modal";
import { useSpring, animated } from "@react-spring/web";
import "./SimulationGateModal.css";
import CloseIcon from "@mui/icons-material/Close";

const Fade = React.forwardRef(function Fade(props, ref) {
  const {
    children,
    in: open,
    onClick,
    onEnter,
    onExited,
    ownerState: _ownerState,
    ...other
  } = props;
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

export default function SimulationGateModal({
  openModal,
  closeModal,
  newComparison,
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
            <div className="simulationGateModal">
              <button
                className="simulationGateModal__close_button"
                onClick={closeModal}
              >
                <CloseIcon sx={{ width: "20px" }} />
              </button>

              <h2 className="simulationGateModal__title">
                Simulado já realizado
              </h2>
              <p className="simulationGateModal__subtitle">
                Você já concluiu o seu simulado. Para gerar um novo, compare
                seu currículo com uma nova vaga.
              </p>
              <button
                className="simulationGateModal__button"
                onClick={newComparison}
              >
                Nova comparação
              </button>
            </div>
          </Box>
        </Fade>
      </Modal>
    </div>
  );
}

SimulationGateModal.propTypes = {
  openModal: PropTypes.bool.isRequired,
  closeModal: PropTypes.func.isRequired,
  newComparison: PropTypes.func.isRequired,
};
