#!/usr/bin/env python3
"""
Lightweight quiz API wrapper for Yug's quiz generator.

Exposes POST /api/quiz with JSON { "paragraph": "...", "num_questions": 2 }
and returns { "mcqs": [ { question, options, answer_index }, ... ] }

This script will try to use Flask if available. If Flask is not installed,
it falls back to a small built-in HTTP server so you can run it without extra deps.
"""

import json
import os
import sys
import threading
from pathlib import Path
import uuid
import csv
from datetime import datetime

# Lazy loader for the heavier generator to avoid import-time crashes
generate_mcqs = None
_generator_tried = False

def safe_generate(paragraph, num_qs=3):
    """Try to call the real generator if available; otherwise use the tiny fallback.
    This function will attempt to import the real generator once and cache the result.
    Any import or runtime errors are caught and the fallback is used instead.
    """
    if os.environ.get('QUIZ_FORCE_FALLBACK') == '1':
        return fallback_generate_mcqs(paragraph, num_qs)
    global generate_mcqs, _generator_tried
    if generate_mcqs is None and not _generator_tried:
        _generator_tried = True
        try:
            # try package-style imports
            from backend.ai.quiz_generator_rag_tfidf import generate_mcqs as real_gen
            generate_mcqs = real_gen
        except Exception:
            try:
                from ai.quiz_generator_rag_tfidf import generate_mcqs as real_gen
                generate_mcqs = real_gen
            except Exception:
                try:
                    import importlib.util
                    repo_root = Path(__file__).resolve().parents[2]
                    candidate = repo_root / 'backend' / 'ai' / 'quiz_generator_rag_tfidf.py'
                    if candidate.exists():
                        spec = importlib.util.spec_from_file_location('quiz_generator_rag_tfidf', str(candidate))
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        generate_mcqs = getattr(module, 'generate_mcqs', None)
                except Exception:
                    generate_mcqs = None

    if generate_mcqs:
        try:
            return generate_mcqs(paragraph, num_qs)
        except Exception:
            return fallback_generate_mcqs(paragraph, num_qs)
    else:
        return fallback_generate_mcqs(paragraph, num_qs)


def fallback_generate_mcqs(text, num_qs=3):
    """Improved lightweight generator that creates a mix of MCQ, True/False and Fill-in."""
    import re, random
    sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if s.strip()]
    words = [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", text)]
    words = list(dict.fromkeys(words))
    out = []

    # Helper: create MCQ from a sentence/word
    def make_mcq(answer, sentence=None):
        opts = [answer]
        # choose random distractors from words (avoid duplicates and the answer)
        candidates = [w for w in words if w.lower() != answer.lower() and w not in opts]
        random.shuffle(candidates)
        for w in candidates:
            if len(opts) >= 4:
                break
            opts.append(w)
        # pad with generated distractors if needed
        k = 1
        while len(opts) < 4:
            opts.append(f"{answer}_opt{k}")
            k += 1
        random.shuffle(opts)
        qtext = sentence or f"Choose the correct option about '{answer}'"
        return {'type': 'mcq', 'question': qtext.replace(answer, '_____') if sentence and answer.lower() in sentence.lower() else qtext, 'options': opts, 'answer_index': opts.index(answer)}

    # Helper: true/false question
    def make_tf(statement, truth=True):
        return {'type': 'tf', 'question': statement + ' (True/False)', 'options': ['True', 'False'], 'answer_index': 0 if truth else 1}

    # Helper: fill-in question
    def make_fill(answer, sentence=None):
        qtext = sentence.replace(answer, '_____') if sentence and answer.lower() in sentence.lower() else f"Fill the blank: _____"
        return {'type': 'fill', 'question': qtext, 'options': [], 'answer_index': 0, 'answer_text': answer}

    # Prefer sentence-local answers; pick a random candidate per sentence for variety
    for s in sentences:
        if len(out) >= num_qs:
            break
        candidates = re.findall(r"\b[a-zA-Z]{4,}\b", s)
        if not candidates:
            continue
        ans = random.choice(candidates)
        # randomly choose question type, weighted toward mcq
        idx = random.choices([0, 1, 2], weights=(6, 3, 3), k=1)[0]
        if idx == 0:
            out.append(make_mcq(ans, s))
        elif idx == 1:
            # make a simple TF by asserting a short fact from sentence
            stmt = s if len(s) < 120 else s[:120]
            truth = random.choice([True, True, False])
            out.append(make_tf(stmt, truth=truth))
        else:
            out.append(make_fill(ans, s))

    # If not enough, create questions from global words (randomized order)
    random.shuffle(words)
    wi = 0
    while len(out) < num_qs and wi < len(words):
        ans = words[wi]
        wi += 1
        idx = random.choice([0, 1, 2])
        if idx == 0:
            out.append(make_mcq(ans))
        elif idx == 1:
            out.append(make_tf(f"{ans} is mentioned in the paragraph.", truth=random.choice([True, False])))
        else:
            out.append(make_fill(ans))

    # Final pad with generic fill/mcq
    while len(out) < num_qs:
        base = f"option{len(out)+1}"
        out.append({'type': 'mcq', 'question': f"Choose the correct option about {base}", 'options': [base, base + '_A', base + '_B', base + '_C'], 'answer_index': 0})

    return out
    


def safe_make_response(data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "POST, GET, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]
    return status, headers, body


def _results_csv_path():
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / 'backend' / 'quiz_results.csv'


def persist_result(name, student_id, score, total, quiz_id=None):
    path = _results_csv_path()
    header = ['quiz_id', 'student_name', 'student_id', 'score', 'total', 'date']
    row = [quiz_id or '', name or '', student_id or '', str(score), str(total), datetime.utcnow().isoformat()]
    write_header = not path.exists()
    try:
        with open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            writer.writerow(row)
        return True
    except Exception:
        return False


def ensure_mcqs_have_explanations(mcqs):
    # Add a simple explanation if not present
    for m in mcqs:
        if 'explanation' not in m:
            options = m.get('options') or []
            idx = int(m.get('answer_index', 0)) if isinstance(m.get('answer_index', 0), (int, str)) else 0
            answer_text = None
            if options and 0 <= idx < len(options):
                answer_text = options[idx]
            elif 'answer_text' in m:
                answer_text = m['answer_text']
            else:
                answer_text = 'the correct choice'
            m['explanation'] = f"Answer is '{answer_text}'"
    return mcqs


def _demo_timestamp():
    return datetime.utcnow().isoformat()


def demo_attendance():
    return {
        'present_count': 24,
        'total_students': 30,
        'updated_at': _demo_timestamp(),
    }


def demo_teacher_status():
    return {
        'status': 'All teachers checked in',
        'note': 'Demo data returned by backend/api/quiz.py',
        'updated_at': _demo_timestamp(),
    }


def demo_chat_reply(message: str | None) -> str:
    if not message:
        return 'Hello! Ask me anything about the quiz or school.'
    lower = message.lower()
    if 'quiz' in lower:
        return 'The quiz API can generate MCQs, true/false, and fill-in blanks.'
    if 'result' in lower or 'score' in lower:
        return 'Scores are stored in backend/quiz_results.csv with name, id, and date.'
    return f"You said: '{message}'. Keep exploring!"


def build_flask_app():
    try:
        from flask import Flask, request, jsonify, make_response
    except Exception:
        raise

    app = Flask(__name__)

    # Ensure CORS headers are always present for browser calls from http://localhost:3000
    @app.after_request
    def add_cors_headers(response):
        response.headers.setdefault('Access-Control-Allow-Origin', '*')
        response.headers.setdefault('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        response.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type')
        return response

    def _options_response():
        resp = make_response('', 204)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    @app.route('/api/quiz', methods=['POST', 'OPTIONS'])
    def quiz_endpoint():
        if request.method == 'OPTIONS':
            return _options_response()

        data = request.get_json(force=True) or {}
        paragraph = data.get('paragraph') or data.get('text') or data.get('paragraph', '')
        num_qs = int(data.get('num_questions') or data.get('num') or 3)
        if not paragraph:
            return jsonify({'error': 'No paragraph provided.'}), 400
        mcqs = safe_generate(paragraph, num_qs)
        mcqs = ensure_mcqs_have_explanations(mcqs)
        return jsonify({'mcqs': mcqs})

    @app.route('/api/generate-quiz', methods=['POST', 'OPTIONS'])
    def generate_quiz():
        if request.method == 'OPTIONS':
            return _options_response()
        data = request.get_json(force=True) or {}
        paragraph = data.get('paragraph') or data.get('text') or ''
        num_qs = int(data.get('num_questions') or data.get('num') or 3)
        if not paragraph:
            return jsonify({'error': 'No paragraph provided.'}), 400
        mcqs = safe_generate(paragraph, num_qs)
        mcqs = ensure_mcqs_have_explanations(mcqs)
        answer_key = [int(q.get('answer_index', 0)) for q in mcqs]
        explanations = [q.get('explanation', '') for q in mcqs]
        quiz_id = str(uuid.uuid4())
        return jsonify({'quiz_id': quiz_id, 'mcqs': mcqs, 'answer_key': answer_key, 'explanations': explanations})

    @app.route('/api/submit-quiz', methods=['POST', 'OPTIONS'])
    def submit_quiz():
        if request.method == 'OPTIONS':
            return _options_response()
        data = request.get_json(force=True) or {}
        quiz_id = data.get('quiz_id')
        student_name = data.get('student_name') or data.get('name')
        student_id = data.get('student_id') or data.get('sid')
        answers = data.get('answers') or []
        mcqs = data.get('mcqs') or []
        answer_key = data.get('answer_key') or []

        if not answer_key and mcqs:
            try:
                answer_key = [int(q.get('answer_index', 0)) for q in mcqs]
            except Exception:
                answer_key = []

        if not answer_key:
            return jsonify({'error': 'No answer_key or mcqs provided for grading.'}), 400

        total = len(answer_key)
        correct = 0
        for i, a in enumerate(answer_key):
            try:
                submitted = int(answers[i]) if i < len(answers) else None
                if submitted is not None and submitted == int(a):
                    correct += 1
            except Exception:
                pass

        persist_result(student_name, student_id, correct, total, quiz_id=quiz_id)
        return jsonify({'score': correct, 'total': total, 'percentage': round(100.0 * correct / total, 2)})

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/api/attendance')
    def attendance():
        return jsonify(demo_attendance())

    @app.route('/api/teacher_status')
    def teacher_status():
        return jsonify(demo_teacher_status())

    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.get_json(force=True) or {}
        message = data.get('message') or data.get('text')
        return jsonify({'reply': demo_chat_reply(message)})

    return app


def run_flask():
    app = build_flask_app()
    print('Starting Flask server on http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000)


def run_fallback_server():
    # Minimal HTTP server using http.server
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def _set_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        def do_OPTIONS(self):
            self.send_response(204)
            self._set_cors_headers()
            self.end_headers()

        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length).decode('utf-8') if length else ''
            try:
                payload = json.loads(raw) if raw else {}
            except Exception:
                payload = {}
            # /api/quiz and /api/generate-quiz -> generate questions
            if self.path in ['/api/quiz', '/api/generate-quiz']:
                paragraph = payload.get('paragraph') or payload.get('text') or ''
                num_qs = int(payload.get('num_questions') or payload.get('num') or 3)
                if not paragraph:
                    status, headers, body = safe_make_response({'error': 'No paragraph provided.'}, status=400)
                else:
                    mcqs = safe_generate(paragraph, num_qs)
                    mcqs = ensure_mcqs_have_explanations(mcqs)
                    status, headers, body = safe_make_response({'quiz_id': str(uuid.uuid4()), 'mcqs': mcqs}, status=200)
            # /api/submit-quiz -> grade and persist
            elif self.path == '/api/submit-quiz':
                quiz_id = payload.get('quiz_id')
                student_name = payload.get('student_name') or payload.get('name')
                student_id = payload.get('student_id') or payload.get('sid')
                answers = payload.get('answers') or []
                mcqs = payload.get('mcqs') or []
                if not mcqs:
                    status, headers, body = safe_make_response({'error': 'No quiz questions provided for grading.'}, status=400)
                else:
                    total = len(mcqs)
                    correct = 0
                    for i, q in enumerate(mcqs):
                        correct_index = q.get('answer_index') if 'answer_index' in q else q.get('answerIndex', 0)
                        try:
                            if i < len(answers) and int(answers[i]) == int(correct_index):
                                correct += 1
                        except Exception:
                            pass
                    persist_result(student_name, student_id, correct, total, quiz_id=quiz_id)
                    status, headers, body = safe_make_response({'score': correct, 'total': total, 'percentage': round(100.0 * correct / total, 2)}, status=200)
            elif self.path == '/api/chat':
                message = payload.get('message') or payload.get('text')
                status, headers, body = safe_make_response({'reply': demo_chat_reply(message)})
            else:
                self.send_response(404)
                self._set_cors_headers()
                self.end_headers()
                return

            self.send_response(status)
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == '/api/health':
                status, headers, body = safe_make_response({'status': 'ok'})
            elif self.path == '/api/attendance':
                status, headers, body = safe_make_response(demo_attendance())
            elif self.path == '/api/teacher_status':
                status, headers, body = safe_make_response(demo_teacher_status())
            else:
                status, headers, body = safe_make_response({'message': 'Quiz API fallback server. POST /api/quiz'}, status=200)
            self.send_response(status)
            for k, v in headers:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

    port = 5000
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'Starting fallback HTTP server on http://127.0.0.1:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down')
        server.server_close()


def main():
    # If flask is available, prefer it for better dev UX
    try:
        import flask  # noqa: F401
        run_flask()
    except Exception:
        print('Flask not available or failed to import; using fallback HTTP server.')
        run_fallback_server()


if __name__ == '__main__':
    main()
