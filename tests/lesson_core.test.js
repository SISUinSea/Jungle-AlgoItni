const test = require("node:test");
const assert = require("node:assert/strict");

const {
  normalizeCode,
  gradeBlankExercise,
  gradeParsonsExercise,
} = require("../static/js/lesson_core.js");

test("normalizeCode removes whitespace differences", () => {
  assert.equal(normalizeCode(" left = mid + 1 "), "left=mid+1");
});

test("gradeBlankExercise accepts canonical and accepted answers", () => {
  const result = gradeBlankExercise(
    {
      blanks: [
        {
          id: "b1",
          answer: "mid = (left + right) // 2",
          acceptedAnswers: ["mid=(left+right)//2"],
          hint: "mid",
        },
      ],
    },
    { b1: "mid=(left+right)//2" },
  );

  assert.equal(result.passed, true);
  assert.equal(result.incorrectIds.length, 0);
});

test("gradeBlankExercise reports incorrect blanks", () => {
  const result = gradeBlankExercise(
    {
      blanks: [
        {
          id: "b2",
          answer: "left = mid + 1",
          acceptedAnswers: [],
          hint: "left",
        },
      ],
    },
    { b2: "right = mid - 1" },
  );

  assert.equal(result.passed, false);
  assert.deepEqual(result.incorrectIds, ["b2"]);
});

test("gradeParsonsExercise passes only on exact answer order", () => {
  const exercise = {
    answerOrder: [0, 1, 2, 3],
    groupedIndices: [[2, 3]],
  };

  assert.equal(gradeParsonsExercise(exercise, [0, 1, 2, 3]).passed, true);
  assert.equal(gradeParsonsExercise(exercise, [0, 2, 1, 3]).passed, false);
});

test("gradeParsonsExercise detects broken grouped blocks", () => {
  const result = gradeParsonsExercise(
    {
      answerOrder: [0, 1, 2, 3, 4],
      groupedIndices: [[1, 2]],
    },
    [0, 2, 3, 1, 4],
  );

  assert.equal(result.passed, false);
  assert.equal(result.brokenGroups.length, 1);
});
