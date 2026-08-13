import { useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import StepContent from "@mui/material/StepContent";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import tpImageHomepage from "../../assets/TP-image_homepage.png";
import "./StepperHomePage.css";

// Scroll-driven vertical stepper on the landing page (HomePage), walking
// through the 4 product steps as the user scrolls past them. No props -
// content is fixed. Active step is derived from an IntersectionObserver
// rather than scroll-position math, so it stays correct regardless of
// step height.
const steps = [
  {
    label: "Envie seu perfil",
    description:
      "Currículo e a vaga que você quer. A gente compara os dois e mostra sua compatibilidade.",
  },
  {
    label: "Faça a simulação",
    description:
      "Um teste técnico gerado pra sua área, no seu nível, sem enrolação, direto no que importa.",
  },
  {
    label: "Estude com trilha personalizada",
    description:
      "Veja exatamente o que falta e siga uma trilha construída em cima dos seus gaps reais.",
  },
  {
    label: "Desbloqueie o Talent Passport",
    description:
      "Reúna suas conquistas e apresente sua evolução em um passaporte profissional.",
  },
];

export default function StepperHomePage() {
  const [activeStep, setActiveStep] = useState(0);
  const stepRefs = useRef([]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort(
            (a, b) =>
              Math.abs(a.boundingClientRect.top - window.innerHeight * 0.4) -
              Math.abs(b.boundingClientRect.top - window.innerHeight * 0.4),
          )[0];

        if (visibleEntry) {
          setActiveStep(Number(visibleEntry.target.dataset.stepIndex));
        }
      },
      {
        rootMargin: "-70% 0px -20% 0px",
        threshold: 0,
      },
    );

    const observedSteps = stepRefs.current.filter(Boolean);
    observedSteps.forEach((step) => observer.observe(step));

    return () => observer.disconnect();
  }, []);

  return (
    <Box className="scroll-stepper">
      <Stepper
        className="scroll-stepper__steps"
        activeStep={activeStep}
        orientation="vertical"
        sx={{
          "& .MuiStepIcon-root.Mui-active, & .MuiStepIcon-root.Mui-completed": {
            color: "#26215c",
          },
        }}
      >
        {steps.map((step, index) => (
          <Step
            key={step.label}
            ref={(node) => {
              stepRefs.current[index] = node;
            }}
            data-step-index={index}
            completed={index < activeStep}
            expanded={index <= activeStep}
            className={`scroll-stepper__step ${
              index <= activeStep ? "scroll-stepper__step--revealed" : ""
            } ${
              index === activeStep - 1
                ? "scroll-stepper__step--previous"
                : ""
            }`}
          >
            <StepLabel>
              {step.label}
            </StepLabel>
            <StepContent
              transitionDuration={index === steps.length - 1 ? 1600 : 800}
            >
              <Typography className="scroll-stepper__description">
                {step.description}
              </Typography>
              {index === steps.length - 1 && (
                <Paper
                  className={`scroll-stepper__visual ${
                    activeStep === steps.length - 1
                      ? "scroll-stepper__visual--revealed"
                      : ""
                  }`}
                  square
                  elevation={0}
                  aria-hidden={activeStep !== steps.length - 1}
                >
                  <Box
                    component="img"
                    src={tpImageHomepage}
                    alt="Talent Passport"
                    width="1448"
                    height="1086"
                    className="scroll-stepper__image"
                  />
                </Paper>
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
}
