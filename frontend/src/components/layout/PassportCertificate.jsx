import { useImageComposer } from "../../hooks/useImageComposer";
import {
  buscarDadosPassaporte,
  PROFICIENCY_LABELS,
} from "../../services/passportService";
import { useEffect, useState } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import VerifiedIcon from "@mui/icons-material/Verified";
import LoadingSpinner from "../ui/LoadingSpinner";

//imagens fixas
import passportTemplate from "../../assets/passportTalent-template.png";
import stamp_1 from "../../assets/stamp_1.png";
import stamp_2 from "../../assets/stamp_2.png";
import stamp_3 from "../../assets/stamp_3.png";
import stamp_4 from "../../assets/stamp_4.png";
import stamp_5 from "../../assets/stamp_5.png";
import stamp_6 from "../../assets/stamp_6.png";
import wave from "../../assets/wave.svg";
import lock from "../../assets/lock.svg";
import globe from "../../assets/globe.svg";

//tech icons
import react from "../../assets/tech_icons/react.svg";
import css from "../../assets/tech_icons/css3.svg";
import tailwind from "../../assets/tech_icons/tailwind.svg";
import github from "../../assets/tech_icons/github.svg";
import html from "../../assets/tech_icons/html.svg";
import git from "../../assets/tech_icons/git.svg";
import angular from "../../assets/tech_icons/angular.svg";
import javascript from "../../assets/tech_icons/javascript.svg";
import next from "../../assets/tech_icons/next.svg";
import node from "../../assets/tech_icons/node.svg";
import vue from "../../assets/tech_icons/vue.svg";

import "./PassportCertificate.css";

const CINZA_NAO_VALIDADO = "rgb(64%, 60%, 56%)";

// SVG string for the fallback icon, built once so it can be loaded as a
// canvas image (the pipeline draws image URLs, not React components) and
// recolored per carimbo the same way the tech icons are.
//
// renderToStaticMarkup on a styled MUI icon emits a leading <style
// data-emotion=...> sibling plus a bare <svg> with no XML namespace -- fine
// inline in an HTML document, but a standalone SVG image needs a single
// <svg> root with an explicit xmlns, or the browser's strict SVG parser
// rejects it and the <img> fails to load.
function paraImagemSvg(svgString) {
  const [svgApenas] = svgString.match(/<svg[\s\S]*<\/svg>/) || [svgString];
  const comNamespace = /<svg[^>]*\sxmlns=/.test(svgApenas)
    ? svgApenas
    : svgApenas.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"');
  return `data:image/svg+xml,${encodeURIComponent(comNamespace)}`;
}

const ICONE_GENERICO = paraImagemSvg(renderToStaticMarkup(<VerifiedIcon />));

// Resolve a skill name (as returned by the LLM, e.g. "React.js") to one of
// the available tech icons; unrecognized skills fall back to ICONE_GENERICO.
const ICONS_BY_SKILL = {
  react: react,
  "react.js": react,
  reactjs: react,
  css: css,
  css3: css,
  tailwind: tailwind,
  tailwindcss: tailwind,
  github: github,
  html: html,
  html5: html,
  git: git,
  angular: angular,
  javascript: javascript,
  js: javascript,
  node: node,
  "node.js": node,
  nodejs: node,
  next: next,
  "next.js": next,
  nextjs: next,
  vue: vue,
  "vue.js": vue,
};

function resolverIcone(skill) {
  return ICONS_BY_SKILL[(skill || "").trim().toLowerCase()] || ICONE_GENERICO;
}

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

// Fixed per-slot artwork/layout (stamp graphic, grid position, decorative
// glyphs tuned to that specific PNG, original accent color). The dynamic
// content (skill, proficiency level, icon, validated state) is filled in
// from the candidate's real competencies in montarCarimbo below.
function construirLayoutsDeCarimbo() {
  const row1 = 0.62;
  const row2 = 0.8205;
  const col1 = 0.263;
  const col2 = 0.5;
  const col3 = 0.7422;

  return [
    {
      url: stamp_1,
      xPercent: col1,
      yPercent: row1,
      corOriginal: "rgb(29%, 47%, 32%)",
      textoYPercent: 0.27,
      nivelYPercent: 0.74,
      iconeXPercent: 0.5,
      iconeYPercent: 0.5,
      decoracoes: [
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
          url: wave,
          xPercent: 0.15,
          yPercent: 0.5,
          largura: 80,
        },
      ],
    },
    {
      url: stamp_2,
      xPercent: col2,
      yPercent: row1,
      corOriginal: "rgb(49%, 43%, 60%)",
      textoYPercent: 0.28,
      nivelYPercent: 0.74,
      iconeXPercent: 0.5,
      iconeYPercent: 0.5,
      decoracoes: [
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
      ],
    },
    {
      url: stamp_5,
      xPercent: col3,
      yPercent: row1,
      corOriginal: "rgb(62%, 46%, 26%)",
      textoYPercent: 0.24,
      nivelYPercent: 0.78,
      iconeXPercent: 0.51,
      iconeYPercent: 0.5,
      decoracoes: [
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
      ],
    },
    {
      url: stamp_3,
      xPercent: col1,
      yPercent: row2,
      corOriginal: "rgb(22%, 49%, 54%)",
      textoYPercent: 0.28,
      nivelYPercent: 0.74,
      iconeXPercent: 0.5,
      iconeYPercent: 0.5,
      decoracoes: [
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
      ],
    },
    {
      url: stamp_4,
      xPercent: col2,
      yPercent: row2,
      corOriginal: "rgb(26%, 40%, 58%)",
      textoYPercent: 0.26,
      nivelYPercent: 0.78,
      iconeXPercent: 0.5,
      iconeYPercent: 0.5,
      decoracoes: [
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
      ],
    },
    {
      url: stamp_6,
      xPercent: col3,
      yPercent: row2,
      corOriginal: "rgb(58%, 33%, 19%)",
      textoYPercent: 0.28,
      nivelYPercent: 0.74,
      iconeXPercent: 0.5,
      iconeYPercent: 0.5,
      decoracoes: [
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
      ],
    },
  ];
}

function montarCarimbo(layout, competencia) {
  const { cor, filtro, elementosExtras } = aplicarValidacao(
    competencia.validado,
    layout.corOriginal,
  );

  return {
    url: layout.url,
    xPercent: layout.xPercent,
    yPercent: layout.yPercent,
    largura: 300,
    cor,
    filtro,
    elementos: [
      {
        tipo: "texto",
        texto: (competencia.skill || "").toUpperCase(),
        xPercent: 0.5,
        yPercent: layout.textoYPercent,
        tamanho: 28,
        alinhamento: "center",
        fonte: '"Augustus"',
        // a borda do carimbo é bem mais estreita perto do topo/base do que no
        // meio; mantém uma margem segura pra não encostar nela
        larguraMaximaPercent: 0.6,
      },
      {
        tipo: "texto",
        texto: `★ ${PROFICIENCY_LABELS[competencia.nivel] || (competencia.nivel || "").toUpperCase()} ★`,
        xPercent: 0.5,
        yPercent: layout.nivelYPercent,
        tamanho: 18,
        alinhamento: "center",
        fonte: '"Romanica"',
        larguraMaximaPercent: 0.68,
      },
      {
        tipo: "imagem",
        url: resolverIcone(competencia.skill),
        xPercent: layout.iconeXPercent,
        yPercent: layout.iconeYPercent,
        largura: 60,
        falhaTinta: true,
      },
      ...layout.decoracoes,
      ...elementosExtras,
    ],
  };
}

export default function PassportCertificate({ onImagemGerada }) {
  const { gerar, loading, resultado, erro } = useImageComposer();
  const [dadosUsuario, setDadosUsuario] = useState(null);
  const [erroDados, setErroDados] = useState(null);

  useEffect(() => {
    buscarDadosPassaporte()
      .then(setDadosUsuario)
      .catch((error) => setErroDados(error.message));
  }, []);

  useEffect(() => {
    if (!dadosUsuario) return;

    const layouts = construirLayoutsDeCarimbo();
    const carimbos = (dadosUsuario.carimbos || [])
      .slice(0, layouts.length)
      .map((competencia, index) => montarCarimbo(layouts[index], competencia));

    const config = {
      imagemBase: passportTemplate,

      roleTitulo: {
        xPercent: 0.5082,
        yPercent: 0.3354,
        alinhamento: "center",
        // largura interna do retângulo do certificado no template, com uma
        // margem para o texto não encostar nas bordas
        larguraMaximaPercent: 0.56,
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

      carimbos,
    };

    gerar(config);
  }, [dadosUsuario]);

  useEffect(() => {
    if (resultado) {
      onImagemGerada?.(resultado.dataUrl);
    }
  }, [resultado]);

  return (
    <div className="passport-certificate">
      {loading && !erroDados && (
        <div className="passport-certificate__overlay">
          <LoadingSpinner />
        </div>
      )}
      {erroDados && <p>{erroDados}</p>}
      {!erroDados && erro && <p>Erro ao gerar a imagem.</p>}
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
