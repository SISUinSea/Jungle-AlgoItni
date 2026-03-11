const test = require("node:test");
const assert = require("node:assert/strict");

const {
  shouldAllowProblemAccess,
  lessonPathFor,
} = require("../static/js/problem.js");

test("shouldAllowProblemAccess blocks incomplete lesson state", () => {
  assert.equal(
    shouldAllowProblemAccess({
      lessonCompleted: false,
    }),
    false,
  );
});

test("shouldAllowProblemAccess allows completed lesson state", () => {
  assert.equal(
    shouldAllowProblemAccess({
      lessonCompleted: true,
    }),
    true,
  );
});

test("lessonPathFor returns the lesson route for a slug", () => {
  assert.equal(lessonPathFor("binary-search"), "/algorithms/binary-search/lesson");
});
