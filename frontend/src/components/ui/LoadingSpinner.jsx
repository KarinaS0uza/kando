import * as React from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import logo from "../../assets/logo-indigo.svg";

// Generic loading indicator: MUI CircularProgress ring with the TP logo
// centered inside, popping in with a scale animation on mount. No props.
// Styled entirely via MUI's `sx` prop (no className/CSS file), unlike most
// of the app - kept 100% MUI here since it's a small, self-contained
// visual with no page-specific layout concerns.
export default function LoadingSpinner() {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Box sx={{ position: "relative", display: "inline-flex" }}>
        <CircularProgress size={72} />
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        >
          <Box
            component="img"
            src={logo}
            alt=""
            sx={{
              display: "block",
              width: 32,
              height: 32,
              "@keyframes popIn": {
                "0%": { transform: "scale(0.5)" },
                "60%": { transform: "scale(1.25)" },
                "100%": { transform: "scale(0.5)" },
              },
              animation: "popIn 2500ms ease-out infinite",
            }}
          />
        </Box>
      </Box>
      <Box sx={{ mt: 2 }}>Carregando…</Box>
    </Box>
  );
}
