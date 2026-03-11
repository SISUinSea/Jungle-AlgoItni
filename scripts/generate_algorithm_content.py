from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS_DIR = REPO_ROOT / "content" / "algorithms"
TEMPLATE_ROOT = Path("/Users/wiseungcheol/Downloads/SW-AI-W02-05-TEMPLATE-main")
STARTER_CODE = 'def solve():\n    pass\n\n\nif __name__ == "__main__":\n    solve()'


def block(text: str) -> str:
    return dedent(text).strip("\n")


def step(label: str, explanation: str) -> dict:
    return {"label": label, "explanation": explanation}


def blank(blank_id: str, answer: str, hint: str, accepted_answers: list[str] | None = None) -> dict:
    compact = re.sub(r"\s+", "", answer)
    answers = accepted_answers if accepted_answers is not None else ([compact] if compact != answer else [])
    return {"id": blank_id, "answer": answer, "acceptedAnswers": answers, "hint": hint}


def build_blank_exercise(prompt: str, source: str, blanks: list[dict]) -> dict:
    lines = block(source).splitlines()
    template_lines = list(lines)

    for item in blanks:
      answer = item["answer"]
      for index, line in enumerate(template_lines):
          if line.strip() == answer:
              indent = line[: len(line) - len(line.lstrip(" "))]
              template_lines[index] = f"{indent}__BLANK_{item['id']}__"
              break
      else:
          raise ValueError(f"Could not find blank answer line: {answer}")

    return {
        "prompt": prompt,
        "template": "\n".join(template_lines),
        "blanks": blanks,
    }


def build_parsons_exercise(prompt: str, source: str, include_signature: bool = False) -> dict:
    lines = [line.rstrip() for line in block(source).splitlines() if line.strip()]
    if not include_signature and lines and lines[0].lstrip().startswith(("def ", "class ")):
        lines = lines[1:]
    return {
        "prompt": prompt,
        "lines": lines,
        "answerOrder": list(range(len(lines))),
        "groupedIndices": [],
    }


def build_concept(entry: dict) -> dict:
    return {
        "meta": {
            "slug": entry["slug"],
            "title": entry["title"],
            "aliases": entry["aliases"],
            "difficulty": "basic",
            "tags": entry["tags"],
            "summary": entry["summary"],
        },
        "overview": entry["overview"],
        "coreIdea": entry["coreIdea"],
        "complexity": {
            "time": entry["complexityTime"],
            "space": entry["complexitySpace"],
        },
        "commonMistake": {
            "title": entry["commonMistake"]["title"],
            "whyWrong": entry["commonMistake"]["whyWrong"],
        },
        "visualNotes": [
            f"{entry['visualFocus']}이 어떻게 바뀌는지 단계별로 표시한다.",
            f"대표 구현에서 {entry['visualFocus']}을 갱신하는 시점을 강조한다.",
        ],
    }


def build_lesson(entry: dict) -> dict:
    return {
        "algorithmSlug": entry["slug"],
        "title": entry["lessonTitle"],
        "objective": entry["objective"],
        "codeLanguage": "python",
        "inputExample": entry["inputExample"],
        "outputExample": entry["outputExample"],
        "representativeCode": entry["representativeCode"],
        "traceSteps": entry["traceSteps"],
        "blankExercise": build_blank_exercise(
            entry["blankPrompt"],
            entry["blankSource"],
            entry["blankSpecs"],
        ),
        "parsonsExercise": build_parsons_exercise(
            entry["parsonsPrompt"],
            entry["parsonsSource"],
            entry.get("parsonsIncludeSignature", False),
        ),
        "commonMistake": entry["commonMistake"],
        "bridgeSummary": entry["bridgeSummary"],
    }


def build_problem(entry: dict) -> dict:
    return {
        "algorithmSlug": entry["slug"],
        "problemSource": "internal-demo",
        "problemIdOrUrl": f"{entry['slug']}-demo-problem",
        "title": entry["problemTitle"],
        "description": entry["problemDescription"],
        "inputFormat": entry["inputFormat"],
        "outputFormat": entry["outputFormat"],
        "starterCode": STARTER_CODE,
        "knownEdgeCases": entry["knownEdgeCases"],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip("\n")


def validate_entry(entry: dict) -> None:
    source = entry["templatePath"].read_text(encoding="utf-8")
    marker = "# 테스트 케이스"
    if marker not in source:
        raise ValueError(f"Missing test marker in {entry['templatePath']}")

    harness = source.split(marker, 1)[1]
    validation_source = f"{entry['representativeCode']}\n\n{marker}{harness}"
    output_path = entry["templatePath"].with_name(f"{entry['templatePath'].stem}_output.txt")
    expected = output_path.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "validate_module.py"
        temp_path.write_text(validation_source, encoding="utf-8")
        result = subprocess.run(
            ["python3", str(temp_path)],
            capture_output=True,
            text=True,
            check=False,
        )

    if result.returncode != 0:
        raise RuntimeError(
            f"Validation failed for {entry['slug']}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    if normalize_newlines(result.stdout) != normalize_newlines(expected):
        raise AssertionError(
            f"Output mismatch for {entry['slug']}.\nExpected:\n{expected}\nActual:\n{result.stdout}"
        )


def make_entry(**kwargs) -> dict:
    kwargs["templatePath"] = TEMPLATE_ROOT / kwargs["templateRel"]
    return kwargs


ALGORITHMS = [
    make_entry(
        slug="python-basics",
        templateRel="week2/basic/01_python_dict.py",
        title="파이썬 문법",
        aliases=["python basics", "list", "dict"],
        tags=["python", "list", "dict"],
        summary="리스트와 딕셔너리를 조합해 데이터를 모으고 다시 조건에 맞는 항목만 추리는 기본 패턴",
        overview="파이썬 문법 단원에서는 리스트와 딕셔너리에서 필요한 값을 꺼내고, 계산한 기준으로 다시 필터링하는 흐름을 익힌다.",
        coreIdea="점수 목록을 먼저 만들고 평균을 계산한 뒤, 같은 원본 데이터에서 평균 이상 학생의 이름만 다시 추출한다.",
        complexityTime="O(n)",
        complexitySpace="O(n)",
        visualFocus="점수 목록과 평균 기준",
        lessonTitle="리스트와 딕셔너리로 평균 이상 학생 찾기",
        objective="데이터 추출 -> 평균 계산 -> 조건 필터링 순서를 한 번에 연결해 구현한다.",
        inputExample='students = [\n    {"name": "Alice", "score": 85},\n    {"name": "Bob", "score": 92},\n    {"name": "Charlie", "score": 78},\n    {"name": "David", "score": 95},\n]',
        outputExample="평균 점수: 87.5\n평균 이상 학생: ['Bob', 'David']",
        representativeCode=block(
            """
            def find_above_average_students(students):
                scores = [student["score"] for student in students]
                average = sum(scores) / len(scores)
                above_average_students = [
                    student["name"] for student in students if student["score"] >= average
                ]
                return average, above_average_students
            """
        ),
        traceSteps=[
            step("점수 추출", "딕셔너리 리스트에서 score 값만 따로 모아 평균 계산 준비를 끝낸다."),
            step("기준 계산", "sum(scores) / len(scores)로 비교 기준이 될 평균을 만든다."),
            step("조건 필터링", "원본 학생 목록을 다시 보면서 평균 이상인 이름만 순서대로 추린다."),
        ],
        blankPrompt="평균 계산 전에 어떤 데이터를 만들고, 어떤 기준으로 이름을 걸러내는지 회상한다.",
        blankSource=block(
            """
            scores = [student["score"] for student in students]
            average = sum(scores) / len(scores)
            above_average_students = [
                student["name"] for student in students if student["score"] >= average
            ]
            return average, above_average_students
            """
        ),
        blankSpecs=[
            blank("b1", 'scores = [student["score"] for student in students]', "점수만 추출하는 리스트 컴프리헨션이다."),
            blank("b2", "average = sum(scores) / len(scores)", "비교 기준이 되는 평균을 계산한다."),
            blank("b3", 'student["name"] for student in students if student["score"] >= average', "평균 이상 학생 이름을 추출하는 핵심 조건식이다."),
        ],
        parsonsPrompt="추출 -> 계산 -> 필터링 순서가 끊기지 않게 코드 흐름을 재배치한다.",
        parsonsSource=block(
            """
            def find_above_average_students(students):
                scores = [student["score"] for student in students]
                average = sum(scores) / len(scores)
                above_average_students = [
                    student["name"] for student in students if student["score"] >= average
                ]
                return average, above_average_students
            """
        ),
        commonMistake={
            "title": "평균을 만들기 전에 이름 필터링부터 시도하는 실수",
            "whyWrong": "평균 값이 준비되지 않으면 어떤 학생이 기준 이상인지 비교할 수 없다.",
        },
        bridgeSummary="실전 문제에서도 원본 데이터를 한 번 훑어 기준값을 만들고, 두 번째 단계에서 그 기준으로 필터링하면 구현이 단순해진다.",
        problemTitle="평균 이상 학생 명단 만들기",
        problemDescription="학생 이름과 점수가 담긴 목록이 주어질 때 평균 점수와 평균 이상 학생 이름 목록을 구한다.",
        inputFormat="학생 정보를 담은 딕셔너리 리스트가 함수 인자로 주어진다.",
        outputFormat="평균 점수와 평균 이상 학생 이름 리스트를 반환한다.",
        knownEdgeCases=["학생이 1명인 경우", "모든 학생 점수가 같은 경우", "소수 평균이 나오는 경우"],
    ),
    make_entry(
        slug="array",
        templateRel="week2/basic/02_array.py",
        title="배열",
        aliases=["array", "matrix rotation"],
        tags=["array", "matrix", "index"],
        summary="2차원 배열의 인덱스가 회전 후 어디로 이동하는지 좌표 규칙으로 추적하는 단원",
        overview="배열 단원에서는 행과 열 인덱스를 변환해 새로운 위치에 값을 배치하는 사고방식을 익힌다.",
        coreIdea="원본 배열의 (i, j) 값을 회전 후 (j, n - 1 - i) 위치에 정확히 복사하면 90도 회전이 완성된다.",
        complexityTime="O(n^2)",
        complexitySpace="O(n^2)",
        visualFocus="원본 좌표와 회전 후 좌표",
        lessonTitle="2차원 배열 90도 회전 구현하기",
        objective="원본 좌표를 회전 좌표로 바꾸는 인덱스 규칙을 그대로 코드에 옮긴다.",
        inputExample="matrix = [\n    [1, 2, 3],\n    [4, 5, 6],\n    [7, 8, 9],\n]",
        outputExample="[7, 4, 1]\n[8, 5, 2]\n[9, 6, 3]",
        representativeCode=block(
            """
            def rotate_matrix_90(matrix):
                n = len(matrix)
                rotated = [[0] * n for _ in range(n)]

                for i in range(n):
                    for j in range(n):
                        rotated[j][n - 1 - i] = matrix[i][j]

                return rotated


            def print_matrix(matrix):
                for row in matrix:
                    print(row)
            """
        ),
        traceSteps=[
            step("빈 배열 준비", "원본과 같은 크기의 새 배열을 0으로 채워 회전 결과를 담을 공간을 만든다."),
            step("원본 순회", "모든 (i, j) 위치를 한 번씩 방문해 각 값이 어디로 이동할지 계산한다."),
            step("회전 배치", "회전 규칙에 맞는 새 좌표에 값을 기록하고 완성된 배열을 반환한다."),
        ],
        blankPrompt="좌표 변환 규칙이 정확해야 회전 결과가 뒤집히지 않는다.",
        blankSource=block(
            """
            n = len(matrix)
            rotated = [[0] * n for _ in range(n)]

            for i in range(n):
                for j in range(n):
                    rotated[j][n - 1 - i] = matrix[i][j]

            return rotated
            """
        ),
        blankSpecs=[
            blank("b1", "rotated = [[0] * n for _ in range(n)]", "회전 결과를 담을 새 배열을 만든다."),
            blank("b2", "for i in range(n):", "원본 배열의 행을 순회한다."),
            blank("b3", "rotated[j][n - 1 - i] = matrix[i][j]", "회전 후 좌표에 값을 배치하는 핵심 줄이다."),
        ],
        parsonsPrompt="배열 크기 준비 -> 이중 반복 -> 회전 배치 흐름을 올바르게 복원한다.",
        parsonsSource=block(
            """
            def rotate_matrix_90(matrix):
                n = len(matrix)
                rotated = [[0] * n for _ in range(n)]
                for i in range(n):
                    for j in range(n):
                        rotated[j][n - 1 - i] = matrix[i][j]
                return rotated
            """
        ),
        commonMistake={
            "title": "행과 열 인덱스를 바꾼 뒤 마지막 보정을 빼먹는 실수",
            "whyWrong": "n - 1 - i를 쓰지 않으면 단순 전치 행렬이 되거나 반대 방향으로 회전한다.",
        },
        bridgeSummary="배열 문제에서는 값 자체보다 인덱스가 어디로 이동하는지 먼저 적어 보면 구현 실수가 크게 줄어든다.",
        problemTitle="정사각 행렬 시계 방향 회전",
        problemDescription="N x N 행렬이 주어질 때 모든 원소를 시계 방향으로 90도 회전한 새 행렬을 만든다.",
        inputFormat="정사각 2차원 리스트가 함수 인자로 주어진다.",
        outputFormat="회전된 2차원 리스트를 반환한다.",
        knownEdgeCases=["1 x 1 행렬", "음수가 포함된 행렬", "이미 대칭인 행렬"],
    ),
    make_entry(
        slug="string",
        templateRel="week2/basic/03_string.py",
        title="문자열",
        aliases=["string", "palindrome"],
        tags=["string", "two-pointer", "normalization"],
        summary="문자열을 정제한 뒤 같은 기준으로 앞뒤를 비교하는 전처리 패턴을 익히는 단원",
        overview="문자열 단원에서는 대소문자와 특수문자처럼 비교 전에 제거해야 하는 요소를 먼저 정리하는 습관을 만든다.",
        coreIdea="알파벳과 숫자만 남기고 모두 소문자로 바꾼 뒤, 정제된 문자열이 뒤집은 문자열과 같은지 비교한다.",
        complexityTime="O(n)",
        complexitySpace="O(n)",
        visualFocus="정제된 문자열",
        lessonTitle="정제 후 회문 판별하기",
        objective="전처리와 실제 비교 단계를 분리해 문자열 문제를 안정적으로 구현한다.",
        inputExample='s = "A man, a plan, a canal: Panama"',
        outputExample="True",
        representativeCode=block(
            """
            def is_palindrome(s):
                filtered = "".join(char.lower() for char in s if char.isalnum())
                return filtered == filtered[::-1]
            """
        ),
        traceSteps=[
            step("문자 정제", "알파벳과 숫자만 남기고 모두 소문자로 바꿔 비교 기준을 통일한다."),
            step("뒤집기", "정제된 문자열을 같은 규칙으로 뒤집어 비교 대상을 만든다."),
            step("동일성 비교", "원본과 뒤집은 문자열이 같으면 회문으로 판단한다."),
        ],
        blankPrompt="문자열 문제는 비교 전에 어떤 문자를 남길지 먼저 고정해야 한다.",
        blankSource=block(
            """
            filtered = "".join(char.lower() for char in s if char.isalnum())
            return filtered == filtered[::-1]
            """
        ),
        blankSpecs=[
            blank("b1", 'filtered = "".join(char.lower() for char in s if char.isalnum())', "비교 전 정제 과정을 한 줄로 만든다."),
            blank("b2", "return filtered == filtered[::-1]", "정제된 문자열과 뒤집은 문자열을 비교한다."),
        ],
        parsonsPrompt="정제 -> 뒤집기 비교의 최소 흐름을 코드 순서로 재배치한다.",
        parsonsSource=block(
            """
            def is_palindrome(s):
                filtered = "".join(char.lower() for char in s if char.isalnum())
                return filtered == filtered[::-1]
            """
        ),
        commonMistake={
            "title": "원본 문자열을 그대로 비교하는 실수",
            "whyWrong": "공백, 구두점, 대소문자를 그대로 두면 문제에서 무시하라고 한 요소 때문에 오답이 된다.",
        },
        bridgeSummary="실전 문자열 문제에서는 먼저 '비교 전에 무엇을 버리고 무엇을 남길지'를 정리하면 이후 로직이 단순해진다.",
        problemTitle="특수문자를 무시한 회문 판별",
        problemDescription="문자열에서 알파벳과 숫자만 남기고 소문자로 바꾼 뒤 회문인지 판단한다.",
        inputFormat="문자열 하나가 함수 인자로 주어진다.",
        outputFormat="회문이면 True, 아니면 False를 반환한다.",
        knownEdgeCases=["빈 문자열", "숫자만 있는 문자열", "대소문자만 다른 회문"],
    ),
    make_entry(
        slug="brute-force",
        templateRel="week2/basic/04_brute_force.py",
        title="완전탐색",
        aliases=["brute force", "two sum pairs"],
        tags=["brute-force", "array", "double-loop"],
        summary="가능한 모든 경우를 빠짐없이 확인해 조건을 만족하는 해를 찾는 가장 직접적인 탐색 방식",
        overview="완전탐색 단원에서는 최적화보다 먼저 모든 경우를 빠짐없이 점검하는 기준 구현을 만드는 법을 익힌다.",
        coreIdea="i보다 뒤에 있는 j만 확인하는 이중 반복문으로 모든 인덱스 쌍을 한 번씩만 점검한다.",
        complexityTime="O(n^2)",
        complexitySpace="O(k)",
        visualFocus="인덱스 쌍 (i, j)",
        lessonTitle="모든 두 수 쌍을 확인해 target 찾기",
        objective="이중 반복문의 범위를 정확히 잡아 중복 없이 모든 후보 쌍을 확인한다.",
        inputExample="nums = [1, 3, 4, 2, 5, 6]\ntarget = 7",
        outputExample="[(0, 5), (1, 2), (3, 4)]",
        representativeCode=block(
            """
            def find_two_sum_pairs(nums, target):
                pairs = []
                n = len(nums)

                for i in range(n):
                    for j in range(i + 1, n):
                        if nums[i] + nums[j] == target:
                            pairs.append((i, j))

                return pairs
            """
        ),
        traceSteps=[
            step("첫 인덱스 고정", "바깥 반복문에서 현재 기준이 될 i를 하나 고정한다."),
            step("뒤쪽 후보 확인", "안쪽 반복문은 i보다 큰 j만 돌며 중복 없는 쌍을 만든다."),
            step("조건 만족 시 기록", "합이 target과 같으면 현재 인덱스 쌍을 결과에 추가한다."),
        ],
        blankPrompt="완전탐색은 범위를 빠짐없이 돌되 중복만 막는 것이 핵심이다.",
        blankSource=block(
            """
            pairs = []
            n = len(nums)

            for i in range(n):
                for j in range(i + 1, n):
                    if nums[i] + nums[j] == target:
                        pairs.append((i, j))

            return pairs
            """
        ),
        blankSpecs=[
            blank("b1", "for i in range(n):", "첫 번째 인덱스를 고정하는 바깥 반복문이다."),
            blank("b2", "for j in range(i + 1, n):", "중복을 막기 위해 i 다음부터 도는 안쪽 반복문이다."),
            blank("b3", "pairs.append((i, j))", "조건을 만족한 인덱스 쌍을 결과에 저장한다."),
        ],
        parsonsPrompt="인덱스 고정 -> 뒤쪽 탐색 -> 조건 만족 시 기록 순서를 복원한다.",
        parsonsSource=block(
            """
            def find_two_sum_pairs(nums, target):
                pairs = []
                n = len(nums)
                for i in range(n):
                    for j in range(i + 1, n):
                        if nums[i] + nums[j] == target:
                            pairs.append((i, j))
                return pairs
            """
        ),
        commonMistake={
            "title": "j를 0부터 다시 시작해 같은 쌍을 두 번 보는 실수",
            "whyWrong": "완전탐색이라도 중복 기준을 정해야 (0,1)과 (1,0)을 둘 다 세지 않는다.",
        },
        bridgeSummary="실전 문제에서 더 빠른 풀이를 쓰더라도, 먼저 완전탐색 기준 구현을 만들면 반례와 정답 검증에 큰 도움이 된다.",
        problemTitle="합이 target인 모든 인덱스 쌍 찾기",
        problemDescription="정수 배열에서 두 수의 합이 target이 되는 모든 인덱스 쌍을 찾는다.",
        inputFormat="정수 배열과 목표 합 target이 함수 인자로 주어진다.",
        outputFormat="조건을 만족하는 (i, j) 쌍 리스트를 반환한다.",
        knownEdgeCases=["같은 값이 여러 번 나오는 배열", "정답이 없는 경우", "모든 쌍이 정답인 경우"],
    ),
    make_entry(
        slug="recursion",
        templateRel="week2/basic/05_recursion.py",
        title="재귀함수",
        aliases=["recursion", "factorial", "fibonacci"],
        tags=["recursion", "base-case", "call-stack"],
        summary="base case와 recursive case를 분리해 같은 패턴을 반복 호출하는 사고방식을 익히는 단원",
        overview="재귀 단원에서는 멈추는 조건과 더 작은 문제로 줄이는 규칙이 함께 있어야 함수가 올바르게 동작한다는 점을 익힌다.",
        coreIdea="먼저 가장 작은 경우를 바로 반환하고, 그 외에는 더 작은 입력으로 함수를 다시 호출해 답을 조립한다.",
        complexityTime="O(2^n) / O(n)",
        complexitySpace="O(n)",
        visualFocus="base case와 recursive case",
        lessonTitle="base case와 recursive case로 수열 계산하기",
        objective="재귀 함수에서 종료 조건과 더 작은 문제로 이동하는 규칙을 분명히 나눈다.",
        inputExample="n = 5",
        outputExample="5! = 120\nfib(5) = 5",
        representativeCode=block(
            """
            def factorial(n):
                if n in (0, 1):
                    return 1
                return n * factorial(n - 1)


            def fibonacci(n):
                if n == 0:
                    return 0
                if n == 1:
                    return 1
                return fibonacci(n - 1) + fibonacci(n - 2)
            """
        ),
        traceSteps=[
            step("종료 조건 확인", "가장 작은 입력이면 더 내려가지 않고 바로 답을 반환한다."),
            step("작은 문제 호출", "아직 크기가 남아 있으면 더 작은 n으로 같은 함수를 호출한다."),
            step("결과 조립", "호출 결과를 곱하거나 더해 현재 문제의 답을 만든다."),
        ],
        blankPrompt="재귀 함수는 언제 멈추고, 언제 더 작은 문제로 내려가는지가 핵심이다.",
        blankSource=block(
            """
            if n == 0:
                return 0
            if n == 1:
                return 1
            return fibonacci(n - 1) + fibonacci(n - 2)
            """
        ),
        blankSpecs=[
            blank("b1", "if n == 0:", "첫 번째 종료 조건을 확인한다."),
            blank("b2", "if n == 1:", "두 번째 종료 조건을 확인한다."),
            blank("b3", "return fibonacci(n - 1) + fibonacci(n - 2)", "더 작은 두 문제를 조합해 현재 답을 만든다."),
        ],
        parsonsPrompt="종료 조건을 먼저 두고, 마지막에 recursive case를 배치해야 한다.",
        parsonsSource=block(
            """
            def fibonacci(n):
                if n == 0:
                    return 0
                if n == 1:
                    return 1
                return fibonacci(n - 1) + fibonacci(n - 2)
            """
        ),
        commonMistake={
            "title": "base case 없이 recursive call부터 작성하는 실수",
            "whyWrong": "멈추는 조건이 없으면 함수가 끝없이 내려가거나 잘못된 값을 반환한다.",
        },
        bridgeSummary="재귀 문제를 만나면 먼저 가장 작은 입력의 답을 적고, 그 다음에 '현재 답을 어떤 더 작은 답들로 만들 수 있는가'를 써 보는 것이 안전하다.",
        problemTitle="재귀로 팩토리얼과 피보나치 계산",
        problemDescription="재귀 함수를 사용해 팩토리얼과 피보나치 수를 각각 계산한다.",
        inputFormat="양의 정수 n이 함수 인자로 주어진다.",
        outputFormat="팩토리얼 값과 n번째 피보나치 값을 계산해 반환하거나 출력한다.",
        knownEdgeCases=["n = 0", "n = 1", "재귀 깊이가 커지는 큰 입력"],
    ),
    make_entry(
        slug="backtracking",
        templateRel="week2/basic/06_backtracking.py",
        title="백트래킹",
        aliases=["backtracking", "combinations"],
        tags=["backtracking", "combination", "dfs"],
        summary="선택하고 내려갔다가 되돌리는 과정을 반복해 가능한 해를 체계적으로 생성하는 탐색 방식",
        overview="백트래킹 단원에서는 현재 선택 상태를 들고 내려가며, 탐색이 끝나면 바로 직전 상태로 되돌아오는 흐름을 익힌다.",
        coreIdea="현재 조합에 숫자를 하나 추가하고 재귀 호출한 뒤, 돌아오면 그 숫자를 다시 빼서 다음 후보를 시도한다.",
        complexityTime="O(C(n, k) * k)",
        complexitySpace="O(k)",
        visualFocus="현재 조합 current_combination",
        lessonTitle="조합 생성 백트래킹 흐름 익히기",
        objective="Choose -> Explore -> Unchoose 세 단계를 코드 안에서 한 묶음으로 유지한다.",
        inputExample="n = 4\nk = 2",
        outputExample="[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]",
        representativeCode=block(
            """
            def combinations(n, k):
                result = []

                def backtrack(start, current_combination):
                    if len(current_combination) == k:
                        result.append(current_combination.copy())
                        return

                    for number in range(start, n + 1):
                        current_combination.append(number)
                        backtrack(number + 1, current_combination)
                        current_combination.pop()

                backtrack(1, [])
                return result


            def combinations_itertools_compare(n, k):
                from itertools import combinations as comb
                return [list(values) for values in comb(range(1, n + 1), k)]
            """
        ),
        traceSteps=[
            step("선택 상태 확인", "현재 조합 길이가 k와 같으면 완성된 조합으로 결과에 저장한다."),
            step("후보 선택", "start부터 가능한 숫자를 하나 골라 현재 조합에 추가하고 더 깊이 내려간다."),
            step("상태 복구", "재귀가 끝나면 방금 넣은 숫자를 pop해서 다음 후보를 시도한다."),
        ],
        blankPrompt="백트래킹은 선택, 재귀 호출, 취소가 항상 세트로 움직여야 한다.",
        blankSource=block(
            """
            if len(current_combination) == k:
                result.append(current_combination.copy())
                return

            for number in range(start, n + 1):
                current_combination.append(number)
                backtrack(number + 1, current_combination)
                current_combination.pop()
            """
        ),
        blankSpecs=[
            blank("b1", "result.append(current_combination.copy())", "완성된 조합을 별도 복사본으로 저장한다."),
            blank("b2", "current_combination.append(number)", "현재 숫자를 조합에 선택한다."),
            blank("b3", "current_combination.pop()", "재귀가 끝난 뒤 방금 선택을 되돌린다."),
        ],
        parsonsPrompt="완성 체크 -> 숫자 선택 -> 재귀 -> 복구 순서를 유지해야 한다.",
        parsonsSource=block(
            """
            def backtrack(start, current_combination):
                if len(current_combination) == k:
                    result.append(current_combination.copy())
                    return
                for number in range(start, n + 1):
                    current_combination.append(number)
                    backtrack(number + 1, current_combination)
                    current_combination.pop()
            """
        ),
        commonMistake={
            "title": "append한 값을 pop하지 않고 다음 후보로 넘어가는 실수",
            "whyWrong": "상태 복구가 빠지면 이전 선택이 다음 탐색에도 남아 잘못된 조합이 만들어진다.",
        },
        bridgeSummary="백트래킹 문제에서는 현재 상태를 어떻게 바꾸는지보다, 호출이 끝났을 때 어떻게 원래 상태로 되돌리는지가 더 중요하다.",
        problemTitle="1부터 n까지의 조합 생성",
        problemDescription="1부터 n까지 숫자 중 k개를 골라 만들 수 있는 모든 조합을 생성한다.",
        inputFormat="전체 숫자 개수 n과 선택 개수 k가 함수 인자로 주어진다.",
        outputFormat="모든 조합을 리스트의 리스트 형태로 반환한다.",
        knownEdgeCases=["k = 1", "k = n", "n이 작고 k가 큰 경우"],
    ),
    make_entry(
        slug="complexity",
        templateRel="week2/basic/07_complexity.py",
        title="복잡도",
        aliases=["complexity", "big o"],
        tags=["complexity", "set", "sorting"],
        summary="같은 문제를 서로 다른 시간 복잡도로 풀어 보며 자료구조 선택이 성능에 미치는 영향을 비교하는 단원",
        overview="복잡도 단원에서는 같은 기능을 하는 코드라도 반복 구조와 자료구조에 따라 성능 차이가 크게 난다는 점을 체감한다.",
        coreIdea="중복 탐색을 이중 반복문, 정렬 후 비교, 해시 집합 세 방식으로 구현하고 각각의 비용을 비교한다.",
        complexityTime="O(n^2) / O(n log n) / O(n)",
        complexitySpace="O(1) / O(1) / O(n)",
        visualFocus="중복을 찾는 기준 자료구조",
        lessonTitle="중복 탐색 세 가지 복잡도 비교하기",
        objective="같은 출력이라도 반복 횟수와 보조 자료구조가 어떻게 달라지는지 코드 수준에서 비교한다.",
        inputExample="nums = [4, 3, 2, 7, 8, 2, 3, 1]",
        outputExample="[2, 3]",
        representativeCode=block(
            """
            def find_duplicates_brute_force(nums):
                duplicates = []
                n = len(nums)

                for i in range(n):
                    for j in range(i + 1, n):
                        if nums[i] == nums[j] and nums[i] not in duplicates:
                            duplicates.append(nums[i])
                            break

                return duplicates


            def find_duplicates_sorting(nums):
                if not nums:
                    return []

                nums.sort()
                duplicates = []

                for index in range(len(nums) - 1):
                    if nums[index] == nums[index + 1] and nums[index] not in duplicates:
                        duplicates.append(nums[index])

                return duplicates


            def find_duplicates_hash(nums):
                seen = set()
                duplicates = set()

                for number in nums:
                    if number in seen:
                        duplicates.add(number)
                    else:
                        seen.add(number)

                return list(duplicates)


            def measure_time(func, nums, method_name):
                result = func(nums[:])
                print(f"{method_name}: {sorted(result)}")
                print()
            """
        ),
        traceSteps=[
            step("기준 구현 작성", "먼저 이중 반복문으로 모든 쌍을 직접 비교하는 가장 단순한 구현을 만든다."),
            step("구조 개선", "정렬이나 해시 집합을 써서 비교 범위를 줄이거나 이미 본 값을 저장한다."),
            step("복잡도 비교", "출력은 같지만 반복 수와 추가 메모리가 어떻게 달라지는지 정리한다."),
        ],
        blankPrompt="복잡도 비교의 핵심은 같은 문제를 다른 자료구조로 다시 푸는 데 있다.",
        blankSource=block(
            """
            seen = set()
            duplicates = set()

            for number in nums:
                if number in seen:
                    duplicates.add(number)
                else:
                    seen.add(number)

            return list(duplicates)
            """
        ),
        blankSpecs=[
            blank("b1", "seen = set()", "이미 본 숫자를 저장할 집합을 만든다."),
            blank("b2", "if number in seen:", "현재 숫자가 이미 등장했는지 확인한다."),
            blank("b3", "duplicates.add(number)", "중복으로 확인된 숫자를 결과 집합에 추가한다."),
        ],
        parsonsPrompt="해시 집합 버전의 중복 탐색 흐름을 순서대로 복원한다.",
        parsonsSource=block(
            """
            def find_duplicates_hash(nums):
                seen = set()
                duplicates = set()
                for number in nums:
                    if number in seen:
                        duplicates.add(number)
                    else:
                        seen.add(number)
                return list(duplicates)
            """
        ),
        commonMistake={
            "title": "출력이 같으니 구현 차이도 중요하지 않다고 보는 실수",
            "whyWrong": "같은 정답이라도 입력 크기가 커지면 O(n^2)와 O(n)의 실행 시간 차이는 매우 크게 벌어진다.",
        },
        bridgeSummary="실전 문제에서는 먼저 기준 풀이를 만들고, 병목이 되는 반복이나 조회를 어떤 자료구조로 줄일 수 있는지 바로 이어서 생각하는 습관이 중요하다.",
        problemTitle="배열 중복 원소 찾기 방식 비교",
        problemDescription="배열에서 중복된 원소를 찾아야 할 때 brute force, sorting, hash 방식이 각각 어떻게 동작하는지 비교한다.",
        inputFormat="정수 배열이 함수 인자로 주어진다.",
        outputFormat="중복된 원소 리스트를 반환한다.",
        knownEdgeCases=["중복이 전혀 없는 배열", "같은 값이 세 번 이상 나오는 배열", "빈 배열"],
    ),
    make_entry(
        slug="sorting",
        templateRel="week2/basic/09_insertion_sort.py",
        title="정렬",
        aliases=["sorting", "insertion sort"],
        tags=["sorting", "insertion-sort", "array"],
        summary="정렬된 구간에 새 원소를 한 칸씩 끼워 넣으며 배열을 정리하는 기본 정렬 패턴",
        overview="정렬 단원에서는 이미 정렬된 앞부분을 유지하면서 새 원소를 적절한 위치에 끼워 넣는 삽입 정렬의 흐름을 익힌다.",
        coreIdea="현재 key보다 큰 값들을 오른쪽으로 한 칸씩 밀고, 빈 자리에 key를 끼워 넣는다.",
        complexityTime="O(n^2)",
        complexitySpace="O(1)",
        visualFocus="정렬된 앞부분과 key 위치",
        lessonTitle="삽입 정렬로 정렬된 구간 확장하기",
        objective="key를 뽑고, 큰 값을 미루고, 빈 자리에 다시 넣는 세 단계를 유지한다.",
        inputExample="arr = [12, 11, 13, 5, 6]",
        outputExample="[5, 6, 11, 12, 13]",
        representativeCode=block(
            """
            def insertion_sort(arr):
                for i in range(1, len(arr)):
                    key = arr[i]
                    j = i - 1

                    while j >= 0 and arr[j] > key:
                        arr[j + 1] = arr[j]
                        j -= 1

                    arr[j + 1] = key

                return arr


            def insertion_sort_with_steps(arr):
                print(f"초기 배열: {arr}")

                for i in range(1, len(arr)):
                    key = arr[i]
                    j = i - 1

                    print(f"\\nStep {i}: key = {key}")
                    print(f"정렬된 부분: {arr[:i]}")

                    while j >= 0 and arr[j] > key:
                        arr[j + 1] = arr[j]
                        j -= 1

                    arr[j + 1] = key
                    print(f"삽입 후: {arr}")

                return arr
            """
        ),
        traceSteps=[
            step("key 선택", "정렬되지 않은 구간의 첫 원소를 key로 들고 나온다."),
            step("오른쪽 밀기", "정렬된 앞부분에서 key보다 큰 값들을 한 칸씩 오른쪽으로 밀어 빈칸을 만든다."),
            step("삽입", "비교가 끝난 자리에 key를 넣어 정렬된 구간을 한 칸 늘린다."),
        ],
        blankPrompt="삽입 정렬은 key를 분리한 뒤 큰 값을 미는 흐름이 끊기면 안 된다.",
        blankSource=block(
            """
            for i in range(1, len(arr)):
                key = arr[i]
                j = i - 1

                while j >= 0 and arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1

                arr[j + 1] = key
            """
        ),
        blankSpecs=[
            blank("b1", "key = arr[i]", "삽입할 현재 원소를 따로 저장한다."),
            blank("b2", "while j >= 0 and arr[j] > key:", "밀어낼 원소가 남아 있는 동안 반복한다."),
            blank("b3", "arr[j + 1] = key", "빈 자리에 key를 삽입한다."),
        ],
        parsonsPrompt="key 선택 -> 큰 값 이동 -> key 삽입 흐름을 코드 줄로 재구성한다.",
        parsonsSource=block(
            """
            def insertion_sort(arr):
                for i in range(1, len(arr)):
                    key = arr[i]
                    j = i - 1
                    while j >= 0 and arr[j] > key:
                        arr[j + 1] = arr[j]
                        j -= 1
                    arr[j + 1] = key
                return arr
            """
        ),
        commonMistake={
            "title": "key를 따로 저장하지 않고 바로 덮어쓰는 실수",
            "whyWrong": "이동 과정에서 현재 값이 사라지면 마지막에 어디에 넣어야 할지 잃어버린다.",
        },
        bridgeSummary="정렬 문제에서는 '현재 보고 있는 값'과 '이미 정렬된 구간'을 분리해서 생각하면 로직을 안정적으로 유지할 수 있다.",
        problemTitle="삽입 정렬 구현",
        problemDescription="배열을 앞에서부터 보며 각 원소를 정렬된 위치에 삽입해 오름차순으로 정렬한다.",
        inputFormat="정렬되지 않은 정수 배열이 함수 인자로 주어진다.",
        outputFormat="정렬된 배열을 반환한다.",
        knownEdgeCases=["이미 정렬된 배열", "역순 배열", "중복 원소가 있는 배열"],
    ),
    make_entry(
        slug="number-theory",
        templateRel="week2/basic/10_number_theory.py",
        title="정수론",
        aliases=["number theory", "gcd", "lcm"],
        tags=["math", "gcd", "prime"],
        summary="유클리드 호제법을 중심으로 최대공약수, 최소공배수, 소수 판별 같은 기본 수론 도구를 묶어 익히는 단원",
        overview="정수론 단원에서는 나눗셈의 나머지를 반복해 공약수를 빠르게 찾고, 그 결과를 다른 계산에 재사용하는 법을 익힌다.",
        coreIdea="gcd(a, b)는 gcd(b, a % b)로 줄일 수 있고, LCM과 확장 유클리드도 이 재귀 구조를 기반으로 계산한다.",
        complexityTime="O(log min(a, b))",
        complexitySpace="O(log min(a, b))",
        visualFocus="a, b, 나머지의 변화",
        lessonTitle="유클리드 호제법으로 GCD와 LCM 구하기",
        objective="나머지가 0이 될 때까지 수를 줄이는 패턴을 기준 구현으로 고정한다.",
        inputExample="a = 48\nb = 18",
        outputExample="GCD = 6\nLCM = 144",
        representativeCode=block(
            """
            def gcd(a, b):
                if b == 0:
                    return a
                return gcd(b, a % b)


            def gcd_iterative(a, b):
                while b:
                    a, b = b, a % b
                return a


            def lcm(a, b):
                return a * b // gcd(a, b)


            def extended_gcd(a, b):
                if b == 0:
                    return a, 1, 0
                g, x1, y1 = extended_gcd(b, a % b)
                x = y1
                y = x1 - (a // b) * y1
                return g, x, y


            def is_prime(n):
                if n < 2:
                    return False
                if n == 2:
                    return True
                if n % 2 == 0:
                    return False

                limit = int(n ** 0.5)
                for divisor in range(3, limit + 1, 2):
                    if n % divisor == 0:
                        return False

                return True
            """
        ),
        traceSteps=[
            step("나머지 축소", "gcd는 두 수를 더 작은 쌍 (b, a % b)로 줄여 간다."),
            step("기본값 재사용", "LCM과 확장 유클리드도 같은 gcd 구조를 바탕으로 계산을 이어 간다."),
            step("약수 탐색 최적화", "소수 판별은 sqrt(n)까지만 검사해 불필요한 나눗셈을 줄인다."),
        ],
        blankPrompt="정수론 구현은 나머지로 문제 크기를 줄이는 규칙을 정확히 기억해야 한다.",
        blankSource=block(
            """
            if b == 0:
                return a
            return gcd(b, a % b)
            """
        ),
        blankSpecs=[
            blank("b1", "if b == 0:", "나머지가 0이면 더 이상 줄일 수 없다."),
            blank("b2", "return a", "종료 조건에서 최대공약수를 반환한다."),
            blank("b3", "return gcd(b, a % b)", "더 작은 문제로 재귀 호출한다."),
        ],
        parsonsPrompt="유클리드 호제법의 종료 조건과 재귀 호출 순서를 복원한다.",
        parsonsSource=block(
            """
            def gcd(a, b):
                if b == 0:
                    return a
                return gcd(b, a % b)
            """
        ),
        commonMistake={
            "title": "a % b와 b의 위치를 뒤바꾸는 실수",
            "whyWrong": "유클리드 호제법은 (b, a % b) 순서로 줄여야 동일한 최대공약수를 유지할 수 있다.",
        },
        bridgeSummary="수학 문제에서는 식을 외우는 것보다 '어떤 값이 줄어들며 언제 종료되는가'를 먼저 보면 구현 실수가 줄어든다.",
        problemTitle="최대공약수와 최소공배수 계산",
        problemDescription="두 양의 정수가 주어질 때 최대공약수와 최소공배수를 계산한다.",
        inputFormat="두 양의 정수 a, b가 함수 인자로 주어진다.",
        outputFormat="GCD와 LCM을 계산해 반환하거나 출력한다.",
        knownEdgeCases=["두 수가 같은 경우", "서로소인 경우", "한 수가 다른 수의 배수인 경우"],
    ),
    make_entry(
        slug="binary-search",
        templateRel="week3/basic/01_binary_search.py",
        title="이분탐색",
        aliases=["binary search"],
        tags=["search", "array", "sorted"],
        summary="정렬된 배열에서 비교 결과에 따라 탐색 범위를 절반씩 버리는 대표 탐색 알고리즘",
        overview="이분탐색은 정렬된 배열에서 가운데 값을 기준으로 target이 있을 수 없는 절반을 과감히 버리며 진행한다.",
        coreIdea="mid를 계산하고 arr[mid]와 target을 비교한 뒤, 남아 있어야 할 절반만 다음 탐색 범위로 남긴다.",
        complexityTime="O(log n)",
        complexitySpace="O(1)",
        visualFocus="left, mid, right 포인터",
        lessonTitle="정렬 배열에서 target 위치 찾기",
        objective="mid 계산 -> 값 비교 -> 범위 축소 순서를 흔들리지 않게 유지한다.",
        inputExample="arr = [1, 3, 5, 7, 9, 11, 13]\ntarget = 7",
        outputExample="3",
        representativeCode=block(
            """
            def binary_search(arr, target):
                left = 0
                right = len(arr) - 1

                while left <= right:
                    mid = (left + right) // 2

                    if arr[mid] == target:
                        return mid
                    if arr[mid] < target:
                        left = mid + 1
                    else:
                        right = mid - 1

                return -1
            """
        ),
        traceSteps=[
            step("범위 초기화", "left는 0, right는 마지막 인덱스로 두고 전체 구간을 탐색 범위로 잡는다."),
            step("mid 비교", "가운데 위치 mid를 계산해 target과 현재 값을 비교한다."),
            step("절반 제거", "비교 결과에 따라 왼쪽 또는 오른쪽 절반만 남기고 나머지는 버린다."),
        ],
        blankPrompt="mid 계산과 범위 축소 방향이 정확해야 반례를 피할 수 있다.",
        blankSource=block(
            """
            left = 0
            right = len(arr) - 1

            while left <= right:
                mid = (left + right) // 2

                if arr[mid] == target:
                    return mid
                if arr[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1

            return -1
            """
        ),
        blankSpecs=[
            blank("b1", "mid = (left + right) // 2", "현재 탐색 범위의 가운데 인덱스를 만든다."),
            blank("b2", "left = mid + 1", "target이 더 오른쪽에 있을 때 왼쪽 경계를 움직인다."),
            blank("b3", "right = mid - 1", "target이 더 왼쪽에 있을 때 오른쪽 경계를 움직인다."),
        ],
        parsonsPrompt="mid 계산 -> 비교 -> 경계 갱신 흐름을 줄 순서로 재배치한다.",
        parsonsSource=block(
            """
            def binary_search(arr, target):
                left = 0
                right = len(arr) - 1
                while left <= right:
                    mid = (left + right) // 2
                    if arr[mid] == target:
                        return mid
                    if arr[mid] < target:
                        left = mid + 1
                    else:
                        right = mid - 1
                return -1
            """
        ),
        commonMistake={
            "title": "비교 전에 경계를 먼저 줄이는 실수",
            "whyWrong": "현재 mid 값 확인 없이 left나 right를 바꾸면 target을 놓치거나 루프 조건이 깨질 수 있다.",
        },
        bridgeSummary="이분탐색 실전 문제는 대부분 'mid를 어떻게 비교하고 어떤 절반을 버릴지'만 정확히 지키면 핵심은 해결된다.",
        problemTitle="정렬 배열에서 정수 존재 여부 판별",
        problemDescription="정렬된 배열과 여러 질의가 주어질 때 각 질의 값이 배열에 존재하는지 이분탐색으로 판단한다.",
        inputFormat="정렬된 배열과 target 값이 함수 인자로 주어진다.",
        outputFormat="target의 인덱스를 반환하고 없으면 -1을 반환한다.",
        knownEdgeCases=["배열 길이가 1인 경우", "target이 첫 원소 또는 마지막 원소인 경우", "존재하지 않는 target"],
    ),
    make_entry(
        slug="divide-and-conquer",
        templateRel="week3/basic/02_divide_conquer.py",
        title="분할정복",
        aliases=["divide and conquer"],
        tags=["divide-and-conquer", "recursion", "array"],
        summary="문제를 둘로 나눈 뒤 각 부분의 답을 구하고 다시 합쳐 전체 답을 만드는 기본 분할정복 패턴",
        overview="분할정복 단원에서는 전체 문제를 좌우 절반으로 쪼갠 다음, 각 부분 문제의 답을 다시 합쳐 전체 답을 만드는 구조를 익힌다.",
        coreIdea="배열 구간을 절반으로 나눠 왼쪽 최댓값과 오른쪽 최댓값을 재귀로 구하고 마지막에 max로 합친다.",
        complexityTime="O(n)",
        complexitySpace="O(log n)",
        visualFocus="left, mid, right 구간",
        lessonTitle="배열 최댓값을 절반씩 나눠 찾기",
        objective="base case로 멈추고, 좌우 절반 해를 다시 합치는 분할정복 틀을 익힌다.",
        inputExample="arr = [3, 5, 1, 8, 2, 9, 4]",
        outputExample="9",
        representativeCode=block(
            """
            def find_max_divide_conquer(arr, left, right):
                if left == right:
                    return arr[left]

                mid = (left + right) // 2
                left_max = find_max_divide_conquer(arr, left, mid)
                right_max = find_max_divide_conquer(arr, mid + 1, right)
                return max(left_max, right_max)
            """
        ),
        traceSteps=[
            step("기저 구간 확인", "구간에 원소가 하나만 남으면 그 값이 곧 최댓값이다."),
            step("구간 분할", "중간 인덱스를 계산해 왼쪽 절반과 오른쪽 절반으로 나눈다."),
            step("결과 결합", "각 절반의 최댓값을 비교해 더 큰 값을 반환한다."),
        ],
        blankPrompt="분할정복은 언제 멈추고, 어디서 둘로 나누는지가 핵심이다.",
        blankSource=block(
            """
            if left == right:
                return arr[left]

            mid = (left + right) // 2
            left_max = find_max_divide_conquer(arr, left, mid)
            right_max = find_max_divide_conquer(arr, mid + 1, right)
            return max(left_max, right_max)
            """
        ),
        blankSpecs=[
            blank("b1", "if left == right:", "원소가 하나 남은 구간인지 확인한다."),
            blank("b2", "mid = (left + right) // 2", "구간을 둘로 나누는 기준점을 만든다."),
            blank("b3", "return max(left_max, right_max)", "부분 문제의 답을 합쳐 전체 답을 만든다."),
        ],
        parsonsPrompt="base case -> 분할 -> 결합 순서를 그대로 복원한다.",
        parsonsSource=block(
            """
            def find_max_divide_conquer(arr, left, right):
                if left == right:
                    return arr[left]
                mid = (left + right) // 2
                left_max = find_max_divide_conquer(arr, left, mid)
                right_max = find_max_divide_conquer(arr, mid + 1, right)
                return max(left_max, right_max)
            """
        ),
        commonMistake={
            "title": "mid를 기준으로 같은 구간을 다시 호출하는 실수",
            "whyWrong": "분할 범위가 줄지 않으면 재귀가 끝나지 않거나 일부 구간을 중복 계산한다.",
        },
        bridgeSummary="분할정복 문제에서는 '어떻게 나눌지'와 '부분 해를 어떤 연산으로 합칠지'를 먼저 적으면 구현이 깔끔해진다.",
        problemTitle="분할정복으로 배열 최댓값 찾기",
        problemDescription="배열 구간을 절반씩 나눠 각 구간의 최댓값을 구하고 다시 합쳐 전체 최댓값을 찾는다.",
        inputFormat="정수 배열과 시작/끝 인덱스가 함수 인자로 주어진다.",
        outputFormat="주어진 구간의 최댓값을 반환한다.",
        knownEdgeCases=["원소가 1개인 배열", "오름차순 배열", "최댓값이 맨 앞에 있는 경우"],
    ),
    make_entry(
        slug="stack",
        templateRel="week3/basic/05_stack.py",
        title="스택",
        aliases=["stack", "parentheses"],
        tags=["stack", "string", "validation"],
        summary="가장 최근에 넣은 값을 먼저 꺼내는 구조로 짝과 중첩을 검사하는 대표 자료구조 단원",
        overview="스택 단원에서는 열고 닫히는 구조를 검사할 때 왜 최근 상태를 먼저 확인해야 하는지 이해한다.",
        coreIdea="여는 괄호는 push하고 닫는 괄호를 만나면 pop해 짝을 맞춘 뒤, 마지막에 스택이 비어 있는지 확인한다.",
        complexityTime="O(n)",
        complexitySpace="O(n)",
        visualFocus="stack 상태",
        lessonTitle="스택으로 괄호 짝 검사하기",
        objective="push, pop, 빈 스택 검사 세 동작만으로 올바른 괄호를 판별한다.",
        inputExample='s = "()(())"',
        outputExample="True",
        representativeCode=block(
            """
            def is_valid_parentheses(s):
                stack = []

                for char in s:
                    if char == "(":
                        stack.append(char)
                    else:
                        if not stack:
                            return False
                        stack.pop()

                return not stack
            """
        ),
        traceSteps=[
            step("문자 순회", "문자열을 왼쪽부터 한 글자씩 읽는다."),
            step("최근 상태 갱신", "여는 괄호는 스택에 넣고 닫는 괄호는 스택에서 꺼낸다."),
            step("최종 검증", "중간에 빈 스택에서 pop하면 실패, 끝났을 때 스택이 비어 있으면 성공이다."),
        ],
        blankPrompt="스택 문제는 언제 push하고 언제 pop하는지 명확해야 한다.",
        blankSource=block(
            """
            stack = []

            for char in s:
                if char == "(":
                    stack.append(char)
                else:
                    if not stack:
                        return False
                    stack.pop()

            return not stack
            """
        ),
        blankSpecs=[
            blank("b1", "stack.append(char)", "여는 괄호를 스택에 저장한다."),
            blank("b2", "if not stack:", "닫는 괄호를 처리하기 전에 스택이 비었는지 확인한다."),
            blank("b3", "return not stack", "끝났을 때 스택이 비어 있어야 올바른 괄호다."),
        ],
        parsonsPrompt="push -> 빈 스택 검사 -> pop -> 최종 비었는지 확인 순서를 복원한다.",
        parsonsSource=block(
            """
            def is_valid_parentheses(s):
                stack = []
                for char in s:
                    if char == "(":
                        stack.append(char)
                    else:
                        if not stack:
                            return False
                        stack.pop()
                return not stack
            """
        ),
        commonMistake={
            "title": "닫는 괄호를 만났을 때 빈 스택 검사 없이 pop하는 실수",
            "whyWrong": "이미 짝이 맞지 않는 입력인데도 예외가 나거나 잘못된 True 결과를 만들 수 있다.",
        },
        bridgeSummary="실전 스택 문제도 대부분 '최근에 열린 상태를 지금 닫을 수 있는가'를 검사하는 구조로 바꿔 보면 단순해진다.",
        problemTitle="괄호 문자열 유효성 검사",
        problemDescription="괄호 문자열이 올바르게 짝지어져 있는지 스택으로 판단한다.",
        inputFormat="괄호 문자열 하나가 함수 인자로 주어진다.",
        outputFormat="올바르면 True, 아니면 False를 반환한다.",
        knownEdgeCases=["빈 문자열", "닫는 괄호로 시작하는 경우", "끝까지 열기만 있는 경우"],
    ),
    make_entry(
        slug="queue",
        templateRel="week3/basic/06_queue.py",
        title="큐",
        aliases=["queue", "printer queue"],
        tags=["queue", "fifo", "deque"],
        summary="먼저 들어온 작업이 먼저 처리되는 FIFO 구조를 실제 처리 순서와 함께 익히는 단원",
        overview="큐 단원에서는 입력 순서와 처리 순서가 같아야 하는 문제를 자료구조 관점에서 해석하는 법을 배운다.",
        coreIdea="작업을 deque에 넣고, 앞에서 하나씩 꺼내 처리 목록에 추가하면 FIFO 순서가 유지된다.",
        complexityTime="O(n)",
        complexitySpace="O(n)",
        visualFocus="큐의 앞과 뒤",
        lessonTitle="큐로 프린터 작업 순서 처리하기",
        objective="enqueue된 순서를 그대로 dequeue해 처리 순서에 반영한다.",
        inputExample='jobs = ["문서A", "문서B", "문서C"]',
        outputExample="['문서A', '문서B', '문서C']",
        representativeCode=block(
            """
            from collections import deque


            def process_print_queue(jobs):
                queue = deque(jobs)
                processed = []

                while queue:
                    job = queue.popleft()
                    print(f"처리: {job}")
                    processed.append(job)

                return processed
            """
        ),
        traceSteps=[
            step("초기 적재", "입력 작업 목록을 deque로 감싸 FIFO 큐를 만든다."),
            step("앞에서 꺼내기", "큐가 빌 때까지 맨 앞 작업을 popleft로 꺼낸다."),
            step("처리 기록", "처리한 작업을 출력하고 결과 리스트에 같은 순서로 저장한다."),
        ],
        blankPrompt="큐 문제는 자료가 들어간 순서와 나오는 순서를 일관되게 유지해야 한다.",
        blankSource=block(
            """
            queue = deque(jobs)
            processed = []

            while queue:
                job = queue.popleft()
                print(f"처리: {job}")
                processed.append(job)

            return processed
            """
        ),
        blankSpecs=[
            blank("b1", "queue = deque(jobs)", "작업 목록을 큐로 바꾼다."),
            blank("b2", "job = queue.popleft()", "맨 앞 작업을 꺼낸다."),
            blank("b3", "processed.append(job)", "처리 순서를 결과 리스트에 저장한다."),
        ],
        parsonsPrompt="큐 생성 -> 앞에서 꺼내기 -> 처리 기록 순서를 복원한다.",
        parsonsSource=block(
            """
            def process_print_queue(jobs):
                queue = deque(jobs)
                processed = []
                while queue:
                    job = queue.popleft()
                    print(f"처리: {job}")
                    processed.append(job)
                return processed
            """
        ),
        commonMistake={
            "title": "리스트의 뒤에서 pop해 스택처럼 처리하는 실수",
            "whyWrong": "FIFO가 깨지면 가장 먼저 들어온 작업이 먼저 처리된다는 문제 조건을 만족하지 못한다.",
        },
        bridgeSummary="작업 순서가 중요한 실전 문제에서는 '새 작업은 어디에 넣고, 다음 작업은 어디에서 꺼내는가'를 먼저 정하면 구현이 단순해진다.",
        problemTitle="프린터 작업 대기열 처리",
        problemDescription="들어온 순서대로 프린터 작업을 처리하는 큐를 구현한다.",
        inputFormat="작업 이름 문자열 리스트가 함수 인자로 주어진다.",
        outputFormat="처리된 작업 이름 리스트를 반환한다.",
        knownEdgeCases=["작업이 없는 경우", "작업이 1개인 경우", "같은 이름 작업이 반복되는 경우"],
    ),
    make_entry(
        slug="priority-queue",
        templateRel="week3/basic/07_priority_queue.py",
        title="우선순위 큐",
        aliases=["priority queue", "heap"],
        tags=["heap", "priority-queue", "greedy"],
        summary="단순 입력 순서 대신 우선순위가 가장 높은 항목을 먼저 꺼내야 할 때 쓰는 자료구조",
        overview="우선순위 큐 단원에서는 먼저 들어온 순서가 아니라 더 중요한 값부터 처리하는 구조를 heap으로 구현한다.",
        coreIdea="모든 환자를 (우선순위, 이름) 튜플로 힙에 넣고, heappop으로 가장 작은 우선순위부터 꺼낸다.",
        complexityTime="O(n log n)",
        complexitySpace="O(n)",
        visualFocus="힙의 최상단 우선순위",
        lessonTitle="우선순위 큐로 응급실 환자 처리하기",
        objective="힙에 넣을 때와 꺼낼 때 어떤 값이 우선순위 기준인지 분명히 한다.",
        inputExample='patients = [("김철수", 3), ("이영희", 1), ("박민수", 2)]',
        outputExample="['이영희', '박민수', '김철수']",
        representativeCode=block(
            """
            import heapq


            def process_emergency_room(patients):
                heap = []

                for name, priority in patients:
                    heapq.heappush(heap, (priority, name))

                processed = []

                while heap:
                    priority, name = heapq.heappop(heap)
                    print(f"처리: {name} (우선순위: {priority})")
                    processed.append(name)

                return processed
            """
        ),
        traceSteps=[
            step("힙 초기화", "빈 리스트를 힙으로 사용해 우선순위 큐를 준비한다."),
            step("우선순위 적재", "환자 정보를 (priority, name) 형태로 넣어 가장 작은 priority가 먼저 오게 한다."),
            step("최고 우선순위 처리", "heappop으로 가장 시급한 환자를 꺼내 처리 순서에 기록한다."),
        ],
        blankPrompt="우선순위 큐는 어떤 값을 힙의 기준으로 넣는지가 가장 중요하다.",
        blankSource=block(
            """
            heap = []

            for name, priority in patients:
                heapq.heappush(heap, (priority, name))

            processed = []

            while heap:
                priority, name = heapq.heappop(heap)
                print(f"처리: {name} (우선순위: {priority})")
                processed.append(name)

            return processed
            """
        ),
        blankSpecs=[
            blank("b1", "heapq.heappush(heap, (priority, name))", "우선순위가 먼저 오도록 힙에 넣는다."),
            blank("b2", "priority, name = heapq.heappop(heap)", "가장 높은 우선순위 환자를 꺼낸다."),
            blank("b3", "processed.append(name)", "처리 순서를 결과에 기록한다."),
        ],
        parsonsPrompt="힙 적재 -> heappop -> 처리 기록 순서를 복원한다.",
        parsonsSource=block(
            """
            def process_emergency_room(patients):
                heap = []
                for name, priority in patients:
                    heapq.heappush(heap, (priority, name))
                processed = []
                while heap:
                    priority, name = heapq.heappop(heap)
                    print(f"처리: {name} (우선순위: {priority})")
                    processed.append(name)
                return processed
            """
        ),
        commonMistake={
            "title": "이름을 먼저 넣어 우선순위 대신 사전순으로 정렬되는 실수",
            "whyWrong": "힙은 튜플의 첫 원소부터 비교하므로 우선순위 값이 맨 앞에 있어야 한다.",
        },
        bridgeSummary="실전 문제에서 '가장 급한 것부터 뽑는다'가 보이면, 어떤 값을 heap의 첫 원소로 둘지부터 정하는 것이 좋다.",
        problemTitle="응급실 환자 우선 처리",
        problemDescription="환자 이름과 우선순위가 주어질 때 우선순위가 높은 환자부터 처리한다.",
        inputFormat="(이름, 우선순위) 튜플 리스트가 함수 인자로 주어진다.",
        outputFormat="처리된 환자 이름 순서를 리스트로 반환한다.",
        knownEdgeCases=["환자가 없는 경우", "우선순위가 이미 정렬된 경우", "우선순위 값이 크게 차이나는 경우"],
    ),
    make_entry(
        slug="linked-list",
        templateRel="week3/basic/08_linked_list.py",
        title="링크드리스트",
        aliases=["linked list"],
        tags=["linked-list", "pointer", "node"],
        summary="노드와 포인터를 따라가며 값을 저장하고 순회하는 선형 자료구조의 기본 구조",
        overview="링크드리스트 단원에서는 배열처럼 인덱스로 접근하지 않고, 포인터를 따라 마지막 노드까지 이동하는 방식을 익힌다.",
        coreIdea="append는 마지막 노드까지 next를 따라가 새 노드를 연결하고, print_list는 head부터 끝까지 순회하며 값을 수집한다.",
        complexityTime="O(n)",
        complexitySpace="O(1)",
        visualFocus="head와 next 포인터",
        lessonTitle="연결 리스트에 노드 추가하고 순회하기",
        objective="head 처리와 마지막 노드 탐색을 분리해 연결 리스트 기본 동작을 안정적으로 구현한다.",
        inputExample="1 -> 2 -> 3",
        outputExample="[1, 2, 3]",
        representativeCode=block(
            """
            class Node:
                def __init__(self, data):
                    self.data = data
                    self.next = None


            class LinkedList:
                def __init__(self):
                    self.head = None

                def append(self, data):
                    new_node = Node(data)

                    if self.head is None:
                        self.head = new_node
                        return

                    current = self.head
                    while current.next is not None:
                        current = current.next

                    current.next = new_node

                def print_list(self):
                    values = []
                    current = self.head

                    while current is not None:
                        values.append(current.data)
                        current = current.next

                    return values
            """
        ),
        traceSteps=[
            step("빈 리스트 처리", "append 호출 시 head가 비어 있으면 새 노드를 바로 head로 둔다."),
            step("끝까지 이동", "리스트가 비어 있지 않으면 current를 next로 이동시켜 마지막 노드를 찾는다."),
            step("연결과 순회", "마지막 노드의 next를 새 노드로 바꾸고, 출력 시에는 head부터 끝까지 값을 읽는다."),
        ],
        blankPrompt="연결 리스트는 빈 리스트 처리와 마지막 노드 탐색을 빼먹지 않아야 한다.",
        blankSource=block(
            """
            new_node = Node(data)

            if self.head is None:
                self.head = new_node
                return

            current = self.head
            while current.next is not None:
                current = current.next

            current.next = new_node
            """
        ),
        blankSpecs=[
            blank("b1", "if self.head is None:", "빈 리스트인지 먼저 확인한다."),
            blank("b2", "while current.next is not None:", "마지막 노드를 찾을 때까지 포인터를 이동한다."),
            blank("b3", "current.next = new_node", "마지막 노드 뒤에 새 노드를 연결한다."),
        ],
        parsonsPrompt="빈 리스트 처리 -> 마지막 노드 찾기 -> 연결 순서를 복원한다.",
        parsonsSource=block(
            """
            def append(self, data):
                new_node = Node(data)
                if self.head is None:
                    self.head = new_node
                    return
                current = self.head
                while current.next is not None:
                    current = current.next
                current.next = new_node
            """
        ),
        commonMistake={
            "title": "head가 비어 있는 경우와 일반 경우를 같은 흐름으로 처리하는 실수",
            "whyWrong": "첫 노드를 따로 연결하지 않으면 빈 리스트에 값을 추가할 수 없다.",
        },
        bridgeSummary="포인터 기반 자료구조는 인덱스 대신 '현재 노드에서 다음 노드로 어떻게 이동하는가'를 따라가며 구현해야 한다.",
        problemTitle="단순 연결 리스트 기본 구현",
        problemDescription="append와 print_list를 가진 단순 연결 리스트를 구현한다.",
        inputFormat="연결 리스트에 넣을 값들이 순서대로 주어진다.",
        outputFormat="연결 리스트를 순회한 값 리스트를 반환한다.",
        knownEdgeCases=["빈 리스트에 첫 노드 추가", "원소가 1개인 리스트", "여러 노드를 연속 추가하는 경우"],
    ),
    make_entry(
        slug="hash-table",
        templateRel="week3/basic/09_hash_table.py",
        title="해시 테이블",
        aliases=["hash table", "dictionary"],
        tags=["hash-table", "dict", "lookup"],
        summary="키로 값을 빠르게 찾는 딕셔너리 기반 접근 패턴을 성적 관리 예제로 익히는 단원",
        overview="해시 테이블 단원에서는 이름 같은 키로 값을 즉시 조회하고, 전체 값 집합에서 요약 통계를 구하는 흐름을 익힌다.",
        coreIdea="점수 딕셔너리의 values로 평균을 계산하고, key=scores.get 패턴으로 최고 점수 학생을 찾는다.",
        complexityTime="O(n) / O(1)",
        complexitySpace="O(1)",
        visualFocus="학생 이름 키와 점수 값",
        lessonTitle="딕셔너리 기반 성적 관리 구현하기",
        objective="집계 연산과 단일 키 조회를 해시 테이블 연산으로 분리해 구현한다.",
        inputExample='students = {"Alice": 85, "Bob": 92, "Charlie": 78, "David": 95}',
        outputExample="평균 점수: 87.5\n최고 점수: David (95점)",
        representativeCode=block(
            """
            def manage_grades(students):
                average = sum(students.values()) / len(students)
                top_student = max(students, key=students.get)
                top_score = students[top_student]
                return average, top_student, top_score


            def find_student_score(students, name):
                return students.get(name)
            """
        ),
        traceSteps=[
            step("값 집계", "딕셔너리 values를 모아 평균 점수를 계산한다."),
            step("최대값 조회", "max와 students.get을 조합해 최고 점수 학생 이름을 찾는다."),
            step("단일 키 조회", "특정 학생 점수는 get으로 바로 찾고 없으면 None을 돌려준다."),
        ],
        blankPrompt="딕셔너리 문제는 전체 집계와 단일 키 조회를 나눠 생각하면 단순해진다.",
        blankSource=block(
            """
            average = sum(students.values()) / len(students)
            top_student = max(students, key=students.get)
            top_score = students[top_student]
            return average, top_student, top_score
            """
        ),
        blankSpecs=[
            blank("b1", "average = sum(students.values()) / len(students)", "모든 점수의 평균을 계산한다."),
            blank("b2", "top_student = max(students, key=students.get)", "점수가 가장 높은 학생 이름을 찾는다."),
            blank("b3", "top_score = students[top_student]", "찾은 학생의 점수를 꺼낸다."),
        ],
        parsonsPrompt="평균 계산 -> 최고점 학생 찾기 -> 점수 조회 순서를 복원한다.",
        parsonsSource=block(
            """
            def manage_grades(students):
                average = sum(students.values()) / len(students)
                top_student = max(students, key=students.get)
                top_score = students[top_student]
                return average, top_student, top_score
            """
        ),
        commonMistake={
            "title": "학생 이름이 아닌 점수 배열만 보고 최고점 학생 이름을 잃어버리는 실수",
            "whyWrong": "해시 테이블의 장점은 키와 값을 같이 다루는 데 있으므로, 값만 분리하면 대응 관계를 다시 찾아야 한다.",
        },
        bridgeSummary="실전 해시 문제에서도 전체 통계와 빠른 조회를 분리해 생각하면, 어떤 연산을 딕셔너리에 맡겨야 할지 명확해진다.",
        problemTitle="학생 성적 해시 테이블 관리",
        problemDescription="학생 이름을 키로 하는 딕셔너리에서 평균, 최고 점수 학생, 개별 학생 점수를 관리한다.",
        inputFormat="학생 이름을 키, 점수를 값으로 갖는 딕셔너리가 함수 인자로 주어진다.",
        outputFormat="평균과 최고 점수 학생 정보를 반환하고, 개별 조회는 점수를 반환한다.",
        knownEdgeCases=["조회할 학생이 없는 경우", "최고 점수가 마지막에 나오는 경우", "점수가 모두 같은 경우"],
    ),
    make_entry(
        slug="tree",
        templateRel="week4/basic/01_binary_tree.py",
        title="트리",
        aliases=["tree", "binary tree"],
        tags=["tree", "traversal", "recursion"],
        summary="루트와 자식 관계를 따라 전위, 중위, 후위 순회를 구현하며 재귀 트리 구조를 익히는 단원",
        overview="트리 단원에서는 같은 노드 구조라도 방문 순서에 따라 결과가 달라진다는 점을 순회 예제로 체감한다.",
        coreIdea="각 순회는 루트, 왼쪽, 오른쪽을 방문하는 순서만 다르고, 구현 구조는 재귀적으로 동일하다.",
        complexityTime="O(n)",
        complexitySpace="O(h)",
        visualFocus="루트, 왼쪽, 오른쪽 방문 순서",
        lessonTitle="전위·중위·후위 순회 순서 익히기",
        objective="재귀 순회에서 방문 순서만 바뀌고 구조는 같다는 점을 코드로 확인한다.",
        inputExample="루트 1, 왼쪽 자식 2, 오른쪽 자식 3, 2의 자식 4와 5",
        outputExample="전위: [1, 2, 4, 5, 3]\n중위: [4, 2, 5, 1, 3]\n후위: [4, 5, 2, 3, 1]",
        representativeCode=block(
            """
            class TreeNode:
                def __init__(self, value):
                    self.value = value
                    self.left = None
                    self.right = None


            def preorder(root):
                if root is None:
                    return []

                result = [root.value]
                result.extend(preorder(root.left))
                result.extend(preorder(root.right))
                return result


            def inorder(root):
                if root is None:
                    return []

                result = inorder(root.left)
                result.append(root.value)
                result.extend(inorder(root.right))
                return result


            def postorder(root):
                if root is None:
                    return []

                result = postorder(root.left)
                result.extend(postorder(root.right))
                result.append(root.value)
                return result
            """
        ),
        traceSteps=[
            step("빈 노드 처리", "현재 노드가 없으면 더 내려가지 않고 빈 리스트를 반환한다."),
            step("방문 순서 선택", "전위, 중위, 후위 중 어떤 시점에 루트 값을 넣을지 정한다."),
            step("서브트리 결합", "왼쪽과 오른쪽 서브트리 순회 결과를 방문 순서에 맞춰 이어 붙인다."),
        ],
        blankPrompt="트리 순회는 방문 순서가 한 줄만 바뀌어도 결과가 달라진다.",
        blankSource=block(
            """
            if root is None:
                return []

            result = [root.value]
            result.extend(preorder(root.left))
            result.extend(preorder(root.right))
            return result
            """
        ),
        blankSpecs=[
            blank("b1", "if root is None:", "재귀를 멈추는 빈 노드 조건이다."),
            blank("b2", "result = [root.value]", "전위 순회에서는 루트 값을 먼저 넣는다."),
            blank("b3", "result.extend(preorder(root.right))", "오른쪽 서브트리 결과를 마지막에 붙인다."),
        ],
        parsonsPrompt="전위 순회 기준으로 빈 노드 처리 -> 루트 방문 -> 왼쪽 -> 오른쪽 순서를 복원한다.",
        parsonsSource=block(
            """
            def preorder(root):
                if root is None:
                    return []
                result = [root.value]
                result.extend(preorder(root.left))
                result.extend(preorder(root.right))
                return result
            """
        ),
        commonMistake={
            "title": "전위, 중위, 후위의 차이를 재귀 호출 순서로 바꾸는 실수",
            "whyWrong": "순회의 차이는 호출 순서가 아니라 루트 값을 결과에 넣는 시점에서 결정된다.",
        },
        bridgeSummary="트리 실전 문제에서는 각 노드를 언제 처리할지 먼저 정하고, 그 다음에 같은 재귀 뼈대를 재사용하면 된다.",
        problemTitle="이진 트리 순회 결과 구하기",
        problemDescription="이진 트리가 주어질 때 전위, 중위, 후위 순회 결과를 각각 구한다.",
        inputFormat="트리 노드 구조가 함수 인자로 주어지거나 미리 생성된다.",
        outputFormat="각 순회 결과를 리스트로 반환한다.",
        knownEdgeCases=["루트만 있는 트리", "한쪽으로만 치우친 트리", "빈 자식이 많은 트리"],
    ),
    make_entry(
        slug="graph",
        templateRel="week4/basic/03_graph_basic.py",
        title="그래프",
        aliases=["graph", "adjacency list"],
        tags=["graph", "adjacency-list", "data-structure"],
        summary="정점과 간선을 인접 리스트로 표현해 이후 탐색 알고리즘의 기반 자료구조를 만드는 단원",
        overview="그래프 단원에서는 각 정점에 연결된 이웃 목록을 어떻게 저장할지 먼저 정해 두는 것이 중요하다.",
        coreIdea="정점 수만큼 빈 리스트를 만들고, 간선을 읽으면서 출발 정점의 이웃 목록에 도착 정점을 추가한다.",
        complexityTime="O(V + E)",
        complexitySpace="O(V + E)",
        visualFocus="정점별 이웃 리스트",
        lessonTitle="인접 리스트로 그래프 표현하기",
        objective="방향/무방향 그래프 차이를 간선 추가 규칙으로 구분해 구현한다.",
        inputExample="vertices = 4\nedges = [(0, 1), (0, 2), (1, 2), (2, 3)]",
        outputExample="0 -> [1, 2]\n1 -> [0, 2]\n2 -> [0, 1, 3]\n3 -> [2]",
        representativeCode=block(
            """
            def create_graph(vertices, edges, directed=False):
                graph = {vertex: [] for vertex in range(vertices)}

                for start, end in edges:
                    graph[start].append(end)
                    if not directed:
                        graph[end].append(start)

                return graph
            """
        ),
        traceSteps=[
            step("정점 초기화", "모든 정점 번호를 키로 갖는 빈 인접 리스트를 만든다."),
            step("간선 추가", "각 간선을 읽어 출발 정점 목록에 도착 정점을 추가한다."),
            step("방향성 반영", "무방향 그래프면 반대 방향 간선도 한 번 더 추가한다."),
        ],
        blankPrompt="그래프 기본은 간선 한 개를 읽었을 때 어느 리스트를 갱신해야 하는지 아는 것이다.",
        blankSource=block(
            """
            graph = {vertex: [] for vertex in range(vertices)}

            for start, end in edges:
                graph[start].append(end)
                if not directed:
                    graph[end].append(start)

            return graph
            """
        ),
        blankSpecs=[
            blank("b1", "graph = {vertex: [] for vertex in range(vertices)}", "정점 수만큼 빈 인접 리스트를 만든다."),
            blank("b2", "graph[start].append(end)", "출발 정점에서 도착 정점을 연결한다."),
            blank("b3", "graph[end].append(start)", "무방향 그래프일 때 반대 방향도 추가한다."),
        ],
        parsonsPrompt="정점 초기화 -> 간선 추가 -> 무방향 보정 순서를 복원한다.",
        parsonsSource=block(
            """
            def create_graph(vertices, edges, directed=False):
                graph = {vertex: [] for vertex in range(vertices)}
                for start, end in edges:
                    graph[start].append(end)
                    if not directed:
                        graph[end].append(start)
                return graph
            """
        ),
        commonMistake={
            "title": "무방향 그래프인데 한쪽 간선만 추가하는 실수",
            "whyWrong": "양방향 연결이 빠지면 이후 BFS/DFS 결과와 차수가 모두 달라진다.",
        },
        bridgeSummary="그래프 실전 문제는 대부분 탐색 전에 그래프를 어떻게 저장할지부터 결정해야 풀리므로, 인접 리스트 생성이 가장 먼저다.",
        problemTitle="인접 리스트 그래프 생성",
        problemDescription="정점 수와 간선 목록이 주어질 때 인접 리스트 형태의 그래프를 만든다.",
        inputFormat="정점 개수 vertices와 간선 튜플 리스트 edges가 함수 인자로 주어진다.",
        outputFormat="각 정점의 이웃 리스트를 담은 딕셔너리를 반환한다.",
        knownEdgeCases=["간선이 없는 그래프", "방향 그래프인 경우", "정점은 있지만 연결이 끊어진 경우"],
    ),
    make_entry(
        slug="bfs",
        templateRel="week4/basic/04_bfs.py",
        title="BFS",
        aliases=["bfs", "breadth-first search"],
        tags=["graph", "bfs", "queue"],
        summary="가까운 정점부터 차례로 방문하기 위해 큐를 사용하는 그래프 탐색 단원",
        overview="BFS 단원에서는 먼저 발견한 정점을 큐에 넣고, 그 큐 순서대로 꺼내며 같은 거리에 있는 정점부터 방문한다.",
        coreIdea="시작 정점을 큐에 넣고 방문 처리한 뒤, 큐에서 꺼낸 정점의 이웃 중 아직 방문하지 않은 정점을 다시 큐 뒤에 넣는다.",
        complexityTime="O(V + E)",
        complexitySpace="O(V)",
        visualFocus="큐와 visited 집합",
        lessonTitle="큐 기반 BFS 방문 순서 만들기",
        objective="발견 즉시 방문 표시하고 큐 뒤에 넣는 BFS의 핵심 규칙을 고정한다.",
        inputExample="graph = {0: [1, 2], 1: [0, 2], 2: [0, 1, 3], 3: [2]}\nstart = 0",
        outputExample="[0, 1, 2, 3]",
        representativeCode=block(
            """
            from collections import deque


            def bfs(graph, start):
                visited = []
                queue = deque([start])
                seen = {start}

                while queue:
                    vertex = queue.popleft()
                    visited.append(vertex)

                    for neighbor in graph[vertex]:
                        if neighbor not in seen:
                            seen.add(neighbor)
                            queue.append(neighbor)

                return visited
            """
        ),
        traceSteps=[
            step("시작 정점 적재", "시작 정점을 큐와 seen 집합에 동시에 넣어 첫 방문을 기록한다."),
            step("가까운 정점 처리", "큐에서 먼저 나온 정점을 visited에 추가해 실제 방문 순서를 확정한다."),
            step("새 이웃 예약", "아직 보지 않은 이웃만 seen에 추가하고 큐 뒤에 넣어 다음 거리 레벨을 준비한다."),
        ],
        blankPrompt="BFS는 발견 순간에 seen 처리하지 않으면 같은 정점이 큐에 여러 번 들어갈 수 있다.",
        blankSource=block(
            """
            visited = []
            queue = deque([start])
            seen = {start}

            while queue:
                vertex = queue.popleft()
                visited.append(vertex)

                for neighbor in graph[vertex]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)

            return visited
            """
        ),
        blankSpecs=[
            blank("b1", "queue = deque([start])", "시작 정점을 큐에 넣는다."),
            blank("b2", "seen = {start}", "시작 정점을 이미 본 정점으로 기록한다."),
            blank("b3", "queue.append(neighbor)", "새로 발견한 이웃을 다음 방문 후보로 넣는다."),
        ],
        parsonsPrompt="큐 초기화 -> popleft -> 새 이웃 append 순서를 복원한다.",
        parsonsSource=block(
            """
            def bfs(graph, start):
                visited = []
                queue = deque([start])
                seen = {start}
                while queue:
                    vertex = queue.popleft()
                    visited.append(vertex)
                    for neighbor in graph[vertex]:
                        if neighbor not in seen:
                            seen.add(neighbor)
                            queue.append(neighbor)
                return visited
            """
        ),
        commonMistake={
            "title": "큐에서 꺼낸 뒤에야 방문 체크하는 실수",
            "whyWrong": "같은 정점이 여러 부모를 통해 중복 enqueue되어 BFS 순서와 비용이 불필요하게 늘어난다.",
        },
        bridgeSummary="최단 거리 성질이 중요한 실전 그래프 문제는 대부분 BFS의 '먼저 발견한 순서대로 큐 처리' 규칙에서 출발한다.",
        problemTitle="그래프 BFS 순회",
        problemDescription="시작 정점에서 가까운 정점부터 차례로 방문하는 BFS 순서를 구한다.",
        inputFormat="인접 리스트 그래프와 시작 정점이 함수 인자로 주어진다.",
        outputFormat="방문 순서를 리스트로 반환한다.",
        knownEdgeCases=["시작 정점만 있는 경우", "사이클이 있는 그래프", "연결되지 않은 정점이 있는 그래프"],
    ),
    make_entry(
        slug="dfs",
        templateRel="week4/basic/05_dfs.py",
        title="DFS",
        aliases=["dfs", "depth-first search"],
        tags=["graph", "dfs", "recursion"],
        summary="한 방향으로 끝까지 내려갔다가 돌아오는 깊이 우선 탐색의 재귀 패턴을 익히는 단원",
        overview="DFS 단원에서는 현재 정점을 방문한 뒤 아직 보지 않은 이웃으로 재귀 호출해 깊이 우선으로 내려가는 구조를 익힌다.",
        coreIdea="현재 정점을 visited에 추가하고, 인접 정점 중 아직 없는 정점만 골라 같은 함수를 재귀 호출한다.",
        complexityTime="O(V + E)",
        complexitySpace="O(V)",
        visualFocus="재귀 호출 스택과 visited 순서",
        lessonTitle="재귀 기반 DFS 방문 순서 만들기",
        objective="현재 방문 처리와 다음 이웃으로 내려가는 재귀 호출 순서를 안정적으로 유지한다.",
        inputExample="graph = {0: [1, 2], 1: [0, 2], 2: [0, 1, 3], 3: [2]}\nstart = 0",
        outputExample="[0, 1, 2, 3]",
        representativeCode=block(
            """
            def dfs(graph, start, visited=None):
                if visited is None:
                    visited = []

                visited.append(start)

                for neighbor in graph[start]:
                    if neighbor not in visited:
                        dfs(graph, neighbor, visited)

                return visited
            """
        ),
        traceSteps=[
            step("방문 리스트 준비", "첫 호출에서는 visited를 새 리스트로 만들고 이후 호출과 공유한다."),
            step("현재 정점 방문", "현재 정점을 visited에 추가해 중복 방문을 막는다."),
            step("깊게 내려가기", "아직 방문하지 않은 이웃을 만나면 그 이웃으로 재귀 호출한다."),
        ],
        blankPrompt="DFS는 현재 정점을 먼저 기록한 뒤 아직 방문하지 않은 이웃으로 내려가야 한다.",
        blankSource=block(
            """
            if visited is None:
                visited = []

            visited.append(start)

            for neighbor in graph[start]:
                if neighbor not in visited:
                    dfs(graph, neighbor, visited)

            return visited
            """
        ),
        blankSpecs=[
            blank("b1", "if visited is None:", "첫 호출에서만 방문 리스트를 만든다."),
            blank("b2", "visited.append(start)", "현재 정점을 방문 처리한다."),
            blank("b3", "dfs(graph, neighbor, visited)", "방문하지 않은 이웃으로 재귀 호출한다."),
        ],
        parsonsPrompt="초기화 -> 현재 방문 -> 재귀 호출 순서를 복원한다.",
        parsonsSource=block(
            """
            def dfs(graph, start, visited=None):
                if visited is None:
                    visited = []
                visited.append(start)
                for neighbor in graph[start]:
                    if neighbor not in visited:
                        dfs(graph, neighbor, visited)
                return visited
            """
        ),
        commonMistake={
            "title": "재귀 호출 전에 현재 정점을 visited에 넣지 않는 실수",
            "whyWrong": "사이클이 있는 그래프에서 같은 정점으로 계속 되돌아와 무한 재귀가 발생할 수 있다.",
        },
        bridgeSummary="실전 DFS 문제에서는 재귀 함수가 '현재 정점에서 할 일'과 '다음 정점으로 내려갈 조건' 두 가지만 갖고 있는지 먼저 확인하면 된다.",
        problemTitle="그래프 DFS 순회",
        problemDescription="시작 정점에서 깊이 우선으로 그래프를 탐색한 방문 순서를 구한다.",
        inputFormat="인접 리스트 그래프와 시작 정점이 함수 인자로 주어진다.",
        outputFormat="방문 순서를 리스트로 반환한다.",
        knownEdgeCases=["사이클이 있는 그래프", "이웃이 없는 정점", "연결 요소가 여러 개인 그래프"],
    ),
    make_entry(
        slug="topological-sort",
        templateRel="week4/basic/06_topological_sort.py",
        title="위상정렬",
        aliases=["topological sort", "kahn"],
        tags=["graph", "dag", "topological-sort"],
        summary="진입 차수가 0인 정점부터 처리해 선행 관계가 있는 작업의 순서를 정하는 단원",
        overview="위상정렬 단원에서는 '지금 바로 할 수 있는 작업'을 진입 차수 0인 정점으로 모델링해 순서를 만든다.",
        coreIdea="그래프와 진입 차수를 만든 뒤, 진입 차수 0인 정점만 큐에 넣어 하나씩 꺼내며 후속 정점의 차수를 감소시킨다.",
        complexityTime="O(V + E)",
        complexitySpace="O(V + E)",
        visualFocus="indegree 배열과 큐",
        lessonTitle="진입 차수로 위상 정렬 구현하기",
        objective="indegree 갱신과 0차수 큐 삽입 시점을 정확히 맞춘다.",
        inputExample="vertices = 4\nedges = [(0, 1), (0, 2), (1, 3)]",
        outputExample="[0, 1, 2, 3]",
        representativeCode=block(
            """
            from collections import deque


            def topological_sort(vertices, edges):
                graph = {vertex: [] for vertex in range(vertices)}
                indegree = [0] * vertices

                for start, end in edges:
                    graph[start].append(end)
                    indegree[end] += 1

                queue = deque(vertex for vertex in range(vertices) if indegree[vertex] == 0)
                result = []

                while queue:
                    vertex = queue.popleft()
                    result.append(vertex)

                    for neighbor in graph[vertex]:
                        indegree[neighbor] -= 1
                        if indegree[neighbor] == 0:
                            queue.append(neighbor)

                return result
            """
        ),
        traceSteps=[
            step("차수 계산", "모든 간선을 돌며 각 정점의 진입 차수를 센다."),
            step("즉시 가능한 작업 적재", "현재 진입 차수가 0인 정점만 큐에 넣어 바로 처리 가능한 작업을 모은다."),
            step("후속 작업 해금", "정점을 하나 처리할 때마다 연결된 이웃의 진입 차수를 줄이고, 0이 되면 큐에 추가한다."),
        ],
        blankPrompt="위상정렬은 그래프와 indegree를 같이 관리해야 올바른 순서가 나온다.",
        blankSource=block(
            """
            graph = {vertex: [] for vertex in range(vertices)}
            indegree = [0] * vertices

            for start, end in edges:
                graph[start].append(end)
                indegree[end] += 1

            queue = deque(vertex for vertex in range(vertices) if indegree[vertex] == 0)
            result = []

            while queue:
                vertex = queue.popleft()
                result.append(vertex)

                for neighbor in graph[vertex]:
                    indegree[neighbor] -= 1
                    if indegree[neighbor] == 0:
                        queue.append(neighbor)

            return result
            """
        ),
        blankSpecs=[
            blank("b1", "indegree = [0] * vertices", "각 정점의 진입 차수를 저장할 배열이다."),
            blank("b2", "indegree[end] += 1", "간선을 읽으며 도착 정점의 차수를 올린다."),
            blank("b3", "if indegree[neighbor] == 0:", "선행 작업이 모두 끝난 정점만 큐에 넣는다."),
        ],
        parsonsPrompt="차수 계산 -> 0차수 큐 적재 -> 후속 차수 감소 순서를 복원한다.",
        parsonsSource=block(
            """
            def topological_sort(vertices, edges):
                graph = {vertex: [] for vertex in range(vertices)}
                indegree = [0] * vertices
                for start, end in edges:
                    graph[start].append(end)
                    indegree[end] += 1
                queue = deque(vertex for vertex in range(vertices) if indegree[vertex] == 0)
                result = []
                while queue:
                    vertex = queue.popleft()
                    result.append(vertex)
                    for neighbor in graph[vertex]:
                        indegree[neighbor] -= 1
                        if indegree[neighbor] == 0:
                            queue.append(neighbor)
                return result
            """
        ),
        commonMistake={
            "title": "진입 차수가 0이 된 정점을 바로 큐에 넣지 않는 실수",
            "whyWrong": "해금된 작업을 놓치면 일부 정점이 결과에 들어가지 않거나 순서가 틀어진다.",
        },
        bridgeSummary="선행 관계 문제를 만나면 먼저 '지금 바로 할 수 있는 정점'을 무엇으로 판단할지 정하고, 그 기준이 바로 indegree 0인지 확인하면 된다.",
        problemTitle="작업 순서를 위한 위상 정렬",
        problemDescription="선행 관계가 있는 작업 그래프에서 가능한 수행 순서 하나를 구한다.",
        inputFormat="정점 개수와 방향 간선 목록이 함수 인자로 주어진다.",
        outputFormat="위상 정렬 순서를 리스트로 반환한다.",
        knownEdgeCases=["간선이 없는 경우", "여러 개의 시작 정점이 있는 경우", "긴 선행 체인이 있는 경우"],
    ),
    make_entry(
        slug="dynamic-programming",
        templateRel="week5/basic/02_dp_stairs.py",
        title="DP",
        aliases=["dynamic programming", "stairs"],
        tags=["dp", "bottom-up", "recurrence"],
        summary="작은 문제의 답을 저장해 점화식으로 큰 문제를 차례로 해결하는 동적 프로그래밍 단원",
        overview="DP 단원에서는 부분 문제 정의, 초기값, 점화식, 계산 순서를 고정해 테이블을 채우는 사고방식을 익힌다.",
        coreIdea="dp[i]를 i번째 계단까지 오르는 방법 수로 정의하고, dp[i] = dp[i - 1] + dp[i - 2]를 작은 값부터 계산한다.",
        complexityTime="O(n)",
        complexitySpace="O(n)",
        visualFocus="dp 테이블",
        lessonTitle="점화식으로 계단 오르기 경우의 수 구하기",
        objective="부분 문제 정의 -> 초기값 -> 점화식 -> 순차 계산 순서를 그대로 구현한다.",
        inputExample="n = 4",
        outputExample="5",
        representativeCode=block(
            """
            def climb_stairs(n):
                if n <= 2:
                    return n

                dp = [0] * (n + 1)
                dp[1] = 1
                dp[2] = 2

                for step in range(3, n + 1):
                    dp[step] = dp[step - 1] + dp[step - 2]

                return dp[n]
            """
        ),
        traceSteps=[
            step("작은 입력 처리", "n이 1 또는 2인 경우는 바로 답을 반환해 점화식 없이 끝낸다."),
            step("초기값 배치", "dp[1]과 dp[2]를 채워 이후 계산의 기준을 만든다."),
            step("점화식 채우기", "3부터 n까지 올라가며 직전 두 값의 합으로 현재 값을 채운다."),
        ],
        blankPrompt="DP는 점화식보다 먼저 dp[i]의 의미와 초기값을 정확히 잡아야 한다.",
        blankSource=block(
            """
            if n <= 2:
                return n

            dp = [0] * (n + 1)
            dp[1] = 1
            dp[2] = 2

            for step in range(3, n + 1):
                dp[step] = dp[step - 1] + dp[step - 2]

            return dp[n]
            """
        ),
        blankSpecs=[
            blank("b1", "dp = [0] * (n + 1)", "계단별 경우의 수를 저장할 테이블을 만든다."),
            blank("b2", "dp[2] = 2", "두 번째 계단의 초기값을 채운다."),
            blank("b3", "dp[step] = dp[step - 1] + dp[step - 2]", "점화식으로 현재 계단 값을 계산한다."),
        ],
        parsonsPrompt="초기값 설정 -> 점화식 반복 -> 최종 반환 순서를 복원한다.",
        parsonsSource=block(
            """
            def climb_stairs(n):
                if n <= 2:
                    return n
                dp = [0] * (n + 1)
                dp[1] = 1
                dp[2] = 2
                for step in range(3, n + 1):
                    dp[step] = dp[step - 1] + dp[step - 2]
                return dp[n]
            """
        ),
        commonMistake={
            "title": "점화식부터 쓰고 초기값을 나중에 채우는 실수",
            "whyWrong": "dp[1], dp[2]가 정해지지 않으면 이후 모든 값이 잘못 전파된다.",
        },
        bridgeSummary="실전 DP 문제는 'dp[i]가 정확히 무엇을 뜻하는가'를 한 줄로 먼저 정의하면 점화식과 초기값이 훨씬 자연스럽게 나온다.",
        problemTitle="계단 오르기 경우의 수",
        problemDescription="한 번에 1칸 또는 2칸씩 오를 수 있을 때 n번째 계단까지 도달하는 방법 수를 구한다.",
        inputFormat="계단 수 n이 함수 인자로 주어진다.",
        outputFormat="n번째 계단까지 오르는 방법 수를 반환한다.",
        knownEdgeCases=["n = 1", "n = 2", "큰 n에서 반복 계산이 필요한 경우"],
    ),
    make_entry(
        slug="greedy",
        templateRel="week5/basic/04_greedy_meeting.py",
        title="그리디",
        aliases=["greedy", "meeting room"],
        tags=["greedy", "interval", "sorting"],
        summary="지금 당장 가장 좋은 선택을 반복해 전체 해를 만드는 그리디 전략을 회의실 배정으로 익히는 단원",
        overview="그리디 단원에서는 한 번의 선택이 다음 선택 가능성을 최대화하는 기준이 무엇인지 찾는 훈련을 한다.",
        coreIdea="종료 시간이 가장 빠른 회의부터 정렬하고, 직전에 선택한 회의가 끝난 뒤 시작하는 회의만 차례로 고른다.",
        complexityTime="O(n log n)",
        complexitySpace="O(n)",
        visualFocus="마지막 선택 회의의 종료 시간",
        lessonTitle="종료 시간이 빠른 회의를 먼저 선택하기",
        objective="정렬 기준과 선택 조건을 고정해 최대 회의 수를 놓치지 않는 그리디 흐름을 익힌다.",
        inputExample="meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 8), (5, 9)]",
        outputExample="2개\n[(1, 4), (5, 7)]",
        representativeCode=block(
            """
            def select_meetings(meetings):
                if not meetings:
                    return 0, []

                sorted_meetings = sorted(meetings, key=lambda meeting: (meeting[1], meeting[0]))
                selected = [sorted_meetings[0]]
                last_end_time = sorted_meetings[0][1]

                for start, end in sorted_meetings[1:]:
                    if start >= last_end_time:
                        selected.append((start, end))
                        last_end_time = end

                return len(selected), selected
            """
        ),
        traceSteps=[
            step("빈 입력 처리", "회의가 없으면 바로 0개와 빈 목록을 반환한다."),
            step("기준 정렬", "종료 시간이 빠른 회의부터 정렬해 다음 선택 여지를 최대화한다."),
            step("가능한 회의만 선택", "현재 시작 시간이 마지막 종료 시간 이상인 회의만 고르고 기준 종료 시간을 갱신한다."),
        ],
        blankPrompt="그리디는 어떤 기준으로 정렬하고 무엇을 비교해 선택할지 분명해야 한다.",
        blankSource=block(
            """
            if not meetings:
                return 0, []

            sorted_meetings = sorted(meetings, key=lambda meeting: (meeting[1], meeting[0]))
            selected = [sorted_meetings[0]]
            last_end_time = sorted_meetings[0][1]

            for start, end in sorted_meetings[1:]:
                if start >= last_end_time:
                    selected.append((start, end))
                    last_end_time = end

            return len(selected), selected
            """
        ),
        blankSpecs=[
            blank("b1", "sorted_meetings = sorted(meetings, key=lambda meeting: (meeting[1], meeting[0]))", "종료 시간이 빠른 순서로 회의를 정렬한다."),
            blank("b2", "if start >= last_end_time:", "이전 회의가 끝난 뒤 시작하는지 확인한다."),
            blank("b3", "last_end_time = end", "새로 선택한 회의의 종료 시간을 기준으로 갱신한다."),
        ],
        parsonsPrompt="정렬 -> 첫 회의 선택 -> 가능한 회의만 추가 순서를 복원한다.",
        parsonsSource=block(
            """
            def select_meetings(meetings):
                if not meetings:
                    return 0, []
                sorted_meetings = sorted(meetings, key=lambda meeting: (meeting[1], meeting[0]))
                selected = [sorted_meetings[0]]
                last_end_time = sorted_meetings[0][1]
                for start, end in sorted_meetings[1:]:
                    if start >= last_end_time:
                        selected.append((start, end))
                        last_end_time = end
                return len(selected), selected
            """
        ),
        commonMistake={
            "title": "시작 시간이 빠른 회의부터 고르는 실수",
            "whyWrong": "그리디 기준이 잘못되면 이후에 더 많은 회의를 배정할 기회를 놓친다.",
        },
        bridgeSummary="그리디 문제에서는 먼저 '이 선택이 다음 선택 가능성을 왜 가장 많이 남기는가'를 설명할 수 있어야 구현도 흔들리지 않는다.",
        problemTitle="회의실 최대 배정",
        problemDescription="하나의 회의실에 겹치지 않게 최대한 많은 회의를 배정한다.",
        inputFormat="(시작 시간, 종료 시간) 튜플 리스트가 함수 인자로 주어진다.",
        outputFormat="배정된 회의 개수와 선택된 회의 리스트를 반환한다.",
        knownEdgeCases=["회의가 없는 경우", "끝나는 시간이 같은 회의가 있는 경우", "서로 겹치지 않는 회의만 있는 경우"],
    ),
]


def main() -> None:
    for entry in ALGORITHMS:
        validate_entry(entry)

    for entry in ALGORITHMS:
        bundle_dir = ALGORITHMS_DIR / entry["slug"]
        bundle_dir.mkdir(parents=True, exist_ok=True)
        write_json(bundle_dir / "concept.json", build_concept(entry))
        write_json(bundle_dir / "lesson.json", build_lesson(entry))
        write_json(bundle_dir / "problem.json", build_problem(entry))

    print(f"Generated and validated {len(ALGORITHMS)} algorithm bundles.")


if __name__ == "__main__":
    main()
