import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api",
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const createQuestions = (resumeId, jobId) => {
  return apiClient.post(`/assessments/`, {
    resume_id: resumeId,
    job_id: jobId,
  });
};

export const listAssessments = () => {
  return apiClient.get(`/assessments/`);
};

export const gradeAnswers = (assessmentId, answers) => {
  return apiClient.post(`/assessments/${assessmentId}/result/`, { answers });
};
