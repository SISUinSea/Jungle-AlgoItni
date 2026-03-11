from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


class ContentService:
    def __init__(self, algorithms_dir: Path) -> None:
        self.algorithms_dir = algorithms_dir

    def list_algorithms(self) -> list[dict]:
        algorithms: list[dict] = []
        if not self.algorithms_dir.exists():
            return algorithms

        for algorithm_dir in sorted(path for path in self.algorithms_dir.iterdir() if path.is_dir()):
            concept = self._load_json(algorithm_dir / "concept.json")
            if concept is None:
                continue
            algorithms.append(concept["meta"])

        return algorithms

    def get_algorithm_bundle(self, slug: str) -> dict | None:
        concept = self._load_json(self.algorithms_dir / slug / "concept.json")
        lesson = self._load_json(self.algorithms_dir / slug / "lesson.json")
        problem = self._load_json(self.algorithms_dir / slug / "problem.json")

        if concept is None or lesson is None or problem is None:
            return None

        return {
            "meta": concept["meta"],
            "concept": concept,
            "lesson": lesson,
            "problem": problem,
        }

    def find_bundle_by_problem_ref(self, problem_source: str, problem_ref: str) -> dict | None:
        for algorithm in self.list_algorithms():
            bundle = self.get_algorithm_bundle(algorithm["slug"])
            if bundle is None:
                continue
            problem = bundle["problem"]
            if (
                problem.get("problemSource") == problem_source
                and problem.get("problemIdOrUrl") == problem_ref
            ):
                return bundle
        return None

    @lru_cache(maxsize=64)
    def _load_json(self, path: Path) -> dict | list | None:
        if not path.exists():
            return None
        with path.open(encoding="utf-8") as file:
            return json.load(file)
