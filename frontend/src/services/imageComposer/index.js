import { carregarImagem, prepararElementos } from "./loadImage";
import { carregarFonte } from "./loadFont";
import { desenharTexto, desenharTextoComposto } from "./drawText";
import { desenharElemento } from "./drawElement";
import { resolverCorElementos } from "./resolveCor";

// fontes disponíveis em /fonts para uso em qualquer elemento via "fonte": '"NomeDaFonte"'
const FONTES_DISPONIVEIS = [
  { nome: "Assinatura", url: "/fonts/Rottasicity-Italic.woff2", fallback: "cursive" },
  { nome: "Warren", url: "/fonts/WARREN.ttf", fallback: "serif" },
  { nome: "Romanica", url: "/fonts/Romanica.ttf", fallback: "serif" },
  { nome: "Augustus", url: "/fonts/AUGUSTUS.TTF", fallback: "serif" },
  { nome: "ModernRomance", url: "/fonts/Modern%20Romance.otf", fallback: "cursive" },
];

export async function gerarImagemFinal(config) {
  await Promise.all(
    FONTES_DISPONIVEIS.map(({ nome, url, fallback }) =>
      carregarFonte(nome, url, fallback),
    ),
  );

  const imgBase = await carregarImagem(config.imagemBase);

  const canvas = document.createElement("canvas");
  canvas.width = imgBase.width;
  canvas.height = imgBase.height;
  const ctx = canvas.getContext("2d");

  ctx.drawImage(imgBase, 0, 0);

  // 1. imagens dinâmicas soltas (ex: foto de perfil)
  const imagensProntas = await prepararElementos(config.imagensDinamicas || []);
  imagensProntas.forEach((el) =>
    desenharElemento(ctx, { ...el, tipo: "imagem" }, canvas),
  );

  // 2. carimbos — resolve cor herdada ANTES de pré-carregar (o SVG precisa da cor no carregamento)
  const carimbosComCor = (config.carimbos || []).map((c) =>
    resolverCorElementos(c),
  );
  const carimbosProntos = await prepararElementos(carimbosComCor);
  carimbosProntos.forEach((el) =>
    desenharElemento(ctx, { ...el, tipo: "imagem" }, canvas),
  );

  // 3. nome
  if (config.nome) {
    desenharTexto(ctx, config.nome, 0, 0, canvas.width, canvas.height);
  }

  // 4. role + título (uma única linha, cada trecho com sua própria fonte/tamanho)
  if (config.roleTitulo) {
    desenharTextoComposto(
      ctx,
      config.roleTitulo,
      0,
      0,
      canvas.width,
      canvas.height,
    );
  }

  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve({ blob, dataUrl: canvas.toDataURL("image/png"), canvas });
    }, "image/png");
  });
}
