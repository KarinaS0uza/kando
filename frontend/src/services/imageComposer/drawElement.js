import { desenharTexto } from "./drawText";

// imita a tinta falhando ao carimbar: "come" pontinhos aleatórios da imagem já desenhada
function aplicarFalhaDeTinta(ctx, x, y, largura, altura, intensidade = 1) {
  ctx.save();
  ctx.globalCompositeOperation = "destination-out";

  const area = largura * altura;
  const quantidade = Math.max(20, Math.round((area / 400) * intensidade));
  const pontosPorAglomerado = 4;
  const raioAglomerado = Math.min(largura, altura) * 0.1;
  const quantidadeAglomerados = Math.max(
    1,
    Math.round(quantidade / pontosPorAglomerado),
  );

  for (let i = 0; i < quantidadeAglomerados; i++) {
    const centroX = x + Math.random() * largura;
    const centroY = y + Math.random() * altura;

    for (let j = 0; j < pontosPorAglomerado; j++) {
      const px = centroX + (Math.random() - 0.5) * raioAglomerado;
      const py = centroY + (Math.random() - 0.5) * raioAglomerado;
      const raio = 0.3 + Math.random() * 0.9;

      ctx.beginPath();
      ctx.arc(px, py, raio, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(0, 0, 0, 1)";
      ctx.fill();
    }
  }

  ctx.restore();
}

function calcularDimensoesProporcionais(img, { largura, altura } = {}) {
  const aspectRatio = img.width / img.height;

  if (largura && !altura) {
    return { largura, altura: largura / aspectRatio };
  }
  if (altura && !largura) {
    return { largura: altura * aspectRatio, altura };
  }
  if (largura && altura) {
    return { largura, altura: largura / aspectRatio };
  }
  return { largura: img.width, altura: img.height };
}

export function desenharElemento(
  ctx,
  el,
  canvas,
  baseX = 0,
  baseY = 0,
  larguraRef = canvas.width,
  alturaRef = canvas.height,
) {
  const centerX = baseX + el.xPercent * larguraRef;
  const centerY = baseY + el.yPercent * alturaRef;

  switch (el.tipo) {
    case "texto": {
      desenharTexto(ctx, el, baseX, baseY, larguraRef, alturaRef);
      break;
    }

    case "imagem": {
      if (!el.imagemCarregada) {
        console.warn("Imagem dinâmica sem pré-carregamento:", el.url);
        return;
      }

      const { largura, altura } = calcularDimensoesProporcionais(
        el.imagemCarregada,
        {
          largura: el.largura,
          altura: el.altura,
        },
      );

      const x = centerX - largura / 2;
      const y = centerY - altura / 2;

      if (el.falhaTinta) {
        // desenha num canvas separado: o "destination-out" só pode revelar o
        // template por baixo se os furos forem transparência de verdade nesse
        // sprite, e não um apagamento direto no canvas final já mesclado
        const spriteCanvas = document.createElement("canvas");
        spriteCanvas.width = largura;
        spriteCanvas.height = altura;
        const spriteCtx = spriteCanvas.getContext("2d");

        spriteCtx.filter = el.filtro || "none";
        spriteCtx.drawImage(el.imagemCarregada, 0, 0, largura, altura);
        spriteCtx.filter = "none";

        aplicarFalhaDeTinta(
          spriteCtx,
          0,
          0,
          largura,
          altura,
          el.falhaTintaIntensidade,
        );

        ctx.drawImage(spriteCanvas, x, y);
      } else {
        ctx.filter = el.filtro || "none";
        ctx.drawImage(el.imagemCarregada, x, y, largura, altura);
        ctx.filter = "none";
      }

      (el.elementos || []).forEach((filho) => {
        desenharElemento(ctx, filho, canvas, x, y, largura, altura);
      });
      break;
    }

    case "retangulo": {
      const x = centerX - el.largura / 2;
      const y = centerY - el.altura / 2;
      ctx.fillStyle = el.cor;
      ctx.fillRect(x, y, el.largura, el.altura);
      break;
    }

    default:
      console.warn("Tipo de elemento desconhecido:", el.tipo);
  }
}
