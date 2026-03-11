# 06. Testing Playbook

현재 저장소에는 자동 테스트 코드가 아직 없다. 이 문서는 구현이 시작된 뒤 merge 안전선을 어떻게 세울지 정의한다.

## 1) 테스트 계층

1. 문서 정합성 검토
2. 브랜치 범위 자동 테스트
3. 브랜치 범위 수동 스모크 테스트
4. 통합 수동 테스트

## 2) 테스트 생성 원칙

- 한 브랜치는 자기 책임 범위의 테스트만 추가한다
- 핵심 비즈니스 규칙은 deterministic 입출력 검증으로 우선 고정한다
- 레슨 채점, 진행 상태 저장, counterexample 판별은 스냅샷보다 행동 검증을 우선한다
- 자동화가 아직 없는 영역은 수동 체크리스트로 남긴다
- 브라우저 자동화는 MVP 기본 전제로 두지 않는다

## 3) 브랜치별 테스트 책임

### Contract / Data Branch

- `concept.json`, `lesson.json`, `problem.json` 스키마 검증
- 알고리즘당 `lesson.json`이 1개인지 검증
- `localStorage` 키와 API request/response shape 검증

### Feature Branch

- `빈칸` normalize 비교와 허용 답안 비교 검증
- `파슨스` `answerOrder`, `groupedIndices` 검증
- 단계 해금과 `localStorage` 저장 동작 검증
- LLM 보조 API가 합격 판정을 반환하지 않는지 검증

### Counterexample Branch

- known case 우선 탐색 검증
- reference solver / validator 비교 검증
- `found:false`가 정답 보장으로 취급되지 않는 응답 처리 검증
- 샌드박스 시간 초과, 런타임 에러, 잘못된 출력 형식 처리 검증

## 4) 수동 스모크 테스트

- 홈에서 알고리즘 목록과 마지막 학습 위치가 보인다
- 개념 설명 화면에 복잡도, 시각화, 대표 실수가 노출된다
- 레슨 화면에서 `빈칸` 오답 시 틀린 위치와 힌트 버튼이 보인다
- `빈칸` 통과 후에만 `파슨스` 단계가 열린다
- `파슨스` 단계는 위/아래 이동 버튼 기준으로 조작 가능하다
- 레슨 완료 후 실전 문제 화면으로 이동할 수 있다
- 반례 생성 결과가 `counterexampleInput`, `userOutput`, `expectedOutput`을 함께 보여준다

## 5) 사람이 확인해야 하는 것

- 데스크톱/모바일 레이아웃 품질
- Tailwind 기반 간격, 타이포그래피, 버튼 상태의 일관성
- 포커스 이동과 키보드 접근성
- 힌트, 재설명, 오답 분석 문구가 과도하게 정답을 직접 노출하지 않는지
- counterexample 실패 메시지가 정답 보장처럼 읽히지 않는지

## 6) PR 기록 원칙

- 자동 검증 완료 범위
- 수동 확인 완료 범위
- 아직 사람 확인이 필요한 범위
- 문서만 바뀐 PR이라면 어떤 상위 문서를 source of truth로 삼았는지
