import json
from pathlib import Path

import pytest

from app import create_app


REPO_ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS_DIR = REPO_ROOT / "content" / "algorithms"


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_algorithm_content_contracts_are_present():
    algorithm_dirs = sorted(path for path in ALGORITHMS_DIR.iterdir() if path.is_dir())
    assert algorithm_dirs

    banned_terms = {"example_id", "whiteboardExercise"}

    for algorithm_dir in algorithm_dirs:
        slug = algorithm_dir.name
        concept = load_json(algorithm_dir / "concept.json")
        lesson = load_json(algorithm_dir / "lesson.json")
        problem = load_json(algorithm_dir / "problem.json")

        assert concept["meta"]["slug"] == slug
        assert lesson["algorithmSlug"] == slug
        assert problem["algorithmSlug"] == slug

        assert concept["overview"]
        assert concept["coreIdea"]
        assert concept["complexity"]["time"]
        assert concept["complexity"]["space"]
        assert concept["visualNotes"]

        assert lesson["codeLanguage"] == "python"
        assert lesson["representativeCode"]
        assert lesson["traceSteps"]
        assert lesson["blankExercise"]["blanks"]
        assert lesson["parsonsExercise"]["answerOrder"]
        assert lesson["bridgeSummary"]

        assert problem["problemSource"]
        assert problem["problemIdOrUrl"]
        assert problem["starterCode"]
        assert problem["knownEdgeCases"]

        bundle_text = json.dumps(
            {"concept": concept, "lesson": lesson, "problem": problem},
            ensure_ascii=False,
        )
        for term in banned_terms:
            assert term not in bundle_text


def test_problem_refs_are_unique():
    refs = set()

    for algorithm_dir in sorted(path for path in ALGORITHMS_DIR.iterdir() if path.is_dir()):
        problem = load_json(algorithm_dir / "problem.json")
        problem_ref = (problem["problemSource"], problem["problemIdOrUrl"])
        assert problem_ref not in refs
        refs.add(problem_ref)


def test_foundation_pages_render(client):
    for path in [
        "/",
        "/algorithms/binary-search",
        "/algorithms/binary-search/lesson",
        "/algorithms/binary-search/problem",
    ]:
        response = client.get(path)
        assert response.status_code == 200


def test_problem_links_are_locked_until_lesson_completion(client):
    index_response = client.get("/")
    concept_response = client.get("/algorithms/binary-search")
    lesson_response = client.get("/algorithms/binary-search/lesson")

    index_html = index_response.get_data(as_text=True)
    concept_html = concept_response.get_data(as_text=True)
    lesson_html = lesson_response.get_data(as_text=True)

    assert 'data-problem-link' in index_html
    assert 'data-problem-link' in concept_html
    assert 'data-problem-link' in lesson_html

    assert 'href="/algorithms/binary-search/problem"' not in index_html
    assert 'href="/algorithms/binary-search/problem"' not in concept_html
    assert 'href="/algorithms/binary-search/problem"' not in lesson_html


def test_problem_page_contains_client_side_lesson_guard(client):
    response = client.get("/algorithms/binary-search/problem")
    html = response.get_data(as_text=True)

    assert 'data-problem-root' in html
    assert 'data-lesson-url="/algorithms/binary-search/lesson"' in html


def test_missing_algorithm_returns_404(client):
    response = client.get("/algorithms/missing-slug")
    assert response.status_code == 404


def test_counterexample_requires_problem_source(client):
    response = client.post(
        "/api/counterexample",
        json={"problemIdOrUrl": "binary-search-demo-problem", "userCode": "print(1)"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "problemSource is required"}


def test_counterexample_requires_problem_ref(client):
    response = client.post(
        "/api/counterexample",
        json={"problemSource": "internal-demo", "userCode": "print(1)"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "problemIdOrUrl is required"}


def test_counterexample_requires_user_code(client):
    response = client.post(
        "/api/counterexample",
        json={
            "problemSource": "internal-demo",
            "problemIdOrUrl": "binary-search-demo-problem",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "userCode is required"}


def test_counterexample_rejects_unknown_problem(client):
    response = client.post(
        "/api/counterexample",
        json={
            "problemSource": "internal-demo",
            "problemIdOrUrl": "missing-problem",
            "userCode": "print(1)",
        },
    )

    assert response.status_code == 404
    assert response.get_json() == {"message": "Unknown problemIdOrUrl"}


def test_counterexample_returns_not_implemented_placeholder(client):
    response = client.post(
        "/api/counterexample",
        json={
            "problemSource": "internal-demo",
            "problemIdOrUrl": "binary-search-demo-problem",
            "userCode": "print(1)",
        },
    )

    assert response.status_code == 501
    assert response.get_json() == {
        "message": "Counterexample pipeline is not implemented in codex/foundation-contracts."
    }


def test_progress_contract_uses_stage_attempts():
    progress_js = (REPO_ROOT / "static" / "js" / "progress.js").read_text(encoding="utf-8")
    problem_js = (REPO_ROOT / "static" / "js" / "problem.js").read_text(encoding="utf-8")

    assert 'const ALGOITNI_PROGRESS_PREFIX = "algostep_progress::";' in progress_js
    assert 'const ALGOITNI_LAST_ALGORITHM_KEY = "algostep_last_algorithm";' in progress_js
    assert "blank: 0" in progress_js
    assert "parsons: 0" in progress_js
    assert "normalizeAttempts" in progress_js
    assert "setProblemLinkState" in progress_js
    assert "window.location.replace(lessonUrl);" in problem_js
    assert "!progress.lessonCompleted" in problem_js
