# algoitni

`algoitni`는 알고리즘 입문자가 대표 파이썬 구현 1개를 기준으로 개념 학습, 단계형 연습, 실전 문제 반례 확인까지 이어서 수행할 수 있게 돕는 학습 웹 MVP입니다.

## 프로젝트 소개

- 프로젝트 한 줄 소개: 알고리즘마다 대표 파이썬 구현 1개를 중심으로 학습 흐름을 고정한 3인 병렬 개발용 docs-first 워크숍 MVP
- 해결하려는 문제: 개념 설명 뒤에 바로 실전 문제로 넘어가면 구현 순서와 상태 변화를 이해하지 못한 채 막히기 쉽다
- 핵심 사용자: 알고리즘 입문자, 구현 순서를 자주 놓치는 학습자, 오답 원인을 반례로 확인하고 싶은 사용자
- 핵심 가치: 작은 학습 단위를 deterministic하게 통과시키고 실전 오답을 이해 가능한 반례로 연결한다
- 진행 맥락: 데모 우선이지만 mock-first는 아니며, 정적 콘텐츠와 실제 Flask API를 함께 쓰는 lightweight real-backend MVP

## 기획 포인트

- 지금 풀려는 문제: 기존 다중 예제 묶음 대신 알고리즘별 대표 파이썬 구현 1개로 학습 구조를 단순화한다
- 이번 범위에서 집중할 가치: `빈칸 -> 파슨스` 2단계 학습과 반례 기반 오답 진단을 끊김 없이 연결한다
- 이번 단계에서 의도적으로 제외하는 것: 백지 코딩, 로그인/동기화, 힌트/재설명/오답 분석, LLM 기반 정답 판정

## 핵심 기능

- 알고리즘 개념 설명, 복잡도, 대표 실수, 시각화 자료 제공
- 알고리즘별 대표 파이썬 구현 레슨 1개와 `빈칸 -> 파슨스` 단계형 연습
- `localStorage` 기반 학습 진행 상태 저장
- 실전 문제 풀이 UI와 counterexample 파이프라인

## 데모 또는 핵심 사용 시나리오

1. 사용자가 알고리즘을 선택하고 개념 설명을 읽는다.
2. 대표 파이썬 구현 레슨에서 `빈칸` 단계를 통과한다.
3. 해금된 `파슨스` 단계를 통과하고 핵심 규칙 요약을 본다.
4. 실전 문제에서 코드를 제출하고 필요하면 반례 생성으로 오답 원인을 확인한다.

## 주요 화면 / 결과물

- 홈 화면: 알고리즘 목록과 마지막 학습 위치 진입점 제공
- 개념 설명 화면: 개념, 복잡도, 시각화, 대표 실수 제공
- 레슨 화면: 대표 구현 코드, `빈칸 -> 파슨스` 인터랙션, 진행 상태 제공
- 실전 문제 화면: 문제 설명, 코드 입력, 제출 결과, 반례 결과 제공

## 아키텍처 요약

- 클라이언트: Flask + Jinja로 렌더링된 HTML에 바닐라 JavaScript와 Tailwind CSS를 결합한다
- 서버: Python Flask가 정적 콘텐츠 로딩과 counterexample 파이프라인을 담당한다
- 데이터 저장소: repo 내 JSON 콘텐츠와 브라우저 `localStorage`를 사용하고 별도 DB는 두지 않는다
- 인증 / 상태 관리: 인증 없음, 학습 진행 상태는 클라이언트 저장
- 배포 방식: 단일 Flask 서버가 템플릿, 정적 자산, API를 함께 제공한다

## 기술 스택

| 영역 | 사용 기술 |
| --- | --- |
| Frontend | `HTML`, `CSS`, `JavaScript`, `Tailwind CSS`, `Jinja` |
| Backend | `Python Flask` |
| Database | 없음 |
| Infra | 단일 Flask 배포, 정적 자산 서빙 |
| Testing | deterministic 채점 규칙 검증 + 수동 스모크 테스트 |

## Quick Start

현재 저장소에는 foundation/contracts 스캐폴드가 포함되어 있다. 레슨 채점과 counterexample 파이프라인은 후속 브랜치에서 구현한다.

### 1) 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app.py run --debug
```

### 2) 검증

```bash
python3 -m pytest
```

## 프로젝트 문서

- [기획 문서](docs/01-product-planning.md)
- [아키텍처 문서](docs/02-architecture.md)
- [API / 인터페이스 문서](docs/03-api-reference.md)
- [개발 가이드](docs/04-development-guide.md)
- [협업 플레이북](docs/05-codex-collaboration-playbook.md)
- [테스트 플레이북](docs/06-testing-playbook.md)

## Known Limitations

- 현재 저장소는 공통 계약 스캐폴드까지만 구현되어 있으며 레슨 채점과 counterexample 실행은 아직 없다
- 알고리즘별 콘텐츠 수와 문제 세트는 초기 구현 브랜치에서 확정된다
- 샌드박스 제한, validator 세부 구현, 반례 후보 확장 전략은 후속 기술 설계에서 고정한다
