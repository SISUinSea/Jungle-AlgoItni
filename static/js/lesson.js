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
  const blankPassButton = document.getElementById("blank-pass-button");
  const parsonsPassButton = document.getElementById("parsons-pass-button");
  const progressResetButton = document.getElementById("progress-reset-button");
  const progressFeedback = document.getElementById("progress-feedback");

  function setFeedback(message) {
    if (progressFeedback) progressFeedback.textContent = message;
  }

  function renderProgress(nextProgress) {
    if (currentStage) currentStage.textContent = nextProgress.currentStage;
    if (passedStages) passedStages.textContent = JSON.stringify(nextProgress.passedStages);
    if (attempts) attempts.textContent = JSON.stringify(nextProgress.attempts);
    if (lessonCompleted) lessonCompleted.textContent = String(nextProgress.lessonCompleted);

    if (problemCta) {
      const unlocked = window.algoitniProgress.setProblemLinkState(problemCta, slug);
      problemCta.textContent = unlocked
        ? "실전 문제로 이동"
        : "lessonCompleted === true 일 때만 활성화";
    }

    if (blankPassButton) {
      blankPassButton.disabled = nextProgress.passedStages.includes("blank");
      blankPassButton.classList.toggle("opacity-60", blankPassButton.disabled);
      blankPassButton.classList.toggle("cursor-not-allowed", blankPassButton.disabled);
    }

    if (parsonsPassButton) {
      const parsonsLocked = !nextProgress.passedStages.includes("blank")
        || nextProgress.lessonCompleted;
      parsonsPassButton.disabled = parsonsLocked;
      parsonsPassButton.classList.toggle("opacity-60", parsonsLocked);
      parsonsPassButton.classList.toggle("cursor-not-allowed", parsonsLocked);
    }
  }

  window.localStorage.setItem(window.algoitniProgress.ALGOITNI_LAST_ALGORITHM_KEY, slug);
  renderProgress(progress);

  if (blankPassButton) {
    blankPassButton.addEventListener("click", () => {
      const currentProgress = window.algoitniProgress.loadProgress(slug);
      const nextProgress = window.algoitniProgress.saveProgress(slug, {
        currentStage: "parsons",
        passedStages: [...new Set([...currentProgress.passedStages, "blank"])],
        attempts: {
          ...currentProgress.attempts,
          blank: currentProgress.attempts.blank + 1,
        },
        lessonCompleted: false,
      });
      renderProgress(nextProgress);
      setFeedback("빈칸 단계 통과 상태를 저장했습니다. 이제 파슨스 단계를 열 수 있습니다.");
    });
  }

  if (parsonsPassButton) {
    parsonsPassButton.addEventListener("click", () => {
      const currentProgress = window.algoitniProgress.loadProgress(slug);
      if (!currentProgress.passedStages.includes("blank")) {
        setFeedback("파슨스 단계 저장 전에는 빈칸 단계를 먼저 통과해야 합니다.");
        renderProgress(currentProgress);
        return;
      }

      const nextProgress = window.algoitniProgress.saveProgress(slug, {
        currentStage: "problem",
        passedStages: [...new Set([...currentProgress.passedStages, "parsons"])],
        attempts: {
          ...currentProgress.attempts,
          parsons: currentProgress.attempts.parsons + 1,
        },
        lessonCompleted: true,
      });
      renderProgress(nextProgress);
      setFeedback("파슨스 단계 통과 상태를 저장했습니다. 이제 실전 문제로 이동할 수 있습니다.");
    });
  }

  if (progressResetButton) {
    progressResetButton.addEventListener("click", () => {
      const resetProgress = window.algoitniProgress.saveProgress(
        slug,
        window.algoitniProgress.defaultProgressState,
      );
      renderProgress(resetProgress);
      setFeedback("진행 상태를 초기화했습니다.");
    });
  }
});
