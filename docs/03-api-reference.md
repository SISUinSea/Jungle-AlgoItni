# 03. API Reference

이 문서는 현재 MVP의 구현 경계를 고정하기 위한 계약 문서다.

## 0) 문서 모드

- 선택: `Backend API Reference`
- 선택 이유: 레슨 채점은 client-side로 끝나지만, 힌트/재설명/오답 분석/반례 생성은 실제 Flask API 계약이 필요하다

## 1) 공통 규칙

- 키 네이밍: `camelCase`
- 시간 포맷: 필요 시 `ISO-8601`
- 인증 방식: 없음
- 저장 경계: 콘텐츠는 repo JSON, 진행 상태는 브라우저 `localStorage`, API 요청 상태는 서버 메모리/샌드박스
- LLM 사용 경계: 서버 API는 힌트, 재설명, 오답 분석, 반례 후보 생성 보조에만 사용한다

## 2A. 엔드포인트 목록

| Method | Endpoint | Auth | 설명 |
| --- | --- | --- | --- |
| `POST` | `/api/hint` | No | 현재 단계에 맞는 힌트 응답 |
| `POST` | `/api/reexplain` | No | 개념 또는 레슨을 더 쉬운 말로 재설명 |
| `POST` | `/api/analyze-wrong-answer` | No | deterministic 실패 원인을 한 줄 요약으로 보조 설명 |
| `POST` | `/api/counterexample` | No | 실전 문제용 반례 탐색 파이프라인 실행 |

## 3A. 핵심 API 상세

#### `POST /api/hint`

Request:

```json
{
  "algorithmSlug": "binary-search",
  "stage": "blank",
  "hintLevel": 1,
  "userAnswer": {
    "b1": "mid = left + right // 2"
  }
}
```

Success:

```json
{
  "hint": "중간 인덱스를 계산하는 줄을 다시 보세요.",
  "source": "static_or_llm"
}
```

#### `POST /api/reexplain`

Request:

```json
{
  "algorithmSlug": "binary-search",
  "context": "concept",
  "userQuestion": "left와 right를 왜 이렇게 움직이는지 쉽게 설명해줘"
}
```

Success:

```json
{
  "explanation": "탐색 범위를 절반씩 줄이기 위해 target이 있는 쪽만 남기는 방식입니다."
}
```

#### `POST /api/analyze-wrong-answer`

Request:

```json
{
  "algorithmSlug": "binary-search",
  "stage": "parsons",
  "userAnswer": [2, 0, 1, 3, 4],
  "failureReason": "wrongOrder",
  "graderFeedback": "범위 이동보다 mid 계산이 먼저 와야 합니다."
}
```

Success:

```json
{
  "summary": "탐색 범위를 줄이기 전에 현재 중간값을 먼저 계산해야 흐름이 유지됩니다."
}
```

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

## 4) 브라우저 저장 계약

| Key / Store | Shape | Source of Truth | 설명 |
| --- | --- | --- | --- |
| `algostep_progress::<algorithmSlug>` | `{ currentStage, passedStages, attempts, hintsUsed, lessonCompleted }` | `localStorage` | 알고리즘별 현재 학습 상태 |
| `algostep_last_algorithm` | `string` | `localStorage` | 마지막으로 본 알고리즘 slug |

| 출발 화면 | 도착 화면 | 전달 데이터 | 필요 조건 |
| --- | --- | --- | --- |
| `/` | `/algorithms/<slug>` | `algorithmSlug` | 선택한 알고리즘이 존재해야 한다 |
| `/algorithms/<slug>` | `/algorithms/<slug>/lesson` | `algorithmSlug` | 개념 페이지 진입 성공 |
| `/algorithms/<slug>/lesson` | `/algorithms/<slug>/problem` | `lessonCompleted` | `blank`, `parsons` 단계 통과 |

## 5) 검증 규칙

- `hintLevel`은 `1`, `2`, `3`만 허용한다
- `stage`는 `blank` 또는 `parsons`만 허용하며, 문제 풀이 단계는 `/api/hint` 대상이 아니다
- `/api/hint`, `/api/reexplain`, `/api/analyze-wrong-answer`는 pass/fail 값을 반환하지 않는다
- `/api/counterexample`은 known edge case, reference solver, brute force를 우선하고 LLM은 후보 입력 생성 보조로만 사용한다
- `found:false`는 반례 미발견을 의미하며 정답 보장을 의미하지 않는다
- 사용자 코드 실행은 샌드박스에서만 수행하고 시간 제한 초과, 런타임 에러, 잘못된 입력 형식을 명시적으로 구분한다
