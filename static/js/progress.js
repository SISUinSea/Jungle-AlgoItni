const ALGOITNI_PROGRESS_PREFIX = "algostep_progress::";
const ALGOITNI_LAST_ALGORITHM_KEY = "algostep_last_algorithm";
const ALGOITNI_STAGES = ["blank", "parsons", "problem"];
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
const inactiveProblemLinkClasses = ["text-stone-400", "text-stone-500"];
const lockedProblemLinkClasses = ["pointer-events-none", "cursor-not-allowed", "opacity-60"];

function uniqueStages(stages) {
  return Array.from(new Set(stages.filter((stage) => ALGOITNI_STAGES.includes(stage))));
}

function normalizeAttempts(attempts) {
  if (!attempts || typeof attempts !== "object" || Array.isArray(attempts)) {
    if (Number.isFinite(Number(attempts))) {
      const total = Math.max(0, Number(attempts));
      return { blank: total, parsons: 0 };
    }
    return { ...defaultAttempts };
  }

  return {
    blank: Number.isFinite(Number(attempts.blank)) ? Math.max(0, Number(attempts.blank)) : 0,
    parsons: Number.isFinite(Number(attempts.parsons)) ? Math.max(0, Number(attempts.parsons)) : 0,
  };
}

function normalizeProgressState(state = {}) {
  const attempts = normalizeAttempts(state.attempts);
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
  if (!raw) return { ...defaultProgressState, attempts: { ...defaultAttempts } };

  try {
    const parsed = JSON.parse(raw);
    return normalizeProgressState({ ...defaultProgressState, ...parsed });
  } catch (_error) {
    return { ...defaultProgressState, attempts: { ...defaultAttempts } };
  }
}

function saveProgress(algorithmSlug, nextState) {
  const state = normalizeProgressState({ ...defaultProgressState, ...nextState });
  window.localStorage.setItem(progressKey(algorithmSlug), JSON.stringify(state));
  return state;
}

function recordAttempt(progressState, stage) {
  const attempts = normalizeAttempts(progressState.attempts);
  return normalizeProgressState({
    ...progressState,
    attempts: {
      ...attempts,
      [stage]: (attempts[stage] || 0) + 1,
    },
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
  const attempts = normalizeAttempts(progressState.attempts);
  const totalAttempts = attempts.blank + attempts.parsons;

  if (progressState.lessonCompleted) {
    return "레슨 완료. 실전 문제로 이동할 수 있습니다.";
  }
  if (progressState.passedStages.includes("blank")) {
    return "빈칸 통과 완료. 파슨스 단계를 진행하세요.";
  }
  if (totalAttempts > 0) {
    return `빈칸 단계 진행 중. 현재까지 ${totalAttempts}회 제출했습니다.`;
  }
  return "아직 레슨을 시작하지 않았습니다.";
}

function setLastAlgorithm(algorithmSlug) {
  if (!algorithmSlug) return;
  window.localStorage.setItem(ALGOITNI_LAST_ALGORITHM_KEY, algorithmSlug);
}

function setLinkEnabled(link, enabled, enabledText) {
  if (!link) return;
  const storedHref = link.dataset.problemUrl || link.dataset.href || link.getAttribute("href") || "";

  if (enabled) {
    if (storedHref) {
      if (link.dataset.problemUrl) link.dataset.problemUrl = storedHref;
      else link.dataset.href = storedHref;
      link.setAttribute("href", storedHref);
    }
    link.setAttribute("aria-disabled", "false");
    link.removeAttribute("tabindex");
    link.classList.remove(...lockedProblemLinkClasses);
    link.classList.remove(...inactiveProblemLinkClasses);
    link.classList.add(...activeProblemLinkClasses);
    if (enabledText) link.textContent = enabledText;
    return;
  }

  if (storedHref) {
    if (link.dataset.problemUrl) link.dataset.problemUrl = storedHref;
    else link.dataset.href = storedHref;
  }
  link.removeAttribute("href");
  link.setAttribute("aria-disabled", "true");
  link.setAttribute("tabindex", "-1");
  link.classList.add(...lockedProblemLinkClasses);
  link.classList.remove(...activeProblemLinkClasses);
  link.classList.add(...inactiveProblemLinkClasses);
}

function isLessonCompleted(algorithmSlug) {
  return loadProgress(algorithmSlug).lessonCompleted === true;
}

function setProblemLinkState(link, algorithmSlug) {
  if (!link || !algorithmSlug) return false;
  const isUnlocked = isLessonCompleted(algorithmSlug);
  setLinkEnabled(link, isUnlocked);
  return isUnlocked;
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
    setProblemLinkState(problemLink, slug);
  });

  const lastAlgorithm = window.localStorage.getItem(ALGOITNI_LAST_ALGORITHM_KEY);
  if (!lastAlgorithm || !resumeCard || !resumeCopy || !resumeLesson || !resumeProblem) return;

  const lastState = loadProgress(lastAlgorithm);
  resumeCard.classList.remove("hidden");
  resumeCopy.textContent = `${lastAlgorithm} · ${describeProgress(lastState)}`;
  resumeLesson.href = `/algorithms/${lastAlgorithm}/lesson`;
  resumeProblem.dataset.problemUrl = `/algorithms/${lastAlgorithm}/problem`;
  resumeProblem.dataset.algorithmSlug = lastAlgorithm;
  setProblemLinkState(resumeProblem, lastAlgorithm);
  if (!lastState.lessonCompleted) {
    resumeProblem.textContent = "실전 문제 잠김";
  }
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
  const unlocked = setProblemLinkState(problemLink, slug);
  if (problemLink && !unlocked) {
    problemLink.textContent = "실전 문제는 레슨 완료 후 열림";
  } else if (problemLink && unlocked) {
    problemLink.textContent = "실전 문제로 이동";
  }
}

const progressApi = {
  ALGOITNI_PROGRESS_PREFIX,
  ALGOITNI_LAST_ALGORITHM_KEY,
  ALGOITNI_STAGES,
  defaultAttempts,
  defaultProgressState,
  activeProblemLinkClasses,
  inactiveProblemLinkClasses,
  lockedProblemLinkClasses,
  uniqueStages,
  normalizeAttempts,
  normalizeProgressState,
  progressKey,
  loadProgress,
  saveProgress,
  recordAttempt,
  markStagePassed,
  describeProgress,
  setLastAlgorithm,
  setLinkEnabled,
  isLessonCompleted,
  setProblemLinkState,
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
