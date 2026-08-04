export async function carregarSvgColorido(url, cor) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Falha ao buscar SVG: ${url}`);
  }

  let svgTexto = await response.text();

  if (cor) {
    // preserva fill/stroke="none" (ex.: contornos de wave.svg) e só substitui cores de verdade
    svgTexto = svgTexto
      .replace(/fill=(["'])(?!\s*none\1)[^"']*\1/gi, `fill="${cor}"`)
      .replace(/stroke=(["'])(?!\s*none\1)[^"']*\1/gi, `stroke="${cor}"`);

    if (!/<svg[^>]*\sfill=/i.test(svgTexto)) {
      svgTexto = svgTexto.replace("<svg", `<svg fill="${cor}"`);
    }
    if (!/<svg[^>]*\sstroke=/i.test(svgTexto)) {
      svgTexto = svgTexto.replace("<svg", `<svg stroke="${cor}"`);
    }
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
