const USAR_MOCK = true; // troque pra false quando o backend estiver pronto

const DADOS_MOCK = {
  nome: "Nícolas Silva Gomes",
  role: "FRONTEND",
  title: "ESPECIALISTA",
};

export async function buscarDadosPassaporte(id) {
  if (USAR_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(DADOS_MOCK), 300);
    });
  }

  const res = await fetch(`/api/passaporte/${id}`);

  if (!res.ok) {
    throw new Error(`Erro ${res.status} ao buscar dados do passaporte`);
  }

  return res.json();
}
