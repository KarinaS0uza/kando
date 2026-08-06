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
