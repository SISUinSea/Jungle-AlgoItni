# 03. API Reference

이 문서는 현재 MVP의 구현 경계를 고정하기 위한 계약 문서다.

## 0) 문서 모드

- 선택: `Backend API Reference`
- 선택 이유: 레슨 채점과 진행 상태는 client-side로 끝나고, 서버가 맡는 기능은 반례 생성 파이프라인 하나로 축소되었다

## 1) 공통 규칙

- 키 네이밍: `camelCase`
- 시간 포맷: 필요 시 `ISO-8601`
- 인증 방식: 없음
- 저장 경계: 콘텐츠는 repo JSON, 진행 상태는 브라우저 `localStorage`, API 요청 상태는 서버 메모리/샌드박스
- 후보 생성 보조 경계: 반례 파이프라인에서만 필요 시 사용하며, 채점이나 pass/fail 결정에는 사용하지 않는다

## 2A. 엔드포인트 목록

| Method | Endpoint | Auth | 설명 |
| --- | --- | --- | --- |
| `POST` | `/api/counterexample` | No | 실전 문제용 반례 탐색 파이프라인 실행 |

## 3A. 핵심 API 상세

#### `POST /api/counterexample`

Request:

```json
{
  "problemSource": "baekjoon",
  "problemIdOrUrl": "https://www.acmicpc.net/problem/1920",
  "userCode": "n = int(input())\n..."
}
```

Success:

```json
{
  "found": true,
  "counterexampleInput": "5\n1 2 3 4 5\n4\n1 2 6 7\n",
  "userOutput": "1 1 1 0",
  "expectedOutput": "1 1 0 0"
}
```

Failure:

```json
{
  "found": false,
  "message": "현재 탐색 범위에서는 반례를 찾지 못했습니다."
}
```

Foundation placeholder:

```json
{
  "message": "Counterexample pipeline is not implemented in codex/foundation-contracts."
}
```

상태 코드 규칙:

- `400`: `problemSource`, `problemIdOrUrl`, `userCode` 중 필수 필드 누락
- `404`: 문서에 등록되지 않은 `problemIdOrUrl`
- `501`: foundation 브랜치에서 경로와 입력 검증만 고정한 상태

## 4) 브라우저 저장 계약

| Key / Store | Shape | Source of Truth | 설명 |
| --- | --- | --- | --- |
| `algostep_progress::<algorithmSlug>` | `{ currentStage, passedStages, attempts: { blank, parsons }, lessonCompleted }` | `localStorage` | 알고리즘별 현재 학습 상태 |
| `algostep_last_algorithm` | `string` | `localStorage` | 마지막으로 본 알고리즘 slug |

| 출발 화면 | 도착 화면 | 전달 데이터 | 필요 조건 |
| --- | --- | --- | --- |
| `/` | `/algorithms/<slug>` | `algorithmSlug` | 선택한 알고리즘이 존재해야 한다 |
| `/algorithms/<slug>` | `/algorithms/<slug>/lesson` | `algorithmSlug` | 개념 페이지 진입 성공 |
| `/algorithms/<slug>/lesson` | `/algorithms/<slug>/problem` | `lessonCompleted` | `blank`, `parsons` 단계 통과 |

## 5) 검증 규칙

- `/api/counterexample`은 known edge case, reference solver, brute force를 우선하고 후보 입력 생성 보조는 선택적으로만 사용한다
- `found:false`는 반례 미발견을 의미하며 정답 보장을 의미하지 않는다
- 사용자 코드 실행은 샌드박스에서만 수행하고 시간 제한 초과, 런타임 에러, 잘못된 입력 형식을 명시적으로 구분한다
