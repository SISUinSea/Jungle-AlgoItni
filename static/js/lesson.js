document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-progress-root]");
  const lessonDataNode = document.getElementById("lesson-data");
  if (!root || !lessonDataNode || !window.algoitniProgress) return;

  const slug = root.dataset.algorithmSlug;
  if (!slug) return;

  const progress = window.algoitniProgress.loadProgress(slug);
  const currentStage = document.getElementById("progress-current-stage");
  const passedStages = document.getElementById("progress-passed-stages");
  const attempts = document.getElementById("progress-attempts");
  const lessonCompleted = document.getElementById("progress-lesson-completed");
  const problemCta = document.getElementById("problem-cta");

  if (currentStage) currentStage.textContent = progress.currentStage;
  if (passedStages) passedStages.textContent = JSON.stringify(progress.passedStages);
  if (attempts) attempts.textContent = String(progress.attempts);
  if (lessonCompleted) lessonCompleted.textContent = String(progress.lessonCompleted);

  window.localStorage.setItem(window.algoitniProgress.ALGOITNI_LAST_ALGORITHM_KEY, slug);

  if (problemCta && progress.lessonCompleted) {
    problemCta.dataset.problemCtaDisabled = "false";
    problemCta.setAttribute("aria-disabled", "false");
    problemCta.classList.remove("text-stone-400");
    problemCta.classList.add("text-white");
    problemCta.textContent = "실전 문제로 이동";
  }
});
