let jobPostingPromise = null;
let resumePromise = null;

export const setUploadPromises = (jobP, resumeP) => {
  jobPostingPromise = jobP;
  resumePromise = resumeP;
};

export const waitForUploads = () => {
  return Promise.allSettled([jobPostingPromise, resumePromise]);
};
