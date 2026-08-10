// Caches the in-flight/settled load per font name so concurrent callers (e.g.
// React StrictMode double-invoking the effect that calls gerarImagemFinal)
// reuse the same FontFace.load() instead of racing two network requests for
// the same font, which can make one of them fail with a NetworkError.
const carregamentosPorFonte = new Map();

export function carregarFonte(nomeFonte, url, fallback = "cursive") {
  if (carregamentosPorFonte.has(nomeFonte)) {
    return carregamentosPorFonte.get(nomeFonte);
  }

  const carregamento = (async () => {
    try {
      const font = new FontFace(nomeFonte, `url(${url})`);
      await font.load();
      document.fonts.add(font);
      console.log(`Fonte "${nomeFonte}" carregada com sucesso.`);
      return nomeFonte;
    } catch (erro) {
      console.warn(
        `Falha ao carregar fonte "${nomeFonte}", usando fallback "${fallback}".`,
        erro,
      );
      // não guarda a falha em cache: uma tentativa futura pode ter sucesso
      carregamentosPorFonte.delete(nomeFonte);
      return fallback;
    }
  })();

  carregamentosPorFonte.set(nomeFonte, carregamento);
  return carregamento;
}
