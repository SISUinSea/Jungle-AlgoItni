function shouldAllowProblemAccess(progressState) {
  return Boolean(progressState?.lessonCompleted);
}

function lessonPathFor(slug) {
  return `/algorithms/${slug}/lesson`;
}

function initializeProblemPage() {
  const root = document.querySelector("[data-problem-root]");
  const slug = root?.dataset.algorithmSlug || window.location.pathname.split("/")[2];
  const lessonUrl = root?.dataset.lessonUrl || (slug ? lessonPathFor(slug) : "");
  if (!slug || !window.algoitniProgress) return;

  const progressApi = window.algoitniProgress;
  const progress = progressApi.loadProgress(slug);
  progressApi.setLastAlgorithm(slug);

  if (!progress.lessonCompleted && lessonUrl) {
    window.location.replace(lessonUrl);
    return;
  }

  if (!shouldAllowProblemAccess(progress) && lessonUrl) {
    window.location.replace(lessonUrl);
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
