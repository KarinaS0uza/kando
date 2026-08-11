import * as React from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import logo from "../../assets/logo-indigo.svg";

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
                "0%": { transform: "scale(0.2)" },
                "60%": { transform: "scale(1.25)" },
                "100%": { transform: "scale(1)" },
              },
              animation: "popIn 1500ms ease-out",
            }}
          />
        </Box>
      </Box>
      <Box sx={{ mt: 2 }}>Carregando…</Box>
    </Box>
  );
}
