import axios from "axios";

// Raw API client for the /passports/ endpoints. Not to be confused with
// passportService.js, which aggregates this file's + api.js's responses
// into the view-model PassportCertificate.jsx actually consumes.
// See services/api.js for the note on the hardcoded baseURL and the
// duplicated Bearer-token interceptor.
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

/** Triggers generation of a Talent Passport for a resume/job pair. @param {string|number} resumeId @param {string|number} jobId */
export const createPassport = (resumeId, jobId) => {
  return apiClient.post(`/passports/`, {
    resume_id: resumeId,
    job_id: jobId,
  });
};

/** Lists the current user's generated passports. */
export const listPassports = () => {
  return apiClient.get(`/passports/`);
};

/**
 * Submits the candidate's self-perceived readiness (Reliability page's two
 * slider questions). Called fire-and-forget by Reliability.jsx - its
 * failure is swallowed there and doesn't block navigation, since it's a
 * best-effort signal, not something the flow depends on.
 * @param {string|number} resumeId
 * @param {string|number} jobId
 * @param {number} perceivedPreparationPercentage
 * @param {number} applicationThresholdPercentage
 */
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
