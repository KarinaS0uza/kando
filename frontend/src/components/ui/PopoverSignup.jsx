import Popover from "@mui/material/Popover";
import Typography from "@mui/material/Typography";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useEffect } from "react";

// Hint tooltip anchored to Signup's full-name field, open by default and
// dismissed when the field gains focus (see JoinForm.jsx). Props:
// - anchorEl (HTMLElement | null): the input to anchor to
// - open (bool)
// - onClose (fn)
export default function PopoverSignup({ anchorEl, open, onClose }) {
  const isMobile = useMediaQuery("(max-width:600px)");

  useEffect(() => {
    if (!open) return undefined;

    const closeOnPageClick = () => onClose();
    document.addEventListener("pointerdown", closeOnPageClick, true);

    return () => {
      document.removeEventListener("pointerdown", closeOnPageClick, true);
    };
  }, [open, onClose]);

  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: isMobile ? "bottom" : "top",
        horizontal: isMobile ? "center" : "right",
      }}
      transformOrigin={{
        vertical: isMobile ? "top" : "bottom",
        horizontal: isMobile ? "center" : "left",
      }}
      // Both the backdrop AND the Modal root it sits in span the whole
      // viewport and swallow the click that's supposed to reach the
      // anchored input's onFocus below them, trapping the user instead of
      // letting them dismiss the popover by clicking the field. Make the
      // whole overlay click-through except the popover's own content box.
      // A document-level pointer listener closes it without blocking the
      // element the user intended to click.
      sx={{ pointerEvents: "none" }}
      slotProps={{
        backdrop: {
          invisible: true,
          sx: { pointerEvents: "none" },
        },
        paper: {
          sx: {
            pointerEvents: "auto",
            width: isMobile ? "calc(100vw - 48px)" : "300px",
            maxWidth: "300px",
            mt: isMobile ? 1 : 0,
          },
        },
      }}
    >
      <Typography sx={{ p: 2, fontSize: "12px" }}>
        Digite seu nome completo, como vai aparecer no seu certificado.
      </Typography>
    </Popover>
  );
}
