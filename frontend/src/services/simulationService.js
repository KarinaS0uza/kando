const MOCK_QUESTIONS = [
  {
    id: "q1",
    area: "React",
    enunciado: "O que é o Virtual DOM e por que o React o utiliza?",
    criterioResposta:
      "Deve mencionar que é uma representação em memória da UI, e que o React o usa para otimizar re-renderizações comparando (diffing) antes de atualizar o DOM real.",
  },
  {
    id: "q2",
    area: "Git",
    enunciado: 'Qual a diferença entre "git merge" e "git rebase"?',
    criterioResposta:
      "Deve explicar que merge cria um commit de junção preservando o histórico das duas branches, enquanto rebase reescreve o histórico aplicando os commits sobre a outra branch, mantendo o histórico linear.",
  },
  {
    id: "q3",
    area: "Lógica",
    enunciado:
      "Explique com suas palavras a diferença entre complexidade de tempo O(n) e O(n²).",
    criterioResposta:
      "Deve indicar que O(n) cresce linearmente com o tamanho da entrada, enquanto O(n²) cresce proporcionalmente ao quadrado da entrada, geralmente por conta de loops aninhados.",
  },
  {
    id: "q4",
    area: "APIs",
    enunciado:
      "O que diferencia uma requisição PUT de uma PATCH em uma API REST?",
    criterioResposta:
      "Deve indicar que PUT substitui o recurso inteiro, enquanto PATCH aplica uma atualização parcial, modificando apenas os campos enviados.",
  },
  {
    id: "q5",
    area: "SQL",
    enunciado:
      "O que é uma JOIN e quando você usaria um LEFT JOIN em vez de um INNER JOIN?",
    criterioResposta:
      "Deve explicar que JOIN combina dados de duas tabelas, e que LEFT JOIN retorna todos os registros da tabela da esquerda mesmo sem correspondência na direita, diferente do INNER JOIN que só retorna registros com correspondência em ambas.",
  },
  {
    id: "q6",
    area: "React",
    enunciado: "Para que serve o hook useEffect e quando ele é executado?",
    criterioResposta:
      "Deve mencionar que useEffect lida com efeitos colaterais (side effects) como chamadas de API ou subscriptions, e que roda após a renderização, podendo ser controlado por um array de dependências.",
  },
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const simulationService = {
  async getQuestions() {
    await delay(500);
    return MOCK_QUESTIONS;
  },

  async submitAnswers(answers) {
    await delay(500);
    console.log("Respostas enviadas:", answers);
    return { status: "ok" };
  },
};

export default simulationService;
