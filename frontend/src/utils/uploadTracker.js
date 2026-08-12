import { createMatch } from "../services/api";
import { createQuestions } from "../services/simulationService";

// Relays in-flight request promises across page navigations, so a page
// that kicks off a slow backend call (resume/job upload -> parse, match
// computation, question generation) doesn't have to block navigation on
// it, and the *next* page can pick up the same in-flight request instead
// of re-triggering it. This works because these are plain module-level
// variables: the module stays loaded across React Router navigations
// (it isn't a hook, so unmounting the page that started a request doesn't
// lose the promise), which is what lets UploadProfile.jsx fire off
// createResume/createJobPosting, hand the promises here, and navigate away
// immediately without awaiting them.
//
// Caveat: this state is a single unkeyed slot, not one per
// user/session/tab. Only one upload/match/questions cycle can be in
// flight app-wide at a time, there's no reset function, and starting a new
// cycle silently overwrites whatever the previous one left behind.
let jobPostingPromise = null;
let resumePromise = null;
let matchPromise = null;
let questionsPromise = null;

/** Stashes the in-flight createJobPosting/createResume promises kicked off by UploadProfile, for Reliability to await. */
export const setUploadPromises = (jobP, resumeP) => {
  jobPostingPromise = jobP;
  resumePromise = resumeP;
};

/**
 * Awaits both upload promises stashed by setUploadPromises.
 * @returns {Promise<[PromiseSettledResult, PromiseSettledResult]>}
 *   Uses allSettled (not all) so a failure in one upload doesn't hide the
 *   other's result - callers check `.status === "rejected"` on each entry.
 */
export const waitForUploads = () => {
  return Promise.allSettled([jobPostingPromise, resumePromise]);
};

/** Starts the match computation and stashes the promise for Score to await via waitForMatch. */
export const startMatch = (resumeId, jobId) => {
  matchPromise = createMatch(resumeId, jobId);
  return matchPromise;
};

/** @returns {Promise|null} the in-flight match promise started by startMatch, or null if none is pending. */
export const waitForMatch = () => {
  return matchPromise;
};

/** Starts the assessment-question generation and stashes the promise for SimulationQuestions to await via waitForQuestions. */
export const startQuestions = (resumeId, jobId) => {
  questionsPromise = createQuestions(resumeId, jobId);
  return questionsPromise;
};

/** @returns {Promise|null} the in-flight questions promise started by startQuestions, or null if none is pending. */
export const waitForQuestions = () => {
  return questionsPromise;
};
