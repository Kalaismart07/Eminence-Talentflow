
from src.database import get_connection, RESULTS_FILE

confirm = input(
    "DELETE ALL CANDIDATE RECORDS AND SCREENING RESULTS? Type DELETE: "
)

if confirm != "DELETE":
    print("Cancelled. No data deleted.")
    raise SystemExit

with get_connection() as conn:
    conn.execute("DELETE FROM stage_history")
    conn.execute("DELETE FROM candidates")

if RESULTS_FILE.exists():
    RESULTS_FILE.write_text("[]", encoding="utf-8")

print("Local candidate records and screening results cleared.")
