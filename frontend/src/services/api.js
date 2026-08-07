import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api",
});

// Interceptor para adicionar o token automaticamente
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const createUser = (userInfo) => {
  return apiClient.post(`/users/create/`, userInfo);
};

export const login = (userInfo) => {
  return apiClient.post(`/login/`, userInfo);
};

// Monta o payload no formato { source: "text", raw_text } ou
// FormData com { source: "pdf", file } quando content é um File
function buildSourcePayload(content, extraFields = {}) {
  const isFile = content instanceof File;

  if (isFile) {
    const formData = new FormData();
    formData.append("source", "pdf");
    formData.append("pdf", content);
    Object.entries(extraFields).forEach(([key, value]) => {
      formData.append(key, value);
    });
    return { data: formData, isFormData: true };
  }

  return {
    data: { source: "text", raw_text: content, ...extraFields },
    isFormData: false,
  };
}

export const createJobPosting = (content, extraFields = {}) => {
  const { data, isFormData } = buildSourcePayload(content, extraFields);

  return apiClient.post(`/job-postings/`, data, {
    headers: isFormData ? { "Content-Type": "multipart/form-data" } : undefined,
  });
};

export const createResume = (content, extraFields = {}) => {
  const { data, isFormData } = buildSourcePayload(content, extraFields);

  return apiClient.post(`/resumes/`, data, {
    headers: isFormData ? { "Content-Type": "multipart/form-data" } : undefined,
  });
};

export const createMatch = (resumeId, jobId) => {
  return apiClient.post(`/matching/`, {
    resume_id: resumeId,
    job_id: jobId,
  });
};

export const listMatches = () => {
  return apiClient.get(`/matching/`);
};

// Mock temporário: o backend ainda não expõe /study-track/.
// TODO: trocar pelo apiClient.get(`/study-track/${matchId}/`) quando existir.
const MOCK_STUDY_TRACK = {
  titulo_trilha: "Trilha para Desenvolvedor Full-Stack Pleno",
  introducao:
    "Baseado no seu desempenho no desafio técnico e nos requisitos da vaga, montamos uma trilha priorizando as áreas com maior impacto na sua evolução.",
  itens: [
    {
      posicao: 1,
      skill: "PostgreSQL",
      tipo_recurso: null,
      sugestao_recurso: null,
      motivacao:
        "Bancos de dados relacionais são essenciais pra vagas full-stack, e foi sua área de maior dificuldade no teste.",
    },
    {
      posicao: 2,
      skill: "Angular",
      tipo_recurso: "curso",
      sugestao_recurso: "Curso introdutório de Angular",
      motivacao:
        "Essa é uma das tecnologias mais pedidas nas vagas que você buscou, e ainda não aparece no seu perfil.",
    },
    {
      posicao: 3,
      skill: "C#",
      tipo_recurso: "documentacao",
      sugestao_recurso: "Documentação oficial C#/.NET",
      motivacao:
        "Complementa bem seu conhecimento de backend, ampliando as vagas que você pode buscar.",
    },
  ],
};

export const getStudyTrack = () => {
  return Promise.resolve({ data: MOCK_STUDY_TRACK });
};
