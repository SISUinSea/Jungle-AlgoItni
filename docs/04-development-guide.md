# 04. Development Guide

## 1) 브랜치 전략

- `main`에 직접 push 하지 않는다
- 브랜치 이름은 `codex/` 접두사를 사용한다
- 한 브랜치는 하나의 결과물만 다룬다
- 문서 계약 변경과 구현 변경이 함께 움직여야 하면 같은 브랜치에서 처리한다

권장 브랜치 예시:

- `codex/docs-mvp-scope`
- `codex/feature-concept-page`
- `codex/feature-lesson-flow`
- `codex/feature-counterexample-api`
- `codex/fix-grader-normalize`

## 2) 커밋 규칙

- 기본 형식: `<type>: <subject>`
- 권장 타입: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`
- 문서 계약을 고정하는 커밋과 기능 구현 커밋은 가능한 한 분리한다

## 3) PR 규칙

- 변경 목적, 검증 결과, 문서 반영 여부를 적는다
- UI가 바뀌면 화면 설명 또는 스크린샷을 첨부한다
- API, `lesson.json` 스키마, `localStorage` 키가 바뀌면 `docs/01~03`를 같은 PR에서 갱신한다
- 기존 다중 예제 구조와 관련된 `example_id`, `whiteboardExercise` 같은 폐기 용어를 다시 도입한 PR은 merge하지 않는다

## 4) 구현 순서

1. Flask 기본 앱, 템플릿, 정적 자산 구조를 만든다
2. `content/algorithms/<slug>/concept.json`, `lesson.json`, `problem.json` 계약을 고정한다
3. 홈, 개념, 레슨, 실전 문제 라우트와 Jinja 템플릿을 구현한다
4. `lesson.js`에서 `빈칸 -> 파슨스` client-side deterministic 채점을 구현한다
5. `progress.js`로 `localStorage` 진행 상태 저장과 해금 규칙을 연결한다
6. LLM 보조 API와 counterexample 파이프라인을 Flask 서비스로 구현한다
7. 수동 스모크 테스트와 문서 정합성을 검토한 뒤 배포 준비를 한다

## 5) 좋은 작업 요청 예시

- `docs/01~03을 읽고 대표 구현 레슨 흐름만 구현해줘.`
- `lesson.json 계약을 먼저 고정하고 concept/lesson 라우트를 만들어줘.`
- `counterexample API만 구현하고 관련 문서를 같이 맞춰줘.`

피해야 할 요청 예시:

- `서비스 전체를 한 번에 다 만들어줘`
- `문서 무시하고 알아서 맞춰줘`
- `백지 코딩까지 같이 넣어줘`

## 6) 검증 원칙

- 브랜치 범위에 맞는 검증만 수행한다
- deterministic 채점 규칙은 자동 검증 우선, LLM 응답 품질은 수동 검증 우선으로 나눈다
- README와 numbered docs의 정합성을 PR 전에 다시 확인한다
- 실전 문제 파트는 `found:false`를 정답 판정처럼 기록하지 않는다

## 7) 최소 체크리스트

- [ ] 대표 구현 1개 중심 구조가 유지된다
- [ ] `빈칸 -> 파슨스` 해금 규칙이 작동한다
- [ ] LLM이 정답 판정에 사용되지 않는다
- [ ] 문서와 구현 방향이 맞는다
- [ ] 필요한 검증 명령과 수동 스모크 테스트를 기록했다
