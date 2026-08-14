import axios from "axios";

// This same axios.create + Bearer-token interceptor pattern is duplicated
// (not shared) in simulationService.js and talentPassportService.js.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Public authentication endpoints must never inherit a stale session token.
const publicApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor para adicionar o token automaticamente
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** Creates a user account. @param {{email: string, password: string, full_name: string}} userInfo */
export const createUser = (userInfo) => {
  return publicApiClient.post(`/users/create/`, userInfo);
};

/** Logs in with email/password, returning the JWT access token + user id. @param {{email: string, password: string}} userInfo */
export const login = (userInfo) => {
  return publicApiClient.post(`/login/`, userInfo);
};

/** Fetches a user's profile (used for the full name shown on the certificate). @param {string|number} userId */
export const getUser = (userId) => {
  return apiClient.get(`/users/${userId}/`);
};

/**
 * Builds the request body for createJobPosting/createResume in whichever
 * shape the backend expects for that input: a JSON `{ source: "text",
 * raw_text }` body for pasted text, or a `source: "pdf"` FormData body
 * (field name "pdf") when `content` is a File - letting both callers
 * accept either a File or raw text transparently.
 * @param {string|File} content
 * @param {object} [extraFields]
 * @returns {{data: object|FormData, isFormData: boolean}}
 */
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

/** Submits a job posting (PDF File or pasted text) for the AI to parse. @param {string|File} content */
export const createJobPosting = (content, extraFields = {}) => {
  const { data, isFormData } = buildSourcePayload(content, extraFields);

  return apiClient.post(`/job-postings/`, data, {
    headers: isFormData ? { "Content-Type": "multipart/form-data" } : undefined,
  });
};

/** Submits a resume (PDF File or pasted text) for the AI to parse. @param {string|File} content */
export const createResume = (content, extraFields = {}) => {
  const { data, isFormData } = buildSourcePayload(content, extraFields);

  return apiClient.post(`/resumes/`, data, {
    headers: isFormData ? { "Content-Type": "multipart/form-data" } : undefined,
  });
};

/** Triggers the AI compatibility match between a resume and a job posting. @param {string|number} resumeId @param {string|number} jobId */
export const createMatch = (resumeId, jobId) => {
  return apiClient.post(`/matching/`, {
    resume_id: resumeId,
    job_id: jobId,
  });
};

/** Lists the current user's matches, most recent first. */
export const listMatches = () => {
  return apiClient.get(`/matching/`);
};
