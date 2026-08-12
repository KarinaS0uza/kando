import Popover from "@mui/material/Popover";
import Typography from "@mui/material/Typography";

// Hint tooltip anchored to Signup's full-name field, open by default and
// dismissed when the field gains focus (see JoinForm.jsx). Props:
// - anchorEl (HTMLElement | null): the input to anchor to
// - open (bool)
// - onClose (fn)
export default function PopoverSignup({ anchorEl, open, onClose }) {
  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: "top",
        horizontal: "right",
      }}
      transformOrigin={{
        vertical: "bottom",
        horizontal: "left",
      }}
      // Both the backdrop AND the Modal root it sits in span the whole
      // viewport and swallow the click that's supposed to reach the
      // anchored input's onFocus below them, trapping the user instead of
      // letting them dismiss the popover by clicking the field. Make the
      // whole overlay click-through except the popover's own content box;
      // closing is handled by the input's onFocus instead.
      sx={{ pointerEvents: "none" }}
      slotProps={{
        backdrop: {
          invisible: true,
          sx: { pointerEvents: "none" },
        },
        paper: {
          sx: { pointerEvents: "auto", width: "300px" },
        },
      }}
    >
      <Typography sx={{ p: 2, fontSize: "12px" }}>
        Digite seu nome completo, como vai aparecer no seu certificado.
      </Typography>
    </Popover>
  );
}
