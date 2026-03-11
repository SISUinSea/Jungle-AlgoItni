from pathlib import Path

import json

from flask import Flask, Response, abort, jsonify, render_template, request, stream_with_context

from services.content_service import ContentService
from services.lesson_chat_service import LessonChatError, LessonChatService


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(__name__)
    content_service = ContentService(BASE_DIR / "content" / "algorithms")
    lesson_chat_service = LessonChatService()

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
        problem_source = payload.get("problemSource", "").strip()
        problem_id_or_url = payload.get("problemIdOrUrl", "").strip()
        user_code = payload.get("userCode", "").strip()

        if not problem_source:
            return jsonify({"message": "problemSource is required"}), 400
        if not problem_id_or_url:
            return jsonify({"message": "problemIdOrUrl is required"}), 400
        if not user_code:
            return jsonify({"message": "userCode is required"}), 400

        bundle = content_service.find_bundle_by_problem_ref(problem_source, problem_id_or_url)
        if bundle is None:
            return jsonify({"message": "Unknown problemIdOrUrl"}), 404

        return (
            jsonify(
                {
                    "message": (
                        "Counterexample pipeline is not implemented in "
                        "codex/foundation-contracts."
                    )
                }
            ),
            501,
        )

    @app.post("/api/lesson-chat")
    def lesson_chat_api():
        payload = request.get_json(silent=True) or {}
        algorithm_slug = payload.get("algorithmSlug", "").strip()
        question = payload.get("question", "").strip()

        if not algorithm_slug:
            return jsonify({"message": "algorithmSlug is required"}), 400
        if not question:
            return jsonify({"message": "question is required"}), 400

        bundle = content_service.get_algorithm_bundle(algorithm_slug)
        if bundle is None:
            return jsonify({"message": "Unknown algorithmSlug"}), 404
        if not lesson_chat_service.configured:
            return jsonify({"message": "Lesson chat is disabled until OPENAI_API_KEY is configured"}), 503

        def generate():
            try:
                for delta in lesson_chat_service.stream_answer(
                    bundle["meta"],
                    bundle["lesson"],
                    question,
                ):
                    payload = json.dumps({"delta": delta}, ensure_ascii=False)
                    yield f"event: chunk\ndata: {payload}\n\n"
                yield "event: done\ndata: {}\n\n"
            except LessonChatError as exc:
                payload = json.dumps({"message": str(exc)}, ensure_ascii=False)
                yield f"event: error\ndata: {payload}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
