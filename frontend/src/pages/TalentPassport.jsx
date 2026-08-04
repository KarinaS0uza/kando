import { useState } from "react";
import jsPDF from "jspdf";
import PassportCertificate from "../components/layout/PassportCertificate";
import Header from "../components/layout/Header";
import LinkedInIcon from "@mui/icons-material/LinkedIn";
import DownloadIcon from "@mui/icons-material/Download";
import ImageIcon from "@mui/icons-material/Image";

import "./TalentPassport.css";

function shareOnLinkedin() {
  const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`;
  window.open(url, "_blank", "noopener,noreferrer,width=600,height=600");
}

async function baixarPdf(imagemDataUrl) {
  if (!imagemDataUrl) return;

  const imagem = new Image();
  imagem.src = imagemDataUrl;
  await new Promise((resolve) => {
    imagem.onload = resolve;
  });

  const doc = new jsPDF({
    orientation: imagem.width >= imagem.height ? "landscape" : "portrait",
    unit: "px",
    format: [imagem.width, imagem.height],
  });
  doc.addImage(imagemDataUrl, "PNG", 0, 0, imagem.width, imagem.height);
  doc.save("talent-passport.pdf");
}

function baixarPng(imagemDataUrl) {
  if (!imagemDataUrl) return;

  const link = document.createElement("a");
  link.href = imagemDataUrl;
  link.download = "talent-passport.png";
  link.click();
}

export default function TalentPassport() {
  const [imagemDataUrl, setImagemDataUrl] = useState(null);

  return (
    <>
      <Header menuActive={true} />
      <div className="passport">
        <h1 className="passport__title">Seu certificado Talent Passport</h1>
        <p className="passport__subtitle">
          Parabéns pela conquista! Seu certificado oficial está pronto para ser
          compartilhado.
        </p>

        <div className="passport__certificate">
          <PassportCertificate onImagemGerada={setImagemDataUrl} />
        </div>

        <div className="passport__actions">
          <button
            className="passport__action passport__action--linkedin"
            onClick={shareOnLinkedin}
          >
            <LinkedInIcon fontSize="small" />
            Compartilhar no LinkedIn
          </button>

          <button
            className="passport__action"
            onClick={() => baixarPdf(imagemDataUrl)}
            disabled={!imagemDataUrl}
          >
            <DownloadIcon fontSize="small" />
            Baixar PDF
          </button>

          <button
            className="passport__action"
            onClick={() => baixarPng(imagemDataUrl)}
            disabled={!imagemDataUrl}
          >
            <ImageIcon fontSize="small" />
            Baixar PNG
          </button>
        </div>
      </div>
    </>
  );
}
