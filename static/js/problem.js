document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-problem-root]");
  const slug = root?.dataset.algorithmSlug || window.location.pathname.split("/")[2];
  const lessonUrl = root?.dataset.lessonUrl;
  if (!slug || !window.algoitniProgress) return;

  const progress = window.algoitniProgress.loadProgress(slug);
  if (!progress.lessonCompleted && lessonUrl) {
    window.location.replace(lessonUrl);
    return;
  }

  window.localStorage.setItem(window.algoitniProgress.ALGOITNI_LAST_ALGORITHM_KEY, slug);
});
