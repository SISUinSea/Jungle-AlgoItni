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

window.algoitniProgress = {
  ALGOITNI_PROGRESS_PREFIX,
  ALGOITNI_LAST_ALGORITHM_KEY,
  defaultAttempts,
  defaultProgressState,
  normalizeAttempts,
  progressKey,
  loadProgress,
  saveProgress,
};
