export function resolverCorElementos(elemento, corHerdada) {
  const corFinal = elemento.cor || corHerdada;

  const elementosResolvidos = (elemento.elementos || []).map((filho) =>
    resolverCorElementos(filho, corFinal),
  );

  return {
    ...elemento,
    cor: corFinal,
    elementos: elementosResolvidos,
  };
}
