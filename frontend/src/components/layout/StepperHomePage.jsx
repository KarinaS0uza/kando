import * as React from "react";
import Box from "@mui/material/Box";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import StepContent from "@mui/material/StepContent";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import tpImageHomepage from "../../assets/TP-image_homepage.png";

const steps = [
  {
    label: "Envie seu perfil",
    description: `Currículo e a vaga que você quer. A gente compara os dois e mostra sua compatibilidade.`,
  },
  {
    label: "Faça a simulação",
    description:
      "Um teste técnico gerado pra sua área, no seu nível, sem enrolação, direto no que importa.",
  },
  {
    label: "Estude com trilha personalizada",
    description: `Veja exatamente o que falta e siga uma trilha construída em cima dos seus gaps reais.`,
  },
  {
    label: "Desbloqueie o Talent Passport",
    description: ``,
  },
];

export default function VerticalLinearStepper() {
  const [activeStep, setActiveStep] = React.useState(0);

  const hasInteractedRef = React.useRef(false);

  const handleNext = () => {
    hasInteractedRef.current = true;
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    hasInteractedRef.current = true;
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    hasInteractedRef.current = true;
    setActiveStep(0);
  };

  const previousActiveStepRef = React.useRef(activeStep);
  const continueButtonRef = React.useRef(null);
  const backButtonRef = React.useRef(null);

  // Manage focus when the active step changes.
  React.useEffect(() => {
    const previousActiveStep = previousActiveStepRef.current;
    previousActiveStepRef.current = activeStep;

    // Only move focus in response to an actual click, never on mount
    // (including StrictMode's double-invoked mount effect in dev).
    if (!hasInteractedRef.current) {
      return;
    }

    // If the user is going forward.
    if (previousActiveStep < activeStep) {
      // Focus the "Continue" button, unless there's none to focus: the
      // stepper just finished, or landed on the last step (no buttons there).
      if (activeStep !== steps.length && activeStep !== steps.length - 1) {
        continueButtonRef.current.focus();
      }
      return;
    }
    // Otherwise, the user is going back.

    if (activeStep === 0) {
      // If the user hit "Back" on the second step, or hit "Reset", focus the "Continue" button.
      continueButtonRef.current.focus();
      return;
    }

    // Focus the "Back" button otherwise.
    backButtonRef.current.focus();
  }, [activeStep]);

  // The last step ("Desbloqueie o Talent Passport") has no buttons: reaching
  // it completes the cycle automatically.
  React.useEffect(() => {
    if (activeStep === steps.length - 1 && hasInteractedRef.current) {
      const timer = setTimeout(() => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [activeStep]);

  const [isRevealed, setIsRevealed] = React.useState(true);

  // When the stepper just finished, blink everything out and fade it back in.
  React.useEffect(() => {
    if (activeStep === steps.length && hasInteractedRef.current) {
      setIsRevealed(false);
      const timer = setTimeout(() => setIsRevealed(true), 120);
      return () => clearTimeout(timer);
    }
  }, [activeStep]);

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        opacity: isRevealed ? 1 : 0,
        transition: isRevealed ? "opacity 1s ease" : "opacity 0.6s ease",
      }}
    >
      <Stepper
        activeStep={activeStep}
        orientation="vertical"
        sx={{
          width: 400,
          flexShrink: 0,
          "& .MuiStepIcon-root.Mui-active": {
            color: "#26215c",
          },
          "& .MuiStepIcon-root.Mui-completed": {
            color: "#26215c",
          },
        }}
      >
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel
              onMouseEnter={
                index === 0 && activeStep === steps.length
                  ? handleReset
                  : undefined
              }
              sx={{
                textAlign: "left",
                cursor:
                  index === 0 && activeStep === steps.length
                    ? "pointer"
                    : undefined,
                "& .MuiStepLabel-label": {
                  textAlign: "left",
                },
                "&:hover .MuiStepLabel-label": {
                  color: "#26215c",
                  fontWeight: 600,
                },
                "&:hover .MuiStepLabel-iconContainer .MuiStepIcon-root": {
                  color: "#26215c",
                },
                transition: "color 0.2s ease",
              }}
            >
              {step.label}
              {index === steps.length - 1 && activeStep === steps.length && (
                <ArrowForwardIcon
                  fontSize="small"
                  sx={{
                    ml: 1,
                    verticalAlign: "middle",
                    color: "#26215c",
                  }}
                />
              )}
            </StepLabel>
            <StepContent>
              <Typography sx={{ textAlign: "left" }}>
                {step.description}
              </Typography>
              {index !== steps.length - 1 && (
                <Box sx={{ mb: 2, display: "flex", alignItems: "center" }}>
                  <IconButton
                    aria-label="Continue"
                    title="Continue"
                    onClick={handleNext}
                    sx={{
                      mt: 1,
                      mr: 1,
                      bgcolor: "#26215c",
                      color: "#fff",
                      "&:hover": { bgcolor: "#1c1946" },
                    }}
                    ref={continueButtonRef}
                  >
                    <ArrowDownwardIcon fontSize="small" />
                  </IconButton>
                  {index !== 0 && (
                    <IconButton
                      aria-label="Back"
                      title="Back"
                      onClick={handleBack}
                      sx={{
                        mt: 1,
                        mr: 1,
                        color: "#26215c",
                        border: "1px solid #26215c",
                      }}
                      ref={backButtonRef}
                    >
                      <ArrowUpwardIcon fontSize="small" />
                    </IconButton>
                  )}
                </Box>
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>
      <Paper
        square
        elevation={0}
        sx={{
          p: 3,
          display: "flex",
          flexDirection: "column",
          backgroundColor: "transparent",
        }}
      >
        <Box
          component="img"
          src={tpImageHomepage}
          alt="Talent Passport"
          sx={{
            width: 350,
            display: "block",
            filter:
              activeStep === steps.length ? "none" : "grayscale(1) blur(1px)",
            opacity: activeStep === steps.length ? 1 : 0.6,
            transition: "filter 0.4s ease, opacity 0.4s ease",
          }}
        />
      </Paper>
    </Box>
  );
}
