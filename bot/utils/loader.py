import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
QUESTIONS_PATH = DATA_DIR / "questions.json"
STATS_PATH = DATA_DIR / "stats.json"
FEEDBACK_PATH = DATA_DIR / "feedback.json"


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
