function normalizeCode(value) {
  return String(value ?? "")
    .trim()
    .replace(/\s+/g, "");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function acceptedBlankAnswers(blank) {
  return [blank.answer, ...(blank.acceptedAnswers || [])].map(normalizeCode);
}

function gradeBlankExercise(blankExercise, answers) {
  const blanks = (blankExercise.blanks || []).map((blank) => {
    const userAnswer = answers?.[blank.id] ?? "";
    const normalizedUserAnswer = normalizeCode(userAnswer);
    const normalizedAcceptedAnswers = acceptedBlankAnswers(blank);
    const correct = normalizedAcceptedAnswers.includes(normalizedUserAnswer);

    return {
      id: blank.id,
      correct,
      userAnswer,
      expectedAnswer: blank.answer,
      hint: blank.hint,
    };
  });

  return {
    passed: blanks.every((blank) => blank.correct),
    blanks,
    incorrectIds: blanks.filter((blank) => !blank.correct).map((blank) => blank.id),
  };
}

function gradeParsonsExercise(parsonsExercise, submittedOrder) {
  const expectedOrder = parsonsExercise.answerOrder || [];
  const matches =
    expectedOrder.length === submittedOrder.length &&
    expectedOrder.every((expectedIndex, index) => expectedIndex === submittedOrder[index]);

  const misplacedLines = submittedOrder
    .map((lineIndex, index) => ({
      index,
      lineIndex,
      expectedIndex: expectedOrder[index],
    }))
    .filter((entry) => entry.lineIndex !== entry.expectedIndex)
    .map((entry) => entry.index);

  const brokenGroups = (parsonsExercise.groupedIndices || []).filter((group) => {
    const positions = group
      .map((lineIndex) => submittedOrder.indexOf(lineIndex))
      .sort((left, right) => left - right);

    if (positions.some((position) => position < 0)) {
      return true;
    }

    for (let index = 1; index < positions.length; index += 1) {
      if (positions[index] !== positions[index - 1] + 1) {
        return true;
      }
    }

    return false;
  });

  return {
    passed: matches,
    misplacedLines,
    brokenGroups,
  };
}

const lessonCoreApi = {
  escapeHtml,
  normalizeCode,
  acceptedBlankAnswers,
  gradeBlankExercise,
  gradeParsonsExercise,
};

if (typeof window !== "undefined") {
  window.algoitniLessonCore = lessonCoreApi;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = lessonCoreApi;
}
