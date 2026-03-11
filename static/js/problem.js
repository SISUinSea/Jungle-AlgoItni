function shouldAllowProblemAccess(progressState) {
  return Boolean(progressState?.lessonCompleted);
}

function lessonPathFor(slug) {
  return `/algorithms/${slug}/lesson`;
}

function initializeProblemPage() {
  const slug = window.location.pathname.split("/")[2];
  if (!slug || !window.algoitniProgress) return;

  const progressApi = window.algoitniProgress;
  const progress = progressApi.loadProgress(slug);
  progressApi.setLastAlgorithm(slug);

  if (!shouldAllowProblemAccess(progress)) {
    window.location.replace(lessonPathFor(slug));
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", initializeProblemPage);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    shouldAllowProblemAccess,
    lessonPathFor,
  };
}
