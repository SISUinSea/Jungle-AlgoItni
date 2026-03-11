# 05. Codex Collaboration Playbook

## 1) 문서 우선순위

작업 전에는 아래 순서로 확인한다.

1. `README.md`
2. `docs/01-product-planning.md`
3. `docs/02-architecture.md`
4. `docs/03-api-reference.md`
5. `docs/04-development-guide.md`
6. `docs/06-testing-playbook.md`

실제 source of truth 우선순위는 `docs/01 -> docs/02 -> docs/03 -> docs/04 -> docs/05 -> docs/06 -> README`다.

## 2) 공통 시작 프롬프트

```text
Read README.md and docs/01 through docs/06.
Summarize the fixed MVP scope, especially the one-representative-python-lesson rule.
Do not reintroduce old multi-example or whiteboard-coding scope without updating docs/01~03 first.
Do not add hint, reexplain, or wrong-answer-analysis features.
Implement only the requested branch scope, run the relevant checks, and finish with a PR-ready summary.
```

## 3) 공통 작업 원칙

- 한 작업 단위는 한 결과만 책임진다
- 담당 범위를 벗어난 파일은 필요할 때만 수정한다
- 계약이나 문서 구조가 바뀌면 관련 docs를 같은 작업에서 업데이트한다
- 충돌이 나면 기능 확장보다 정합성 회복을 먼저 한다
- 반례 파이프라인 외의 서버 기능은 임의로 추가하지 않는다

## 4) 현재 운영 방식

- 현재 저장소는 3인 워크숍 기준으로 운영한다
- 공통 계약 브랜치와 기능 브랜치를 분리한다
- foundation owner가 계약을 먼저 고정한 뒤 두 기능 브랜치가 병렬로 붙는다

## 5) 병렬 작업 규칙

- 1번 owner
  담당 브랜치: `codex/foundation-contracts`
  책임: `app.py`, `templates/base.html`, `content` 스키마, `localStorage` 키, `docs/02`, `docs/03`
- 2번 owner
  담당 브랜치: `codex/feature-lesson-flow`
  책임: 홈/개념/레슨 화면, `lesson.js`, `progress.js`, deterministic grader
- 3번 owner
  담당 브랜치: `codex/feature-problem-counterexample`
  책임: 실전 문제 화면, `/api/counterexample`, sandbox, validator, known case
- `lesson.json` 스키마, API request/response shape, `localStorage` 키는 1번 owner가 먼저 고정한다
- 2번과 3번은 `app.py`, `base.html`, 공통 JSON 스키마를 임의로 확장하지 않는다
- `빈칸 -> 파슨스` 순서와 대표 구현 1개 규칙은 하위 브랜치가 바꾸지 않는다
- merge 순서는 `foundation -> lesson-flow -> problem-counterexample`으로 고정한다
- merge-ready 전에 README와 docs가 여전히 같은 용어를 쓰는지 확인한다

## 6) handoff 기록

각 작업 종료 시 아래를 남긴다.

- 완료한 범위
- 고정한 계약
- 남은 의존성
- 사람 확인이 필요한 항목
