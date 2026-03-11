const test = require("node:test");
const assert = require("node:assert/strict");

const {
  normalizeProgressState,
  recordAttempt,
  markStagePassed,
  describeProgress,
} = require("../static/js/progress.js");

test("normalizeProgressState promotes blank pass to parsons stage", () => {
  const state = normalizeProgressState({
    currentStage: "blank",
    passedStages: ["blank"],
    attempts: 1,
    lessonCompleted: false,
  });

  assert.equal(state.currentStage, "parsons");
  assert.equal(state.lessonCompleted, false);
});

test("markStagePassed completes lesson after parsons", () => {
  const state = markStagePassed(
    {
      currentStage: "parsons",
      passedStages: ["blank"],
      attempts: 2,
      lessonCompleted: false,
    },
    "parsons",
  );

  assert.deepEqual(state.passedStages, ["blank", "parsons"]);
  assert.equal(state.lessonCompleted, true);
  assert.equal(state.currentStage, "problem");
});

test("recordAttempt increments attempts", () => {
  const state = recordAttempt({
    currentStage: "blank",
    passedStages: [],
    attempts: 0,
    lessonCompleted: false,
  });

  assert.equal(state.attempts, 1);
});

test("describeProgress reflects completion", () => {
  assert.equal(
    describeProgress({
      currentStage: "problem",
      passedStages: ["blank", "parsons"],
      attempts: 3,
      lessonCompleted: true,
    }),
    "레슨 완료. 실전 문제로 이동할 수 있습니다.",
  );
});
