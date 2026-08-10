// retorna o fator de redução (<=1) necessário para uma largura natural caber
// dentro de larguraMaximaPx; 1 (sem mudança) se já couber ou não houver limite
function calcularEscalaParaCaber(larguraNatural, larguraMaximaPx) {
  if (!larguraMaximaPx || larguraNatural <= larguraMaximaPx) {
    return 1;
  }
  return larguraMaximaPx / larguraNatural;
}

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
  const fonte = textoConfig.fonte || "Arial, sans-serif";
  const tamanhoBase = textoConfig.tamanho || 20;

  // se o texto ultrapassar a largura disponível (ex: a borda de um carimbo),
  // reduz o tamanho da fonte até caber
  ctx.font = `${tamanhoBase}px ${fonte}`;
  const larguraNatural = ctx.measureText(textoConfig.texto).width;
  const escala = textoConfig.larguraMaximaPercent
    ? calcularEscalaParaCaber(
        larguraNatural,
        textoConfig.larguraMaximaPercent * larguraRef,
      )
    : 1;

  ctx.font = `${tamanhoBase * escala}px ${fonte}`;
  ctx.fillStyle = textoConfig.cor || "#000";
  ctx.textAlign = textoConfig.alinhamento || "left";
  ctx.textBaseline = textoConfig.baseline || "middle";
  ctx.fillText(textoConfig.texto, x, y);
}

// desenha vários trechos lado a lado como se fossem uma única string, cada um com sua
// própria fonte/tamanho/cor (ex: título + role numa mesma linha com estilos diferentes)
// mede a largura total dos segmentos com seus tamanhos originais multiplicados por `escala`
function medirLarguraComposta(ctx, segmentos, escala) {
  return segmentos.reduce((total, segmento) => {
    ctx.font = `${(segmento.tamanho || 20) * escala}px ${segmento.fonte || "Arial, sans-serif"}`;
    return total + ctx.measureText(segmento.texto).width;
  }, 0);
}

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
    larguraMaximaPercent,
  } = compostoConfig;

  const x = baseX + xPercent * larguraRef;
  const y = baseY + yPercent * alturaRef;

  // se a linha ultrapassar a largura disponível (ex: o retângulo do certificado),
  // reduz todos os tamanhos proporcionalmente até caber
  const escala = larguraMaximaPercent
    ? calcularEscalaParaCaber(
        medirLarguraComposta(ctx, segmentos, 1),
        larguraMaximaPercent * larguraRef,
      )
    : 1;

  const larguras = segmentos.map((segmento) => {
    ctx.font = `${(segmento.tamanho || 20) * escala}px ${segmento.fonte || "Arial, sans-serif"}`;
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
    ctx.font = `${(segmento.tamanho || 20) * escala}px ${segmento.fonte || "Arial, sans-serif"}`;
    ctx.fillStyle = segmento.cor || "#000";
    ctx.fillText(segmento.texto, cursorX, y);
    cursorX += larguras[i];
  });
}
