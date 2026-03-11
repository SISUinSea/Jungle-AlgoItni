from __future__ import annotations

import json
import os
from typing import Generator
from urllib import error, request


class LessonChatError(Exception):
    pass


class LessonChatService:
    api_url = "https://api.openai.com/v1/responses"

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.model = os.environ.get("OPENAI_LESSON_MODEL", "gpt-4.1-mini").strip()

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def stream_answer(
        self,
        algorithm: dict,
        lesson: dict,
        question: str,
    ) -> Generator[str, None, None]:
        if not self.configured:
            raise LessonChatError("OPENAI_API_KEY is not configured")

        payload = {
            "model": self.model,
            "instructions": self._build_instructions(algorithm, lesson),
            "input": question,
            "stream": True,
        }
        req = request.Request(
            self.api_url,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            data=json.dumps(payload).encode("utf-8"),
        )

        try:
            with request.urlopen(req, timeout=90) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data = line[5:].strip()
                    if data == "[DONE]":
                        break

                    event = json.loads(data)
                    if event.get("type") == "response.output_text.delta":
                        delta = event.get("delta", "")
                        if delta:
                            yield delta
                    elif event.get("type") == "error":
                        message = event.get("message") or "Lesson chat request failed"
                        raise LessonChatError(message)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(detail)
                message = payload.get("error", {}).get("message") or detail
            except json.JSONDecodeError:
                message = detail or str(exc)
            raise LessonChatError(message) from exc
        except error.URLError as exc:
            raise LessonChatError(str(exc.reason)) from exc

    def _build_instructions(self, algorithm: dict, lesson: dict) -> str:
        lesson_snapshot = {
            "title": lesson.get("title"),
            "objective": lesson.get("objective"),
            "representativeCode": lesson.get("representativeCode"),
            "traceSteps": lesson.get("traceSteps"),
            "commonMistake": lesson.get("commonMistake"),
            "bridgeSummary": lesson.get("bridgeSummary"),
        }
        return (
            "You are an algorithm tutor embedded in a lesson page. "
            "Answer in Korean unless the user explicitly asks otherwise. "
            "Be concise, concrete, and explanation-first. "
            "Prioritize the provided lesson content. "
            "If the user asks beyond the lesson, answer briefly and clearly mark it as extra context.\n\n"
            f"Algorithm meta: {json.dumps(algorithm, ensure_ascii=False)}\n"
            f"Lesson snapshot: {json.dumps(lesson_snapshot, ensure_ascii=False)}"
        )
