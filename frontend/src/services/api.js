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

export const setAPIJobText = (jobInfo) => {
  return apiClient.post(`/job-postings/`, jobInfo);
};
