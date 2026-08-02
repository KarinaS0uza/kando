import { carregarSvgColorido } from "./loadSvg";

export function carregarImagem(caminho) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () =>
      reject(new Error(`Falha ao carregar imagem: ${caminho}`));
    img.src = caminho;
  });
}

export async function prepararElementos(elementos) {
  return Promise.all(
    elementos.map(async (el) => {
      let elementoPronto = el;

      if (el.tipo === "imagem" || el.url) {
        const urlLower = el.url?.toLowerCase() ?? "";
        const ehSvg =
          urlLower.endsWith(".svg") ||
          urlLower.startsWith("data:image/svg+xml");

        const imagemCarregada =
          ehSvg && el.cor
            ? await carregarSvgColorido(el.url, el.cor)
            : await carregarImagem(el.url);

        elementoPronto = { ...el, imagemCarregada };
      }

      if (el.elementos && el.elementos.length) {
        const filhosProntos = await prepararElementos(el.elementos);
        elementoPronto = { ...elementoPronto, elementos: filhosProntos };
      }
      return elementoPronto;
    }),
  );
}
