document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-lesson-root]");
  const lessonDataNode = document.getElementById("lesson-data");
  if (!root || !lessonDataNode || !window.algoitniProgress || !window.algoitniLessonCore) return;

  const slug = root.dataset.algorithmSlug;
  if (!slug) return;

  const progressApi = window.algoitniProgress;
  const lessonCore = window.algoitniLessonCore;
  const lesson = JSON.parse(lessonDataNode.textContent);
  let progress = progressApi.loadProgress(slug);
  let parsonsOrder = lesson.parsonsExercise.lines.map((_line, index) => index);

  const currentStage = document.getElementById("progress-current-stage");
  const passedStages = document.getElementById("progress-passed-stages");
  const attempts = document.getElementById("progress-attempts");
  const lessonCompleted = document.getElementById("progress-lesson-completed");
  const problemCta = document.getElementById("problem-cta");
  const blankForm = document.getElementById("blank-form");
  const blankSubmit = document.getElementById("blank-submit");
  const blankReset = document.getElementById("blank-reset");
  const blankFeedback = document.getElementById("blank-feedback");
  const blankBadge = document.getElementById("blank-stage-badge");
  const parsonsList = document.getElementById("parsons-list");
  const parsonsSubmit = document.getElementById("parsons-submit");
  const parsonsReset = document.getElementById("parsons-reset");
  const parsonsFeedback = document.getElementById("parsons-feedback");
  const parsonsBadge = document.getElementById("parsons-stage-badge");
  const parsonsLockedCopy = document.getElementById("parsons-locked-copy");
  const lessonSummary = document.getElementById("lesson-summary");
  const blankPassButton = document.getElementById("blank-pass-button");
  const parsonsPassButton = document.getElementById("parsons-pass-button");
  const progressResetButton = document.getElementById("progress-reset-button");
  const progressFeedback = document.getElementById("progress-feedback");
  const chatQuestion = document.getElementById("lesson-chat-question");
  const chatSubmit = document.getElementById("lesson-chat-submit");
  const chatReset = document.getElementById("lesson-chat-reset");
  const chatFeedback = document.getElementById("lesson-chat-feedback");
  const chatAnswer = document.getElementById("lesson-chat-answer");
  const chatStatus = document.getElementById("lesson-chat-status");
  const chatPromptButtons = document.querySelectorAll("[data-chat-prompt]");

  function setFeedback(message) {
    if (progressFeedback) progressFeedback.textContent = message;
  }

  function setChatStatus(message) {
    if (chatStatus) chatStatus.textContent = message;
  }

  function setChatFeedback(message) {
    if (chatFeedback) chatFeedback.textContent = message;
  }

  function syncProgressPanel() {
    if (currentStage) currentStage.textContent = progress.currentStage;
    if (passedStages) passedStages.textContent = JSON.stringify(progress.passedStages);
    if (attempts) attempts.textContent = JSON.stringify(progress.attempts);
    if (lessonCompleted) lessonCompleted.textContent = String(progress.lessonCompleted);

    if (problemCta) {
      problemCta.dataset.problemCtaDisabled = progress.lessonCompleted ? "false" : "true";
      const unlocked = progressApi.setProblemLinkState(problemCta, slug);
      problemCta.textContent = unlocked
        ? "실전 문제로 이동"
        : "lessonCompleted === true 일 때만 활성화";
      if (unlocked) {
        problemCta.classList.add("border-emerald-300/30", "bg-emerald-300/10");
      } else {
        problemCta.classList.remove("border-emerald-300/30", "bg-emerald-300/10");
      }
    }

    if (blankBadge) {
      blankBadge.textContent = progress.passedStages.includes("blank") ? "passed" : "incomplete";
    }

    const parsonsUnlocked = progress.passedStages.includes("blank");
    if (parsonsBadge) {
      parsonsBadge.textContent = progress.lessonCompleted ? "passed" : parsonsUnlocked ? "unlocked" : "locked";
    }
    if (parsonsLockedCopy) {
      parsonsLockedCopy.classList.toggle("hidden", parsonsUnlocked);
    }
    if (lessonSummary) {
      lessonSummary.classList.toggle("hidden", !progress.lessonCompleted);
    }

    if (blankPassButton) {
      blankPassButton.disabled = progress.passedStages.includes("blank");
    }
    if (parsonsPassButton) {
      parsonsPassButton.disabled = !parsonsUnlocked || progress.lessonCompleted;
    }
  }

  function renderBlankForm() {
    if (!blankForm) return;

    blankForm.innerHTML = lesson.blankExercise.blanks
      .map(
        (blank, index) => `
          <label class="block rounded-2xl border border-white/10 bg-stone-950/50 p-4" for="blank-input-${blank.id}">
            <span class="text-sm font-medium text-white">Blank ${index + 1}</span>
            <span class="mt-2 block text-xs text-stone-400">${blank.hint}</span>
            <input
              id="blank-input-${blank.id}"
              name="${blank.id}"
              type="text"
              class="mt-3 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none placeholder:text-stone-500"
              placeholder="정답 줄을 입력하세요"
              autocomplete="off"
            >
          </label>
        `,
      )
      .join("");
  }

  function moveParsonsItem(index, direction) {
    const nextIndex = index + direction;
    if (nextIndex < 0 || nextIndex >= parsonsOrder.length) return;
    const nextOrder = [...parsonsOrder];
    const [lineIndex] = nextOrder.splice(index, 1);
    nextOrder.splice(nextIndex, 0, lineIndex);
    parsonsOrder = nextOrder;
    renderParsonsList();
  }

  function renderParsonsList() {
    if (!parsonsList) return;

    const unlocked = progress.passedStages.includes("blank");
    parsonsList.innerHTML = parsonsOrder
      .map((lineIndex, index) => {
        const line = lessonCore.escapeHtml(lesson.parsonsExercise.lines[lineIndex]);
        const disableUp = !unlocked || index === 0;
        const disableDown = !unlocked || index === parsonsOrder.length - 1;

        return `
          <li class="rounded-2xl border border-white/10 bg-stone-950/60 p-4">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-xs uppercase tracking-[0.2em] text-stone-500">line ${index + 1}</p>
                <pre class="mt-2 whitespace-pre-wrap text-sm text-stone-100"><code>${line}</code></pre>
              </div>
              <div class="flex flex-col gap-2">
                <button type="button" data-parsons-move="${index}" data-direction="-1" class="rounded-full border border-white/10 px-3 py-1 text-xs ${disableUp ? "text-stone-600" : "text-white"}" ${disableUp ? "disabled" : ""}>위로</button>
                <button type="button" data-parsons-move="${index}" data-direction="1" class="rounded-full border border-white/10 px-3 py-1 text-xs ${disableDown ? "text-stone-600" : "text-white"}" ${disableDown ? "disabled" : ""}>아래로</button>
              </div>
            </div>
          </li>
        `;
      })
      .join("");

    parsonsList.querySelectorAll("[data-parsons-move]").forEach((button) => {
      button.addEventListener("click", () => {
        moveParsonsItem(Number(button.dataset.parsonsMove), Number(button.dataset.direction));
      });
    });
  }

  function persistProgress(nextState) {
    progress = progressApi.saveProgress(slug, nextState);
    syncProgressPanel();
    renderParsonsList();
  }

  function collectBlankAnswers() {
    return lesson.blankExercise.blanks.reduce((accumulator, blank) => {
      const input = document.getElementById(`blank-input-${blank.id}`);
      accumulator[blank.id] = input?.value ?? "";
      return accumulator;
    }, {});
  }

  function markBlankPassed() {
    const attempted = progressApi.recordAttempt(progress, "blank");
    persistProgress(progressApi.markStagePassed(attempted, "blank"));
  }

  function markParsonsPassed() {
    const attempted = progressApi.recordAttempt(progress, "parsons");
    persistProgress(progressApi.markStagePassed(attempted, "parsons"));
  }

  if (blankSubmit) {
    blankSubmit.addEventListener("click", () => {
      persistProgress(progressApi.recordAttempt(progress, "blank"));
      const result = lessonCore.gradeBlankExercise(lesson.blankExercise, collectBlankAnswers());
      if (result.passed) {
        persistProgress(progressApi.markStagePassed(progress, "blank"));
        if (blankFeedback) {
          blankFeedback.textContent = "빈칸 단계를 통과했습니다. 이제 파슨스 단계를 진행할 수 있습니다.";
        }
        setFeedback("빈칸 단계 통과 상태를 저장했습니다. 이제 파슨스 단계를 열 수 있습니다.");
        return;
      }

      if (blankFeedback) {
        const failedTargets = result.blanks
          .filter((blank) => !blank.correct)
          .map((blank) => `${blank.id}: ${blank.hint}`)
          .join(" / ");
        blankFeedback.textContent = `다시 확인이 필요한 항목이 있습니다. ${failedTargets}`;
      }
    });
  }

  if (blankReset) {
    blankReset.addEventListener("click", () => {
      lesson.blankExercise.blanks.forEach((blank) => {
        const input = document.getElementById(`blank-input-${blank.id}`);
        if (input) input.value = "";
      });
      if (blankFeedback) blankFeedback.textContent = "입력을 초기화했습니다.";
    });
  }

  if (parsonsSubmit) {
    parsonsSubmit.addEventListener("click", () => {
      if (!progress.passedStages.includes("blank")) {
        if (parsonsFeedback) {
          parsonsFeedback.textContent = "먼저 빈칸 단계를 통과해야 합니다.";
        }
        return;
      }

      persistProgress(progressApi.recordAttempt(progress, "parsons"));
      const result = lessonCore.gradeParsonsExercise(lesson.parsonsExercise, parsonsOrder);
      if (result.passed) {
        persistProgress(progressApi.markStagePassed(progress, "parsons"));
        if (parsonsFeedback) {
          parsonsFeedback.textContent = "파슨스 단계를 통과했습니다. 실전 문제로 이동할 수 있습니다.";
        }
        setFeedback("파슨스 단계 통과 상태를 저장했습니다. 이제 실전 문제로 이동할 수 있습니다.");
        return;
      }

      if (parsonsFeedback) {
        const misplaced = result.misplacedLines.length > 0 ? `잘못된 위치: ${result.misplacedLines.map((index) => index + 1).join(", ")}` : "";
        const groups = result.brokenGroups.length > 0 ? " 조건문 블록이 붙어 있어야 합니다." : "";
        parsonsFeedback.textContent = `줄 순서를 다시 정렬해야 합니다. ${misplaced}${groups}`.trim();
      }
    });
  }

  if (parsonsReset) {
    parsonsReset.addEventListener("click", () => {
      parsonsOrder = lesson.parsonsExercise.lines.map((_line, index) => index);
      renderParsonsList();
      if (parsonsFeedback) parsonsFeedback.textContent = "파슨스 순서를 초기화했습니다.";
    });
  }

  if (blankPassButton) {
    blankPassButton.addEventListener("click", () => {
      markBlankPassed();
      setFeedback("빈칸 단계 통과 상태를 저장했습니다. 이제 파슨스 단계를 열 수 있습니다.");
    });
  }

  if (parsonsPassButton) {
    parsonsPassButton.addEventListener("click", () => {
      if (!progress.passedStages.includes("blank")) {
        setFeedback("파슨스 단계 저장 전에는 빈칸 단계를 먼저 통과해야 합니다.");
        syncProgressPanel();
        return;
      }
      markParsonsPassed();
      setFeedback("파슨스 단계 통과 상태를 저장했습니다. 이제 실전 문제로 이동할 수 있습니다.");
    });
  }

  if (progressResetButton) {
    progressResetButton.addEventListener("click", () => {
      const resetProgress = progressApi.saveProgress(slug, progressApi.defaultProgressState);
      progress = resetProgress;
      syncProgressPanel();
      renderParsonsList();
      setFeedback("진행 상태를 초기화했습니다.");
    });
  }

  function parseSseChunk(chunk) {
    return chunk
      .split("\n\n")
      .map((part) => part.trim())
      .filter(Boolean)
      .map((part) => {
        const lines = part.split("\n");
        const event = lines.find((line) => line.startsWith("event:"))?.slice(6).trim() || "message";
        const data = lines
          .filter((line) => line.startsWith("data:"))
          .map((line) => line.slice(5).trim())
          .join("\n");
        return { event, data };
      });
  }

  async function submitLessonQuestion(question) {
    if (!chatSubmit || !chatAnswer) return;

    chatSubmit.disabled = true;
    chatAnswer.textContent = "";
    setChatStatus("streaming");
    setChatFeedback("질문을 보내는 중입니다.");

    try {
      const response = await fetch("/api/lesson-chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          algorithmSlug: slug,
          question,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({ message: "질문 요청에 실패했습니다." }));
        throw new Error(payload.message || "질문 요청에 실패했습니다.");
      }

      if (!response.body) {
        throw new Error("스트리밍 응답을 사용할 수 없습니다.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const boundary = buffer.lastIndexOf("\n\n");
        if (boundary === -1) continue;

        const complete = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);

        parseSseChunk(complete).forEach(({ event, data }) => {
          if (event === "chunk") {
            const payload = JSON.parse(data);
            chatAnswer.textContent += payload.delta || "";
            setChatFeedback("답변을 생성 중입니다.");
            return;
          }
          if (event === "error") {
            const payload = JSON.parse(data);
            throw new Error(payload.message || "답변 생성에 실패했습니다.");
          }
          if (event === "done") {
            setChatFeedback("답변이 완료되었습니다.");
          }
        });
      }

      if (buffer.trim()) {
        parseSseChunk(buffer).forEach(({ event, data }) => {
          if (event === "chunk") {
            const payload = JSON.parse(data);
            chatAnswer.textContent += payload.delta || "";
          }
        });
      }

      if (!chatAnswer.textContent.trim()) {
        chatAnswer.textContent = "모델이 빈 응답을 반환했습니다.";
      }
      setChatStatus("done");
    } catch (error) {
      const message = error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
      chatAnswer.textContent = message;
      setChatFeedback("질문을 처리하지 못했습니다.");
      setChatStatus("error");
    } finally {
      chatSubmit.disabled = false;
    }
  }

  if (chatSubmit && chatQuestion) {
    chatSubmit.addEventListener("click", async () => {
      const question = chatQuestion.value.trim();
      if (!question) {
        setChatFeedback("질문을 먼저 입력하세요.");
        setChatStatus("idle");
        return;
      }
      await submitLessonQuestion(question);
    });
  }

  if (chatReset && chatQuestion && chatAnswer) {
    chatReset.addEventListener("click", () => {
      chatQuestion.value = "";
      chatAnswer.textContent = "여기에 답변이 표시됩니다.";
      setChatFeedback("질문과 답변을 초기화했습니다.");
      setChatStatus("idle");
    });
  }

  chatPromptButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (!chatQuestion) return;
      chatQuestion.value = button.dataset.chatPrompt || "";
      chatQuestion.focus();
    });
  });

  progressApi.setLastAlgorithm(slug);
  renderBlankForm();
  syncProgressPanel();
  renderParsonsList();
  setChatStatus("idle");
});
