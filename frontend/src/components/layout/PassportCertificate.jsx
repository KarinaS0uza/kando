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
import react from "devicon/icons/react/react-original.svg";
import css from "devicon/icons/css3/css3-plain.svg";
import tailwind from "devicon/icons/tailwindcss/tailwindcss-original.svg";
import github from "devicon/icons/github/github-original.svg";
import html from "devicon/icons/html5/html5-plain.svg";
import git from "devicon/icons/git/git-plain.svg";
import angular from "devicon/icons/angularjs/angularjs-plain.svg";
import javascript from "devicon/icons/javascript/javascript-plain.svg";
import next from "devicon/icons/nextjs/nextjs-plain.svg";
import node from "devicon/icons/nodejs/nodejs-plain.svg";
import vue from "devicon/icons/vuejs/vuejs-plain.svg";

// linguagens
import python from "devicon/icons/python/python-plain.svg";
import java from "devicon/icons/java/java-plain.svg";
import csharp from "devicon/icons/csharp/csharp-plain.svg";
import cplusplus from "devicon/icons/cplusplus/cplusplus-plain.svg";
import c from "devicon/icons/c/c-original.svg";
import php from "devicon/icons/php/php-plain.svg";
import ruby from "devicon/icons/ruby/ruby-plain.svg";
import go from "devicon/icons/go/go-plain.svg";
import typescript from "devicon/icons/typescript/typescript-plain.svg";
import kotlin from "devicon/icons/kotlin/kotlin-plain.svg";
import swift from "devicon/icons/swift/swift-plain.svg";
import rust from "devicon/icons/rust/rust-original.svg";

// frameworks/libs adicionais
import sass from "devicon/icons/sass/sass-original.svg";
import bootstrap from "devicon/icons/bootstrap/bootstrap-plain.svg";
import materialui from "devicon/icons/materialui/materialui-plain.svg";
import redux from "devicon/icons/redux/redux-original.svg";
import django from "devicon/icons/django/django-plain.svg";
import flask from "devicon/icons/flask/flask-original.svg";
import spring from "devicon/icons/spring/spring-original.svg";
import laravel from "devicon/icons/laravel/laravel-original.svg";
import dotnetcore from "devicon/icons/dotnetcore/dotnetcore-plain.svg";

// bancos de dados
import postgresql from "devicon/icons/postgresql/postgresql-plain.svg";
import mysql from "devicon/icons/mysql/mysql-original.svg";
import mongodb from "devicon/icons/mongodb/mongodb-plain.svg";
import redis from "devicon/icons/redis/redis-plain.svg";
import sqlite from "devicon/icons/sqlite/sqlite-plain.svg";

// cloud/devops
import docker from "devicon/icons/docker/docker-plain.svg";
import kubernetes from "devicon/icons/kubernetes/kubernetes-plain.svg";
import amazonwebservices from "devicon/icons/amazonwebservices/amazonwebservices-original-wordmark.svg";
import azure from "devicon/icons/azure/azure-plain.svg";
import googlecloud from "devicon/icons/googlecloud/googlecloud-plain.svg";
import nginx from "devicon/icons/nginx/nginx-original.svg";
import linux from "devicon/icons/linux/linux-plain.svg";
import bash from "devicon/icons/bash/bash-plain.svg";
import jenkins from "devicon/icons/jenkins/jenkins-plain.svg";
import gitlab from "devicon/icons/gitlab/gitlab-plain.svg";

// ferramentas
import figma from "devicon/icons/figma/figma-plain.svg";
import jira from "devicon/icons/jira/jira-plain.svg";
import npmIcon from "devicon/icons/npm/npm-plain.svg";
import webpack from "devicon/icons/webpack/webpack-plain.svg";
import vitejs from "devicon/icons/vitejs/vitejs-plain.svg";
import jest from "devicon/icons/jest/jest-plain.svg";

// dados/data science (SQL, Seaborn, PySpark, Power BI, Tableau, Looker,
// Excel, BigQuery, Snowflake, Redshift e dbt não têm ícone no pacote
// devicon — ficam no fallback genérico)
import r from "devicon/icons/r/r-plain.svg";
import pandas from "devicon/icons/pandas/pandas-plain.svg";
import numpy from "devicon/icons/numpy/numpy-plain.svg";
import matplotlib from "devicon/icons/matplotlib/matplotlib-plain.svg";
import scikitlearn from "devicon/icons/scikitlearn/scikitlearn-plain.svg";
import apachespark from "devicon/icons/apachespark/apachespark-original.svg";
import hadoop from "devicon/icons/hadoop/hadoop-plain.svg";
import apacheairflow from "devicon/icons/apacheairflow/apacheairflow-plain.svg";
import apachekafka from "devicon/icons/apachekafka/apachekafka-original.svg";
import jupyter from "devicon/icons/jupyter/jupyter-plain.svg";
import googlecolab from "devicon/icons/googlecolab/googlecolab-plain.svg";
import anaconda from "devicon/icons/anaconda/anaconda-original.svg";

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
  "git/github": github,
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

  // linguagens
  python: python,
  py: python,
  r: r,
  java: java,
  csharp: csharp,
  "c#": csharp,
  "c++": cplusplus,
  cplusplus: cplusplus,
  cpp: cplusplus,
  c: c,
  php: php,
  ruby: ruby,
  go: go,
  golang: go,
  typescript: typescript,
  ts: typescript,
  kotlin: kotlin,
  swift: swift,
  rust: rust,

  // frameworks/libs adicionais
  sass: sass,
  scss: sass,
  bootstrap: bootstrap,
  "material ui": materialui,
  materialui: materialui,
  mui: materialui,
  redux: redux,
  django: django,
  flask: flask,
  spring: spring,
  "spring boot": spring,
  springboot: spring,
  laravel: laravel,
  dotnet: dotnetcore,
  ".net": dotnetcore,
  dotnetcore: dotnetcore,

  // bancos de dados
  postgresql: postgresql,
  postgres: postgresql,
  mysql: mysql,
  mongodb: mongodb,
  mongo: mongodb,
  redis: redis,
  sqlite: sqlite,

  // cloud/devops
  docker: docker,
  kubernetes: kubernetes,
  k8s: kubernetes,
  aws: amazonwebservices,
  "amazon web services": amazonwebservices,
  amazonwebservices: amazonwebservices,
  azure: azure,
  "google cloud": googlecloud,
  gcp: googlecloud,
  googlecloud: googlecloud,
  nginx: nginx,
  linux: linux,
  bash: bash,
  shell: bash,
  jenkins: jenkins,
  gitlab: gitlab,

  // ferramentas
  figma: figma,
  jira: jira,
  npm: npmIcon,
  webpack: webpack,
  vite: vitejs,
  vitejs: vitejs,
  jest: jest,

  // dados/data science
  pandas: pandas,
  numpy: numpy,
  matplotlib: matplotlib,
  "scikit-learn": scikitlearn,
  scikitlearn: scikitlearn,
  sklearn: scikitlearn,
  "apache spark": apachespark,
  apachespark: apachespark,
  spark: apachespark,
  hadoop: hadoop,
  airflow: apacheairflow,
  "apache airflow": apacheairflow,
  apacheairflow: apacheairflow,
  kafka: apachekafka,
  "apache kafka": apachekafka,
  apachekafka: apachekafka,
  jupyter: jupyter,
  "jupyter notebook": jupyter,
  "google colab": googlecolab,
  colab: googlecolab,
  googlecolab: googlecolab,
  anaconda: anaconda,
  conda: anaconda,
};

function resolverIcone(skill) {
  return ICONS_BY_SKILL[(skill || "").trim().toLowerCase()] || ICONE_GENERICO;
}

// quando `validado` for false, o carimbo usa o cinza padrão e ganha um cadeado no canto superior direito
function aplicarValidacao(validado, corOriginal, nivelOriginal) {
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
    nivel: validado ? nivelOriginal : "blocked",
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
  const { cor, filtro, elementosExtras, nivel } = aplicarValidacao(
    competencia.validado,
    layout.corOriginal,
    competencia.nivel,
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
        texto: `★ ${PROFICIENCY_LABELS[nivel]} ★`,
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
          className="passport-certificate__main-image"
          src={resultado.dataUrl}
          alt="Imagem gerada"
        />
      )}
    </div>
  );
}
