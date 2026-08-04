export function desenharTexto(
  ctx,
  textoConfig,
  baseX,
  baseY,
  larguraRef,
  alturaRef,
) {
  const x = baseX + textoConfig.xPercent * larguraRef;
  const y = baseY + textoConfig.yPercent * alturaRef;

  ctx.font = `${textoConfig.tamanho || 20}px ${textoConfig.fonte || "Arial, sans-serif"}`;
  ctx.fillStyle = textoConfig.cor || "#000";
  ctx.textAlign = textoConfig.alinhamento || "left";
  ctx.textBaseline = textoConfig.baseline || "middle";
  ctx.fillText(textoConfig.texto, x, y);
}

// desenha vários trechos lado a lado como se fossem uma única string, cada um com sua
// própria fonte/tamanho/cor (ex: título + role numa mesma linha com estilos diferentes)
export function desenharTextoComposto(
  ctx,
  compostoConfig,
  baseX,
  baseY,
  larguraRef,
  alturaRef,
) {
  const {
    segmentos,
    xPercent,
    yPercent,
    alinhamento = "left",
    baseline = "middle",
  } = compostoConfig;

  const x = baseX + xPercent * larguraRef;
  const y = baseY + yPercent * alturaRef;

  const larguras = segmentos.map((segmento) => {
    ctx.font = `${segmento.tamanho || 20}px ${segmento.fonte || "Arial, sans-serif"}`;
    return ctx.measureText(segmento.texto).width;
  });
  const larguraTotal = larguras.reduce((soma, largura) => soma + largura, 0);

  let cursorX = x;
  if (alinhamento === "center") {
    cursorX = x - larguraTotal / 2;
  } else if (alinhamento === "right") {
    cursorX = x - larguraTotal;
  }

  ctx.textAlign = "left";
  ctx.textBaseline = baseline;

  segmentos.forEach((segmento, i) => {
    ctx.font = `${segmento.tamanho || 20}px ${segmento.fonte || "Arial, sans-serif"}`;
    ctx.fillStyle = segmento.cor || "#000";
    ctx.fillText(segmento.texto, cursorX, y);
    cursorX += larguras[i];
  });
}
