export async function carregarFonte(nomeFonte, url, fallback = "cursive") {
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
    return fallback;
  }
}
