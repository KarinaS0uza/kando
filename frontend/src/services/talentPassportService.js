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

export const createPassport = (resumeId, jobId) => {
  return apiClient.post(`/passports/`, {
    resume_id: resumeId,
    job_id: jobId,
  });
};

export const listPassports = () => {
  return apiClient.get(`/passports/`);
};

export const submitReadinessSelfAssessment = (
  resumeId,
  jobId,
  perceivedPreparationPercentage,
  applicationThresholdPercentage,
) => {
  return apiClient.post(`/passports/waiting-readiness/`, {
    resume_id: resumeId,
    job_id: jobId,
    perceived_preparation_percentage: perceivedPreparationPercentage,
    application_threshold_percentage: applicationThresholdPercentage,
  });
};
