const ALGOITNI_PROGRESS_PREFIX = "algostep_progress::";
const ALGOITNI_LAST_ALGORITHM_KEY = "algostep_last_algorithm";
const ALGOITNI_STAGES = ["blank", "parsons", "problem"];

const defaultProgressState = {
  currentStage: "blank",
  passedStages: [],
  attempts: 0,
  lessonCompleted: false,
};

function uniqueStages(stages) {
  return Array.from(new Set(stages.filter((stage) => ALGOITNI_STAGES.includes(stage))));
}

function normalizeProgressState(state = {}) {
  const attempts = Number.isFinite(Number(state.attempts)) ? Math.max(0, Number(state.attempts)) : 0;
  const lessonCompleted = Boolean(state.lessonCompleted);
  const passedStages = uniqueStages(Array.isArray(state.passedStages) ? state.passedStages : []);
  let currentStage = ALGOITNI_STAGES.includes(state.currentStage) ? state.currentStage : "blank";

  if (lessonCompleted || passedStages.includes("parsons")) {
    currentStage = "problem";
  } else if (passedStages.includes("blank")) {
    currentStage = "parsons";
  }

  return {
    currentStage,
    passedStages,
    attempts,
    lessonCompleted: lessonCompleted || currentStage === "problem",
  };
}

function progressKey(algorithmSlug) {
  return `${ALGOITNI_PROGRESS_PREFIX}${algorithmSlug}`;
}

function loadProgress(algorithmSlug) {
  const raw = window.localStorage.getItem(progressKey(algorithmSlug));
  if (!raw) return { ...defaultProgressState };

  try {
    return normalizeProgressState({ ...defaultProgressState, ...JSON.parse(raw) });
  } catch (_error) {
    return { ...defaultProgressState };
  }
}

function saveProgress(algorithmSlug, nextState) {
  const state = normalizeProgressState({ ...defaultProgressState, ...nextState });
  window.localStorage.setItem(progressKey(algorithmSlug), JSON.stringify(state));
  return state;
}

function recordAttempt(progressState) {
  return normalizeProgressState({
    ...progressState,
    attempts: Number(progressState.attempts || 0) + 1,
  });
}

function markStagePassed(progressState, stage) {
  const nextPassedStages = uniqueStages([...(progressState.passedStages || []), stage]);
  return normalizeProgressState({
    ...progressState,
    passedStages: nextPassedStages,
    lessonCompleted: nextPassedStages.includes("parsons"),
  });
}

function describeProgress(progressState) {
  if (progressState.lessonCompleted) {
    return "레슨 완료. 실전 문제로 이동할 수 있습니다.";
  }
  if (progressState.passedStages.includes("blank")) {
    return "빈칸 통과 완료. 파슨스 단계를 진행하세요.";
  }
  if (progressState.attempts > 0) {
    return `빈칸 단계 진행 중. 현재까지 ${progressState.attempts}회 제출했습니다.`;
  }
  return "아직 레슨을 시작하지 않았습니다.";
}

function setLastAlgorithm(algorithmSlug) {
  if (!algorithmSlug) return;
  window.localStorage.setItem(ALGOITNI_LAST_ALGORITHM_KEY, algorithmSlug);
}

function setLinkEnabled(link, enabled, enabledText) {
  if (!link) return;
  const storedHref = link.dataset.href || link.getAttribute("href") || "";

  if (enabled) {
    if (storedHref) {
      link.dataset.href = storedHref;
      link.setAttribute("href", storedHref);
    }
    link.setAttribute("aria-disabled", "false");
    link.removeAttribute("tabindex");
    link.classList.remove("text-stone-500", "text-stone-400");
    link.classList.add("text-white");
    if (enabledText) link.textContent = enabledText;
    return;
  }

  if (storedHref) {
    link.dataset.href = storedHref;
  }
  link.removeAttribute("href");
  link.setAttribute("aria-disabled", "true");
  link.setAttribute("tabindex", "-1");
  link.classList.remove("text-white");
  link.classList.add("text-stone-500");
}

function guardDisabledLinks() {
  document.querySelectorAll('a[aria-disabled="true"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      if (link.getAttribute("aria-disabled") === "true") {
        event.preventDefault();
      }
    });
  });
}

function hydrateHomeProgress() {
  const root = document.querySelector("[data-home-root]");
  if (!root) return;

  const resumeCard = root.querySelector("[data-resume-card]");
  const resumeCopy = root.querySelector("[data-resume-copy]");
  const resumeLesson = root.querySelector("[data-resume-lesson]");
  const resumeProblem = root.querySelector("[data-resume-problem]");

  document.querySelectorAll("[data-algorithm-card]").forEach((card) => {
    const slug = card.dataset.algorithmSlug;
    if (!slug) return;

    const state = loadProgress(slug);
    const progressSummary = card.querySelector("[data-progress-summary]");
    const problemStatus = card.querySelector("[data-problem-status]");
    const problemLink = card.querySelector("[data-problem-link]");

    if (progressSummary) progressSummary.textContent = describeProgress(state);
    if (problemStatus) {
      problemStatus.textContent = state.lessonCompleted
        ? "실전 문제가 열려 있습니다."
        : "실전 문제는 레슨 완료 후 열립니다.";
    }
    setLinkEnabled(problemLink, state.lessonCompleted, "문제");
  });

  const lastAlgorithm = window.localStorage.getItem(ALGOITNI_LAST_ALGORITHM_KEY);
  if (!lastAlgorithm || !resumeCard || !resumeCopy || !resumeLesson || !resumeProblem) return;

  const lastState = loadProgress(lastAlgorithm);
  resumeCard.classList.remove("hidden");
  resumeCopy.textContent = `${lastAlgorithm} · ${describeProgress(lastState)}`;
  resumeLesson.href = `/algorithms/${lastAlgorithm}/lesson`;
  resumeProblem.dataset.href = `/algorithms/${lastAlgorithm}/problem`;
  setLinkEnabled(resumeProblem, lastState.lessonCompleted, lastState.lessonCompleted ? "실전 문제" : "실전 문제 잠김");
}

function hydrateConceptProgress() {
  const root = document.querySelector("[data-concept-root]");
  if (!root) return;

  const slug = root.dataset.algorithmSlug;
  if (!slug) return;

  const state = loadProgress(slug);
  setLastAlgorithm(slug);

  const currentStage = root.querySelector("[data-concept-current-stage]");
  const passedStages = root.querySelector("[data-concept-passed-stages]");
  const stageCopy = root.querySelector("[data-concept-stage-copy]");
  const lessonLink = root.querySelector("[data-concept-lesson-link]");
  const problemLink = root.querySelector("[data-concept-problem-link]");

  if (currentStage) currentStage.textContent = state.currentStage;
  if (passedStages) passedStages.textContent = JSON.stringify(state.passedStages);
  if (stageCopy) stageCopy.textContent = describeProgress(state);
  if (lessonLink) lessonLink.textContent = state.passedStages.length > 0 ? "대표 레슨 이어서" : "대표 레슨 시작";
  setLinkEnabled(problemLink, state.lessonCompleted, state.lessonCompleted ? "실전 문제로 이동" : "실전 문제는 레슨 완료 후 열림");
}

const progressApi = {
  ALGOITNI_PROGRESS_PREFIX,
  ALGOITNI_LAST_ALGORITHM_KEY,
  ALGOITNI_STAGES,
  defaultProgressState,
  normalizeProgressState,
  progressKey,
  loadProgress,
  saveProgress,
  recordAttempt,
  markStagePassed,
  describeProgress,
  setLastAlgorithm,
  setLinkEnabled,
};

if (typeof window !== "undefined") {
  window.algoitniProgress = progressApi;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = progressApi;
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const lessonRoot = document.querySelector("[data-lesson-root]");
    if (lessonRoot?.dataset.algorithmSlug) {
      setLastAlgorithm(lessonRoot.dataset.algorithmSlug);
    }
    hydrateHomeProgress();
    hydrateConceptProgress();
    guardDisabledLinks();
  });
}
