import { createMatch } from "../services/api";

let jobPostingPromise = null;
let resumePromise = null;
let matchPromise = null;

export const setUploadPromises = (jobP, resumeP) => {
  jobPostingPromise = jobP;
  resumePromise = resumeP;
};

export const waitForUploads = () => {
  return Promise.allSettled([jobPostingPromise, resumePromise]);
};

export const startMatch = (resumeId, jobId) => {
  matchPromise = createMatch(resumeId, jobId);
  return matchPromise;
};

export const waitForMatch = () => {
  return matchPromise;
};
