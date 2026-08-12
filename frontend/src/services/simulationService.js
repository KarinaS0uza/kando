import axios from "axios";

// See services/api.js for the note on the hardcoded baseURL and the
// Bearer-token interceptor being duplicated across this file, api.js and
// talentPassportService.js.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** Generates the technical assessment questions for a resume/job pair. @param {string|number} resumeId @param {string|number} jobId */
export const createQuestions = (resumeId, jobId) => {
  return apiClient.post(`/assessments/`, {
    resume_id: resumeId,
    job_id: jobId,
  });
};

/** Lists the current user's assessments. */
export const listAssessments = () => {
  return apiClient.get(`/assessments/`);
};

/** Submits the candidate's answers for grading. @param {string|number} assessmentId @param {*} answers */
export const gradeAnswers = (assessmentId, answers) => {
  return apiClient.post(`/assessments/${assessmentId}/result/`, { answers });
};
