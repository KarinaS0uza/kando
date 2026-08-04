// src/hooks/useImageComposer.js
import { useState, useCallback } from "react";
import { gerarImagemFinal } from "../services/imageComposer";

export function useImageComposer() {
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);

  // src/hooks/useImageComposer.js
  const gerar = useCallback(async (config) => {
    setLoading(true);
    setErro(null);
    try {
      const res = await gerarImagemFinal(config);
      setResultado(res);
      return res;
    } catch (e) {
      console.error("Erro ao gerar imagem:", e); // ← adicione isso
      setErro(e);
    } finally {
      setLoading(false);
    }
  }, []);

  return { gerar, loading, resultado, erro };
}
