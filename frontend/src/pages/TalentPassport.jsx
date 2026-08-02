import { useImageComposer } from "../hooks/useImageComposer";
import { buscarDadosPassaporte } from "../services/passportService";
import { useEffect, useState } from "react";

//imagens fixas
import passportTemplate from "../assets/passportTalent-template.png";
import stamp_1 from "../assets/stamp_1.png";
import stamp_2 from "../assets/stamp_2.png";
import stamp_3 from "../assets/stamp_3.png";
import stamp_4 from "../assets/stamp_4.png";
import stamp_5 from "../assets/stamp_5.png";
import stamp_6 from "../assets/stamp_6.png";
import wave from "../assets/wave.svg";
import lock from "../assets/lock.svg";
import globe from "../assets/globe.svg";

//tech icons
import react from "../assets/tech_icons/react.svg";
import css from "../assets/tech_icons/css3.svg";
import tailwind from "../assets/tech_icons/tailwind.svg";
import github from "../assets/tech_icons/github.svg";
import html from "../assets/tech_icons/html.svg";
import git from "../assets/tech_icons/git.svg";

import "./TalentPassport.css";

const CINZA_NAO_VALIDADO = "rgb(64%, 60%, 56%)";

// quando `validado` for false, o carimbo usa o cinza padrão e ganha um cadeado no canto superior direito
function aplicarValidacao(validado, corOriginal) {
  return {
    cor: validado ? corOriginal : CINZA_NAO_VALIDADO,
    filtro: validado ? "none" : "grayscale(1) brightness(1.5)",
    elementosExtras: validado
      ? []
      : [
          {
            tipo: "imagem",
            url: lock,
            xPercent: 0.85,
            yPercent: 0.15,
            largura: 40,
          },
        ],
  };
}

export default function TalentPassport() {
  const { gerar, loading, resultado, erro } = useImageComposer();
  const [dadosUsuario, setDadosUsuario] = useState(null);

  useEffect(() => {
    buscarDadosPassaporte(123).then(setDadosUsuario);
  }, []);

  useEffect(() => {
    if (!dadosUsuario) return;

    const row1 = 0.62;
    const row2 = 0.8205;
    const col1 = 0.263;
    const col2 = 0.5;
    const col3 = 0.7422;

    // TODO: substituir por dados reais vindos de dadosUsuario quando o backend expuser essa informação
    const carimbo1 = aplicarValidacao(true, "rgb(29%, 47%, 32%)");
    const carimbo2 = aplicarValidacao(true, "rgb(49%, 43%, 60%)");
    const carimbo3 = aplicarValidacao(true, "rgb(62%, 46%, 26%)");
    const carimbo4 = aplicarValidacao(true, "rgb(22%, 49%, 54%)");
    const carimbo5 = aplicarValidacao(true, "rgb(26%, 40%, 58%)");
    const carimbo6 = aplicarValidacao(false, "rgb(58%, 33%, 19%)");

    const config = {
      imagemBase: passportTemplate,

      roleTitulo: {
        xPercent: 0.5082,
        yPercent: 0.3354,
        alinhamento: "center",
        segmentos: [
          {
            texto: `${dadosUsuario.role} — `,
            tamanho: 50,
            cor: "rgb(0%, 9%, 27%)",
            fonte: '"Romanica"',
          },
          {
            texto: dadosUsuario.title,
            tamanho: 35,
            cor: "rgb(0%, 9%, 27%)",
            fonte: "Romanica",
          },
        ],
      },

      nome: {
        texto: dadosUsuario.nome,
        xPercent: 0.5029,
        yPercent: 0.4428,
        tamanho: 70,
        cor: "rgb(0%, 9%, 27%)",
        alinhamento: "center",
        fonte: '"Assinatura"',
      },

      carimbos: [
        // carimbo 1
        {
          url: stamp_1,
          xPercent: col1,
          yPercent: row1,
          largura: 300,
          cor: carimbo1.cor,
          filtro: carimbo1.filtro,
          elementos: [
            {
              tipo: "texto",
              texto: "CSS3",
              xPercent: 0.5,
              yPercent: 0.24,
              tamanho: 28,
              alinhamento: "center",
              fonte: '"Augustus"',
            },
            {
              tipo: "texto",
              texto: "★ AVANÇADO ★",
              xPercent: 0.5,
              yPercent: 0.77,
              tamanho: 18,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "texto",
              texto: "✈",
              xPercent: 0.78,
              yPercent: 0.5,
              tamanho: 30,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: css,
              xPercent: 0.5,
              yPercent: 0.5,
              largura: 80,
              falhaTinta: true,
            },
            {
              tipo: "imagem",
              url: wave,
              xPercent: 0.15,
              yPercent: 0.5,
              largura: 80,
            },
            ...carimbo1.elementosExtras,
          ],
        },

        // carimbo 2
        {
          url: stamp_2,
          xPercent: col2,
          yPercent: row1,
          largura: 300,
          cor: carimbo2.cor,
          filtro: carimbo2.filtro,
          elementos: [
            {
              tipo: "texto",
              texto: "TAILWIND",
              xPercent: 0.5,
              yPercent: 0.28,
              tamanho: 28,
              alinhamento: "center",
              fonte: '"Augustus"',
            },
            {
              tipo: "texto",
              texto: "★ EXPERT ★",
              xPercent: 0.5,
              yPercent: 0.78,
              tamanho: 18,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: tailwind,
              xPercent: 0.5,
              yPercent: 0.5,
              largura: 80,
              falhaTinta: true,
            },
            {
              tipo: "imagem",
              url: wave,
              xPercent: 0.15,
              yPercent: 0.5,
              largura: 80,
            },
            {
              tipo: "imagem",
              url: globe,
              xPercent: 0.75,
              yPercent: 0.5,
              largura: 25,
            },
            ...carimbo2.elementosExtras,
          ],
        },

        // carimbo 3
        {
          url: stamp_5,
          xPercent: col3,
          yPercent: row1,
          largura: 300,
          cor: carimbo3.cor,
          filtro: carimbo3.filtro,
          elementos: [
            {
              tipo: "texto",
              texto: "GITHUB",
              xPercent: 0.5,
              yPercent: 0.24,
              tamanho: 28,
              alinhamento: "center",
              fonte: '"Augustus"',
            },
            {
              tipo: "texto",
              texto: "★ ESPECIALISTA ★",
              xPercent: 0.5,
              yPercent: 0.78,
              tamanho: 18,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: github,
              xPercent: 0.51,
              yPercent: 0.5,
              largura: 80,
              falhaTinta: true,
            },
            {
              tipo: "imagem",
              url: wave,
              xPercent: 0.9,
              yPercent: 0.5,
              largura: 80,
            },
            {
              tipo: "texto",
              texto: "✈",
              xPercent: 0.25,
              yPercent: 0.5,
              tamanho: 30,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            ...carimbo3.elementosExtras,
          ],
        },

        // carimbo 4
        {
          url: stamp_3,
          xPercent: col1,
          yPercent: row2,
          largura: 300,
          cor: carimbo4.cor,
          filtro: carimbo4.filtro,
          elementos: [
            {
              tipo: "texto",
              texto: "REACT",
              xPercent: 0.5,
              yPercent: 0.28,
              tamanho: 28,
              alinhamento: "center",
              fonte: '"Augustus"',
            },
            {
              tipo: "texto",
              texto: "★ ASCENSÃO ★",
              xPercent: 0.5,
              yPercent: 0.78,
              tamanho: 18,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: react,
              xPercent: 0.5,
              yPercent: 0.5,
              largura: 80,
              falhaTinta: true,
            },
            {
              tipo: "texto",
              texto: "✈",
              xPercent: 0.75,
              yPercent: 0.5,
              tamanho: 30,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: globe,
              xPercent: 0.245,
              yPercent: 0.5,
              largura: 25,
            },
            ...carimbo4.elementosExtras,
          ],
        },

        // carimbo 5
        {
          url: stamp_4,
          xPercent: col2,
          yPercent: row2,
          largura: 300,
          cor: carimbo5.cor,
          filtro: carimbo5.filtro,
          elementos: [
            {
              tipo: "texto",
              texto: "HTML",
              xPercent: 0.5,
              yPercent: 0.22,
              tamanho: 28,
              alinhamento: "center",
              fonte: '"Augustus"',
            },
            {
              tipo: "texto",
              texto: "★ EXPERT ★",
              xPercent: 0.5,
              yPercent: 0.78,
              tamanho: 18,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: html,
              xPercent: 0.5,
              yPercent: 0.5,
              largura: 80,
              falhaTinta: true,
            },
            {
              tipo: "imagem",
              url: globe,
              xPercent: 0.245,
              yPercent: 0.5,
              largura: 25,
            },
            {
              tipo: "imagem",
              url: wave,
              xPercent: 0.88,
              yPercent: 0.5,
              largura: 80,
            },
            ...carimbo5.elementosExtras,
          ],
        },

        // carimbo 6
        {
          url: stamp_6,
          xPercent: col3,
          yPercent: row2,
          largura: 300,
          cor: carimbo6.cor,
          filtro: carimbo6.filtro,
          elementos: [
            {
              tipo: "texto",
              texto: "GIT",
              xPercent: 0.5,
              yPercent: 0.28,
              tamanho: 28,
              alinhamento: "center",
              fonte: '"Augustus"',
            },
            {
              tipo: "texto",
              texto: "★ JUNINHO ★",
              xPercent: 0.5,
              yPercent: 0.78,
              tamanho: 18,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: git,
              xPercent: 0.5,
              yPercent: 0.5,
              largura: 80,
              falhaTinta: true,
            },
            {
              tipo: "texto",
              texto: "✈",
              xPercent: 0.75,
              yPercent: 0.5,
              tamanho: 30,
              alinhamento: "center",
              fonte: '"Romanica"',
            },
            {
              tipo: "imagem",
              url: globe,
              xPercent: 0.245,
              yPercent: 0.5,
              largura: 25,
            },
            ...carimbo6.elementosExtras,
          ],
        },
      ],
    };

    gerar(config);
  }, [dadosUsuario]);

  return (
    <div>
      {/* resto do conteúdo da página que já existe */}

      {loading && <p>Gerando imagem...</p>}
      {erro && <p>Erro ao gerar a imagem.</p>}
      {resultado && (
        <img
          className="talent__main_image"
          src={resultado.dataUrl}
          alt="Imagem gerada"
        />
      )}
    </div>
  );
}
