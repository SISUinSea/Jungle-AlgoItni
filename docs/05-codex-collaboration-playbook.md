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
Implement only the requested branch scope, run the relevant checks, and finish with a PR-ready summary.
```

## 3) 공통 작업 원칙

- 한 작업 단위는 한 결과만 책임진다
- 담당 범위를 벗어난 파일은 필요할 때만 수정한다
- 계약이나 문서 구조가 바뀌면 관련 docs를 같은 작업에서 업데이트한다
- 충돌이 나면 기능 확장보다 정합성 회복을 먼저 한다
- LLM 관련 변경은 보조 기능인지, 정답 판정 경계를 넘는지 먼저 확인한다

## 4) 현재 운영 방식

- 현재 저장소는 솔로 개발 기준으로 운영한다
- 브랜치는 기능 단위로만 나누고 과도한 phase/track 체계는 만들지 않는다
- 병렬 작업이 필요하면 계약 고정 작업을 먼저 끝낸 뒤 하위 작업을 시작한다

## 5) 병렬 작업 규칙

- `lesson.json` 스키마, API request/response shape, `localStorage` 키는 먼저 owner 브랜치가 고정한다
- downstream 브랜치는 최종 계약을 추측해서 새 필드를 만들지 않는다
- `빈칸 -> 파슨스` 순서와 대표 구현 1개 규칙은 하위 브랜치가 바꾸지 않는다
- merge-ready 전에 README와 docs가 여전히 같은 용어를 쓰는지 확인한다

## 6) handoff 기록

각 작업 종료 시 아래를 남긴다.

- 완료한 범위
- 고정한 계약
- 남은 의존성
- 사람 확인이 필요한 항목
