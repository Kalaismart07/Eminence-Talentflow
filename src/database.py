
import json
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "eminence_talentflow.db"
RESULTS_FILE = DATA_DIR / "screening_results.json"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements_json TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                job_id INTEGER REFERENCES jobs(id),
                skills_json TEXT NOT NULL DEFAULT '[]',
                matched_skills_json TEXT NOT NULL DEFAULT '[]',
                missing_skills_json TEXT NOT NULL DEFAULT '[]',
                skill_score REAL NOT NULL DEFAULT 0,
                education_score REAL NOT NULL DEFAULT 0,
                experience_score REAL NOT NULL DEFAULT 0,
                relevance_score REAL NOT NULL DEFAULT 0,
                final_score REAL NOT NULL DEFAULT 0,
                recommendation TEXT NOT NULL DEFAULT 'Under Review',
                stage TEXT NOT NULL DEFAULT 'Screening',
                resume_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS stage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL REFERENCES candidates(id),
                previous_stage TEXT,
                new_stage TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            )
        """)


def migrate_json_results():
    """Import existing screening results without deleting the JSON file."""
    init_db()

    if not RESULTS_FILE.exists():
        return 0

    try:
        with RESULTS_FILE.open("r", encoding="utf-8") as file:
            results = json.load(file)
    except (OSError, json.JSONDecodeError):
        return 0

    if not isinstance(results, list):
        return 0

    imported = 0
    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        for item in results:
            if not isinstance(item, dict) or not item.get("name"):
                continue

            name = str(item.get("name", "")).strip()
            email = str(item.get("email", "")).strip()
            phone = str(item.get("phone", "")).strip()

            existing = conn.execute(
                """
                SELECT id FROM candidates
                WHERE lower(name) = lower(?) AND lower(email) = lower(?)
                """,
                (name, email)
            ).fetchone()

            if existing:
                continue

            conn.execute("""
                INSERT INTO candidates (
                    name, email, phone, skills_json,
                    matched_skills_json, missing_skills_json,
                    skill_score, education_score, experience_score,
                    relevance_score, final_score, recommendation,
                    stage, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                json.dumps(item.get("skills", [])),
                json.dumps(item.get("matched_skills", [])),
                json.dumps(item.get("missing_skills", [])),
                float(item.get("skill_score", 0) or 0),
                float(item.get("education_score", 0) or 0),
                float(item.get("experience_score", 0) or 0),
                float(item.get("relevance_score", 0) or 0),
                float(item.get("final_score", 0) or 0),
                str(item.get("status", "Under Review")),
                "Screening",
                now,
                now
            ))
            imported += 1

    return imported


def get_candidates():
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM candidates ORDER BY final_score DESC, id DESC"
        ).fetchall()

    candidates = []
    for row in rows:
        item = dict(row)
        for field in (
            "skills_json",
            "matched_skills_json",
            "missing_skills_json"
        ):
            try:
                item[field.removesuffix("_json")] = json.loads(item[field])
            except (TypeError, json.JSONDecodeError):
                item[field.removesuffix("_json")] = []
        candidates.append(item)

    return candidates


def update_candidate_stage(candidate_id, new_stage, notes=""):
    allowed_stages = {
        "Screening", "Shortlisted", "Interview",
        "Offer", "Hired", "Rejected"
    }
    if new_stage not in allowed_stages:
        raise ValueError("Invalid recruitment stage.")

    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT stage FROM candidates WHERE id = ?",
            (candidate_id,)
        ).fetchone()

        if row is None:
            raise ValueError("Candidate not found.")

        previous_stage = row["stage"]

        conn.execute("""
            UPDATE candidates
            SET stage = ?, updated_at = ?
            WHERE id = ?
        """, (new_stage, now, candidate_id))

        conn.execute("""
            INSERT INTO stage_history (
                candidate_id, previous_stage, new_stage,
                changed_at, notes
            ) VALUES (?, ?, ?, ?, ?)
        """, (candidate_id, previous_stage, new_stage, now, notes))

        recommendation = {
            "Shortlisted": "Shortlisted",
            "Rejected": "Not Recommended"
        }.get(new_stage)

        if recommendation:
            conn.execute(
                "UPDATE candidates SET recommendation = ? WHERE id = ?",
                (recommendation, candidate_id)
            )

def save_screening_candidates(results, job_id=None):
    """Persist screening results in SQLite and skip duplicate name/email pairs."""
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    saved = 0

    with get_connection() as conn:
        for item in results:
            name = str(item.get("name", "")).strip()
            email = str(item.get("email", "")).strip()

            if not name:
                continue

            existing = conn.execute(
                """
                SELECT id FROM candidates
                WHERE lower(name) = lower(?) AND lower(email) = lower(?)
                """,
                (name, email)
            ).fetchone()

            if existing:
                continue

            conn.execute("""
                INSERT INTO candidates (
                    name, email, phone, job_id, skills_json,
                    matched_skills_json, missing_skills_json,
                    skill_score, education_score, experience_score,
                    relevance_score, final_score, recommendation,
                    stage, resume_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                str(item.get("phone", "")),
                job_id,
                json.dumps(item.get("skills", [])),
                json.dumps(item.get("matched_skills", [])),
                json.dumps(item.get("missing_skills", [])),
                float(item.get("skill_score", 0) or 0),
                float(item.get("education_score", 0) or 0),
                float(item.get("experience_score", 0) or 0),
                float(item.get("relevance_score", 0) or 0),
                float(item.get("final_score", 0) or 0),
                str(item.get("status", "Under Review")),
                "Screening",
                str(item.get("resume_text", "")),
                now,
                now
            ))
            saved += 1

    return saved


def clear_all_candidates():
    """Remove all candidate records and their stage history."""
    init_db()

    with get_connection() as conn:
        conn.execute("DELETE FROM stage_history")
        conn.execute("DELETE FROM candidates")

    if RESULTS_FILE.exists():
        RESULTS_FILE.write_text("[]", encoding="utf-8")
