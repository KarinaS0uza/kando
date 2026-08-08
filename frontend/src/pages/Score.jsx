import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import { useEffect, useRef, useState } from "react";
import { toast } from "react-hot-toast";

import "./Score.css";
import ScoreModal from "../components/layout/ScoreModal";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import { waitForMatch } from "../utils/uploadTracker";
import { listMatches } from "../services/api";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

const CIRCLE_SIZE = 250;
const CIRCLE_THICKNESS = 3;

// Keeps each line's touch point within its own side of the circle instead
// of swinging toward the other label as the score approaches 0% or 100%.
// Matches stays within [0%, 30%]; gaps stays within [70%, 100%].
const MATCHES_MAX_FRACTION = 0.25;
const GAPS_MIN_FRACTION = 0.75;

// Point on the ring at `fraction` (0-1) of the way clockwise from the top.
function pointOnCircle(cx, cy, radius, fraction) {
  const angle = fraction * 2 * Math.PI;
  return {
    x: cx + radius * Math.sin(angle),
    y: cy - radius * Math.cos(angle),
  };
}

const LINE_END_GAP = 8;

// Pulls both ends of a segment inward by `gap` px so the line's tips don't
// visually touch the elements it connects.
function shrinkLineEnds(x1, y1, x2, y2, gap) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.hypot(dx, dy);
  if (length === 0) return { x1, y1, x2, y2 };

  const ux = dx / length;
  const uy = dy / length;
  const clampedGap = Math.min(gap, length / 2);

  return {
    x1: x1 + ux * clampedGap,
    y1: y1 + uy * clampedGap,
    x2: x2 - ux * clampedGap,
    y2: y2 - uy * clampedGap,
  };
}

// MUI's CircularProgress always renders its <circle> in a fixed
// "22 22 44 44" viewBox, then rotates the whole SVG -90deg via CSS so the
// arc appears to start at 12 o'clock. A gradient placed on that circle has
// to be defined in that same pre-rotation space (angle 0 = 3 o'clock,
// sweeping toward 6 o'clock as it grows) for it to end up following the
// visible arc once the rotation is applied.
const MUI_PROGRESS_CENTER = 44;
const MUI_PROGRESS_RADIUS = 20.5;

function progressGradientEndpoint(fraction) {
  const angle = fraction * 2 * Math.PI;
  return {
    x: MUI_PROGRESS_CENTER + MUI_PROGRESS_RADIUS * Math.cos(angle),
    y: MUI_PROGRESS_CENTER + MUI_PROGRESS_RADIUS * Math.sin(angle),
  };
}

const COMPATIBILITY_LEVELS = [
  { label: "baixa", color: "#d64550", background: "rgba(214, 69, 80, 0.12)" },
  { label: "média", color: "#e08a1e", background: "rgba(224, 138, 30, 0.12)" },
  {
    label: "alta",
    color: "rgb(79, 122, 79)",
    background: "rgb(92%, 95%, 87%)",
  },
];

function getCompatibilityLevel(percent) {
  const index = percent >= 70 ? 2 : percent >= 40 ? 1 : 0;
  const level = COMPATIBILITY_LEVELS[index];
  const nextLevel = COMPATIBILITY_LEVELS[index + 1];

  return {
    ...level,
    gradientFrom: level.color,
    gradientTo: nextLevel ? nextLevel.color : level.color,
  };
}

export default function ProfileScore() {
  const [isLoading, setIsLoading] = useState(true);
  const [percent, setPercent] = useState(0);
  const [gaps, setGaps] = useState([]);
  const [matches, setMatches] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [lines, setLines] = useState([]);

  const navigate = useNavigate();

  const wrapperRef = useRef(null);
  const circleRef = useRef(null);
  const gapsTitleRef = useRef(null);
  const matchesTitleRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchMatch() {
      try {
        // If a match was just started by the Reliability step, await that
        // same in-flight request so we get its result with no extra
        // round-trip and no race with the POST that creates it.
        const pending = waitForMatch();
        let matchData;

        if (pending) {
          const response = await pending;
          if (cancelled) return;
          matchData = response.data;
        } else {
          // Otherwise (direct link, refresh, nav from the header) always
          // load the most recent match on record.
          const response = await listMatches();
          if (cancelled) return;
          const results = response.data || [];
          if (results.length === 0) {
            toast.error(
              "Você ainda não comparou seu currículo com nenhuma vaga.",
            );
            return;
          }
          matchData = results[0];
        }

        if (!matchData.success) {
          toast.error(
            matchData.error_message ||
              "Não foi possível calcular a compatibilidade.",
          );
          return;
        }

        setPercent(matchData.overall_match_score ?? 0);
        setMatches(matchData.matches || []);
        setGaps(matchData.gaps || []);
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

  useEffect(() => {
    if (isLoading) return;

    function calculateLines() {
      const wrapper = wrapperRef.current?.getBoundingClientRect();
      const circle = circleRef.current?.getBoundingClientRect();
      const gapsTitle = gapsTitleRef.current?.getBoundingClientRect();
      const matchesTitle = matchesTitleRef.current?.getBoundingClientRect();
      if (!wrapper || !circle || !gapsTitle || !matchesTitle) return;

      const cx = circle.left + circle.width / 2 - wrapper.left;
      const cy = circle.top + circle.height / 2 - wrapper.top;
      const radius = circle.width / 2 - CIRCLE_THICKNESS / 2;

      // Matches (the "#26215c" arc) spans 0 -> percent; gaps (the "#e0e0e0"
      // arc) spans percent -> 100. Each line touches the ring at the
      // angular midpoint of the arc it represents, capped so it doesn't
      // swing past the other side's territory.
      const matchesFraction = Math.min(percent / 2 / 100, MATCHES_MAX_FRACTION);
      const gapsFraction = Math.max(
        (percent + 100) / 2 / 100,
        GAPS_MIN_FRACTION,
      );

      const matchesPoint = pointOnCircle(cx, cy, radius, matchesFraction);
      const gapsPoint = pointOnCircle(cx, cy, radius, gapsFraction);

      const gapsLine = shrinkLineEnds(
        gapsTitle.right - wrapper.left,
        gapsTitle.top + gapsTitle.height / 2 - wrapper.top,
        gapsPoint.x,
        gapsPoint.y,
        LINE_END_GAP,
      );
      const matchesLine = shrinkLineEnds(
        matchesTitle.left - wrapper.left,
        matchesTitle.top + matchesTitle.height / 2 - wrapper.top,
        matchesPoint.x,
        matchesPoint.y,
        LINE_END_GAP,
      );

      setLines([
        { ...gapsLine, dotColor: "#c4c4c4" },
        { ...matchesLine, dotColor: "rgb(79, 122, 79)" },
      ]);
    }

    const raf = requestAnimationFrame(calculateLines);

    // A window "resize" only fires for viewport changes. Anything else that
    // reshuffles these elements (a CSS edit picked up via HMR, fonts
    // finishing their load, item lists changing height, ...) needs to
    // trigger a recalculation too, so watch the elements themselves.
    const observer = new ResizeObserver(calculateLines);
    [wrapperRef, circleRef, gapsTitleRef, matchesTitleRef].forEach((ref) => {
      if (ref.current) observer.observe(ref.current);
    });

    window.addEventListener("resize", calculateLines);
    return () => {
      cancelAnimationFrame(raf);
      observer.disconnect();
      window.removeEventListener("resize", calculateLines);
    };
  }, [isLoading, percent]);

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

  const compatibility = getCompatibilityLevel(percent);
  const gradientStart = progressGradientEndpoint(0);
  const gradientEnd = progressGradientEndpoint(percent / 100);

  return (
    <>
      <Header />
      <div className="resultsPage">
        <h1 className="resultsPage__title">Estou pronto para essa vaga?</h1>

        <div ref={wrapperRef} className="skillCompare__wrapper">
          <svg className="skillCompare__svg">
            {lines.map((l, i) => (
              <g key={i}>
                <line
                  x1={l.x1}
                  y1={l.y1}
                  x2={l.x2}
                  y2={l.y2}
                  stroke="#c4c4c4"
                  strokeWidth="2"
                  strokeDasharray="1,6"
                  strokeLinecap="round"
                />
                <circle cx={l.x1} cy={l.y1} r="2" fill="#c4c4c4" />
              </g>
            ))}
          </svg>

          <div className="skillCompare">
            <div className="skillCompare__column">
              <h2 ref={gapsTitleRef} className="skillCompare__columnTitle">
                Habilidades faltantes ·{" "}
                <span className="skillCompare__columnCount">{gaps.length}</span>
              </h2>
              <span className="results__divider"></span>
              {gaps.map((skill, i) => (
                <div
                  key={`gap-${i}`}
                  className="skillCompare__item skillCompare__item_gaps"
                >
                  {skill}
                </div>
              ))}
            </div>

            <div className="skillCompare__circleWrap">
              <Box
                ref={circleRef}
                sx={{ position: "relative", display: "inline-flex" }}
              >
                <svg width={0} height={0}>
                  <defs>
                    <linearGradient
                      id="scoreGradient"
                      gradientUnits="userSpaceOnUse"
                      x1={gradientStart.x}
                      y1={gradientStart.y}
                      x2={gradientEnd.x}
                      y2={gradientEnd.y}
                    >
                      <stop
                        offset="0%"
                        stopColor={compatibility.gradientFrom}
                      />
                      <stop
                        offset="100%"
                        stopColor={compatibility.gradientTo}
                      />
                    </linearGradient>
                  </defs>
                </svg>
                <CircularProgress
                  variant="determinate"
                  value={100}
                  size={CIRCLE_SIZE}
                  thickness={CIRCLE_THICKNESS}
                  sx={{ color: "#e0e0e0", position: "absolute", left: 0 }}
                />
                <CircularProgress
                  variant="determinate"
                  value={percent}
                  size={CIRCLE_SIZE}
                  thickness={CIRCLE_THICKNESS}
                  sx={{
                    color: compatibility.color,
                    "& .MuiCircularProgress-circle": {
                      stroke: "url(#scoreGradient)",
                      strokeLinecap: "round",
                    },
                  }}
                />
                <Box
                  sx={{
                    top: 0,
                    left: 0,
                    bottom: 0,
                    right: 0,
                    position: "absolute",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "4px",
                  }}
                >
                  <Typography
                    variant="h4"
                    sx={{ color: compatibility.color, fontWeight: "bold" }}
                  >
                    {`${percent}%`}
                  </Typography>

                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      color: compatibility.color,
                      backgroundColor: compatibility.background,
                      borderRadius: "999px",
                      padding: "3px 10px",
                      fontSize: "11px",
                      fontWeight: 600,
                    }}
                  >
                    <Box
                      component="span"
                      sx={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        backgroundColor: compatibility.color,
                        display: "inline-block",
                      }}
                    />
                    Compatibilidade {compatibility.label}
                  </Box>
                </Box>
              </Box>
            </div>

            <div className="skillCompare__column">
              <h2 className="skillCompare__columnTitle skillCompare__columnTitle_right">
                <span
                  className="skillCompare__columnCount"
                  ref={matchesTitleRef}
                >
                  {matches.length}
                </span>{" "}
                · Habilidades compatíveis
              </h2>
              <span className="results__divider results__divider_right"></span>
              {matches.map((skill, i) => (
                <div
                  key={`match-${i}`}
                  className="skillCompare__item skillCompare__item_matches"
                >
                  {skill}
                </div>
              ))}
            </div>
          </div>
        </div>

        <button className="results__viewMore" onClick={handleOpenModal}>
          Ver mais
        </button>

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
