const ALGOITNI_PROGRESS_PREFIX = "algostep_progress::";
const ALGOITNI_LAST_ALGORITHM_KEY = "algostep_last_algorithm";
const defaultAttempts = {
  blank: 0,
  parsons: 0,
};

const defaultProgressState = {
  currentStage: "blank",
  passedStages: [],
  attempts: defaultAttempts,
  lessonCompleted: false,
};
const activeProblemLinkClasses = ["text-white"];
const inactiveProblemLinkClasses = ["text-stone-400"];
const lockedProblemLinkClasses = ["pointer-events-none", "cursor-not-allowed", "opacity-60"];

function normalizeAttempts(attempts) {
  if (!attempts || typeof attempts !== "object" || Array.isArray(attempts)) {
    return { ...defaultAttempts };
  }

  return {
    blank: Number.isFinite(attempts.blank) ? attempts.blank : 0,
    parsons: Number.isFinite(attempts.parsons) ? attempts.parsons : 0,
  };
}

function progressKey(algorithmSlug) {
  return `${ALGOITNI_PROGRESS_PREFIX}${algorithmSlug}`;
}

function loadProgress(algorithmSlug) {
  const raw = window.localStorage.getItem(progressKey(algorithmSlug));
  if (!raw) return { ...defaultProgressState };

  try {
    const parsed = JSON.parse(raw);
    return {
      ...defaultProgressState,
      ...parsed,
      attempts: normalizeAttempts(parsed.attempts),
    };
  } catch (_error) {
    return { ...defaultProgressState };
  }
}

function saveProgress(algorithmSlug, nextState) {
  const state = {
    ...defaultProgressState,
    ...nextState,
    attempts: normalizeAttempts(nextState.attempts),
  };
  window.localStorage.setItem(progressKey(algorithmSlug), JSON.stringify(state));
  return state;
}

function isLessonCompleted(algorithmSlug) {
  return loadProgress(algorithmSlug).lessonCompleted === true;
}

function setProblemLinkState(link, algorithmSlug) {
  if (!link || !algorithmSlug) return false;

  const isUnlocked = isLessonCompleted(algorithmSlug);
  const problemUrl = link.dataset.problemUrl;

  if (isUnlocked && problemUrl) {
    link.setAttribute("href", problemUrl);
    link.setAttribute("aria-disabled", "false");
    link.dataset.problemLinkDisabled = "false";
    link.classList.remove(...lockedProblemLinkClasses);
    link.classList.remove(...inactiveProblemLinkClasses);
    link.classList.add(...activeProblemLinkClasses);
  } else {
    link.removeAttribute("href");
    link.setAttribute("aria-disabled", "true");
    link.dataset.problemLinkDisabled = "true";
    link.classList.add(...lockedProblemLinkClasses);
    link.classList.remove(...activeProblemLinkClasses);
    link.classList.add(...inactiveProblemLinkClasses);
  }

  return isUnlocked;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-problem-link]").forEach((link) => {
    const algorithmSlug = link.dataset.algorithmSlug;
    setProblemLinkState(link, algorithmSlug);
  });
});

window.algoitniProgress = {
  ALGOITNI_PROGRESS_PREFIX,
  ALGOITNI_LAST_ALGORITHM_KEY,
  defaultAttempts,
  defaultProgressState,
  activeProblemLinkClasses,
  inactiveProblemLinkClasses,
  lockedProblemLinkClasses,
  normalizeAttempts,
  progressKey,
  loadProgress,
  saveProgress,
  isLessonCompleted,
  setProblemLinkState,
};
