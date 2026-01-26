import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = DATA_DIR / "content"
RUNTIME_DIR = DATA_DIR / "runtime"
QUESTIONS_PATH = CONTENT_DIR / "questions.json"
SACRED_NUMBERS_PATH = CONTENT_DIR / "sacred_numbers.json"
COMPARE_TEXT_PATH = CONTENT_DIR / "compare_text.txt"
COMPARE_QUESTIONS_PATH = CONTENT_DIR / "compare_questions.json"
STATS_PATH = RUNTIME_DIR / "stats.json"
FEEDBACK_PATH = RUNTIME_DIR / "feedback.json"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_questions():
    return _load_json(QUESTIONS_PATH, [])


def load_stats():
    return _load_json(STATS_PATH, {})


def save_stats(stats) -> None:
    _save_json(STATS_PATH, stats)


def append_feedback(entry) -> None:
    feedback = _load_json(FEEDBACK_PATH, [])
    feedback.append(entry)
    _save_json(FEEDBACK_PATH, feedback)


def load_sacred_numbers():
    return _load_json(SACRED_NUMBERS_PATH, {})


def load_compare_text() -> str:
    if not COMPARE_TEXT_PATH.exists():
        return ""
    return COMPARE_TEXT_PATH.read_text(encoding="utf-8")


def load_compare_questions():
    return _load_json(COMPARE_QUESTIONS_PATH, [])
