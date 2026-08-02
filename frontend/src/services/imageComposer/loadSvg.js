export async function carregarSvgColorido(url, cor) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Falha ao buscar SVG: ${url}`);
  }

  let svgTexto = await response.text();

  if (cor) {
    svgTexto = svgTexto
      .replace(/fill=["'][^"']*["']/g, "")
      .replace(/stroke=["'][^"']*["']/g, "");

    svgTexto = svgTexto.replace("<svg", `<svg fill="${cor}" stroke="${cor}"`);
  }

  const blob = new Blob([svgTexto], { type: "image/svg+xml" });
  const urlBlob = URL.createObjectURL(blob);

  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = urlBlob;
  });
}
