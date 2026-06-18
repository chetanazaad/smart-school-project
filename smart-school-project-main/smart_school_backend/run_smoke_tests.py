"""Offline smoke test for quiz generation and scoring.

This script exercises backend.api.quiz without starting HTTP servers.
It generates a quiz, prints the questions, simulates a submission,
and appends a result row to backend/quiz_results.csv.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api import quiz


def main() -> None:
    os.environ.setdefault("QUIZ_FORCE_FALLBACK", "1")
    paragraph = (
        "Photosynthesis is the process by which plants use chlorophyll inside "
        "chloroplasts to convert light energy into chemical energy, producing "
        "glucose and oxygen from carbon dioxide and water."
    )
    num_qs = 5

    mcqs = quiz.safe_generate(paragraph, num_qs)
    mcqs = quiz.ensure_mcqs_have_explanations(mcqs)
    answer_key = [int(m.get("answer_index", 0)) for m in mcqs]

    # Simulate a student submission using the correct answers for a perfect score.
    student_answers = answer_key[:]
    score = sum(int(student_answers[i] == answer_key[i]) for i in range(len(answer_key)))

    quiz.persist_result("SmokeTest", "SMK001", score, len(answer_key), quiz_id="smoke-run")

    payload = {
        "paragraph": paragraph,
        "num_questions": num_qs,
        "mcqs": mcqs,
        "answer_key": answer_key,
        "student_answers": student_answers,
        "score": score,
        "total": len(answer_key),
        "results_csv": str((Path(__file__).parents[0] / "quiz_results.csv").resolve()),
    }

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
