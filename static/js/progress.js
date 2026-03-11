const ALGOITNI_PROGRESS_PREFIX = "algostep_progress::";
const ALGOITNI_LAST_ALGORITHM_KEY = "algostep_last_algorithm";

const defaultProgressState = {
  currentStage: "blank",
  passedStages: [],
  attempts: 0,
  lessonCompleted: false,
};

function progressKey(algorithmSlug) {
  return `${ALGOITNI_PROGRESS_PREFIX}${algorithmSlug}`;
}

function loadProgress(algorithmSlug) {
  const raw = window.localStorage.getItem(progressKey(algorithmSlug));
  if (!raw) return { ...defaultProgressState };

  try {
    return { ...defaultProgressState, ...JSON.parse(raw) };
  } catch (_error) {
    return { ...defaultProgressState };
  }
}

function saveProgress(algorithmSlug, nextState) {
  const state = { ...defaultProgressState, ...nextState };
  window.localStorage.setItem(progressKey(algorithmSlug), JSON.stringify(state));
  return state;
}

window.algoitniProgress = {
  ALGOITNI_PROGRESS_PREFIX,
  ALGOITNI_LAST_ALGORITHM_KEY,
  defaultProgressState,
  progressKey,
  loadProgress,
  saveProgress,
};
