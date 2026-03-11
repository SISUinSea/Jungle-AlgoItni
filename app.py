from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

from services.content_service import ContentService


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(__name__)
    content_service = ContentService(BASE_DIR / "content" / "algorithms")

    @app.get("/")
    def index():
        return render_template("index.html", algorithms=content_service.list_algorithms())

    @app.get("/algorithms/<slug>")
    def concept_page(slug: str):
        bundle = content_service.get_algorithm_bundle(slug)
        if bundle is None:
            abort(404)
        return render_template(
            "concept.html",
            algorithm=bundle["meta"],
            concept=bundle["concept"],
            lesson=bundle["lesson"],
            problem=bundle["problem"],
        )

    @app.get("/algorithms/<slug>/lesson")
    def lesson_page(slug: str):
        bundle = content_service.get_algorithm_bundle(slug)
        if bundle is None:
            abort(404)
        return render_template(
            "lesson.html",
            algorithm=bundle["meta"],
            lesson=bundle["lesson"],
        )

    @app.get("/algorithms/<slug>/problem")
    def problem_page(slug: str):
        bundle = content_service.get_algorithm_bundle(slug)
        if bundle is None:
            abort(404)
        return render_template(
            "problem.html",
            algorithm=bundle["meta"],
            problem=bundle["problem"],
        )

    @app.post("/api/counterexample")
    def counterexample_api():
        payload = request.get_json(silent=True) or {}
        problem_id_or_url = payload.get("problemIdOrUrl", "").strip()
        user_code = payload.get("userCode", "").strip()

        if not problem_id_or_url:
            return jsonify({"found": False, "message": "problemIdOrUrl is required"}), 400
        if not user_code:
            return jsonify({"found": False, "message": "userCode is required"}), 400

        bundle = content_service.find_bundle_by_problem_ref(problem_id_or_url)
        if bundle is None:
            return jsonify({"found": False, "message": "Unknown problemIdOrUrl"}), 404

        return jsonify({"found": False, "message": "Not implemented yet"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
