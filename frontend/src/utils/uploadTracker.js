import { createMatch } from "../services/api";
import { createQuestions } from "../services/simulationService";

let jobPostingPromise = null;
let resumePromise = null;
let matchPromise = null;
let questionsPromise = null;

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

export const startQuestions = (resumeId, jobId) => {
  questionsPromise = createQuestions(resumeId, jobId);
  return questionsPromise;
};

export const waitForQuestions = () => {
  return questionsPromise;
};
