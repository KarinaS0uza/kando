// src/hooks/useImageComposer.js
import { useState, useCallback } from "react";
import { gerarImagemFinal } from "../services/imageComposer";

/**
 * Async-state wrapper around the canvas image-composer service
 * (gerarImagemFinal), used by PassportCertificate to render the Talent
 * Passport certificate.
 * @returns {{
 *   gerar: (config: object) => Promise<{blob: Blob, dataUrl: string, canvas: HTMLCanvasElement}|undefined>,
 *   loading: boolean,
 *   resultado: object|null,
 *   erro: Error|null,
 * }}
 *   `gerar` never rejects - on failure it resolves to `undefined` and
 *   populates `erro` instead, so callers must check `erro`/`resultado`
 *   rather than try/catch around `gerar()`.
 */
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
