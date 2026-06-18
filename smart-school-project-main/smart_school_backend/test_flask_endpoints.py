"""HTTP-like smoke test using Flask's test client.

This avoids binding a real port, so it works even when sockets are blocked.
"""
from __future__ import annotations

import json
import os
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QUIZ_FORCE_FALLBACK", "1")

try:
    import werkzeug
except ImportError:  # pragma: no cover
    werkzeug = None
else:
    if not hasattr(werkzeug, "__version__"):
        try:
            werkzeug.__version__ = pkg_version("werkzeug")
        except Exception:
            werkzeug.__version__ = "unknown"

from backend.api import quiz


def main() -> None:
    app = quiz.build_flask_app()
    client = app.test_client()

    gen_payload = {
        "paragraph": (
            "Chlorophyll inside chloroplasts captures light energy to power "
            "photosynthesis, producing glucose and oxygen from water and carbon dioxide."
        ),
        "num_questions": 4,
    }
    gen_resp = client.post("/api/generate-quiz", json=gen_payload)
    if gen_resp.status_code != 200:
        raise SystemExit(f"/api/generate-quiz failed: {gen_resp.status_code} {gen_resp.data}")
    gen_json = gen_resp.get_json()

    submit_payload = {
        "quiz_id": gen_json.get("quiz_id"),
        "student_name": "TestClient",
        "student_id": "TC001",
        "answers": gen_json.get("answer_key", []),
        "answer_key": gen_json.get("answer_key", []),
    }
    sub_resp = client.post("/api/submit-quiz", json=submit_payload)
    if sub_resp.status_code != 200:
        raise SystemExit(f"/api/submit-quiz failed: {sub_resp.status_code} {sub_resp.data}")

    attendance = client.get("/api/attendance")
    teacher = client.get("/api/teacher_status")
    chat = client.post("/api/chat", json={"message": "How do quizzes work?"})

    for label, resp in ("attendance", attendance), ("teacher_status", teacher), ("chat", chat):
        if resp.status_code != 200:
            raise SystemExit(f"/{label} failed: {resp.status_code} {resp.data}")

    output = {
        "generate_status": gen_resp.status_code,
        "generate_keys": list(gen_json.keys()),
        "num_mcqs": len(gen_json.get("mcqs", [])),
        "submit_response": sub_resp.get_json(),
        "attendance": attendance.get_json(),
        "teacher_status": teacher.get_json(),
        "chat": chat.get_json(),
        "results_csv": str((ROOT / "backend" / "quiz_results.csv").resolve()),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
