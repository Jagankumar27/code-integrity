"""Central configuration. Change weights / risk bands here (or via env vars)."""
import os, json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'backend', 'integrity.db')}")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 200_000))
ALLOWED_EXT = {".py", ".java", ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp"}
# Overall = weighted sum of the four independent scores (weights must sum to 1)
WEIGHTS = json.loads(os.getenv("SIM_WEIGHTS", "null")) or {
    "text": 0.20, "token": 0.25, "structural": 0.30, "semantic": 0.25}
# (lower, upper, label) in percent
RISK_BANDS = [(0, 30, "Low"), (30, 60, "Moderate"), (60, 80, "High"), (80, 100.01, "Very High")]
SHINGLE_SIZE = 4
NOTE = ("This report identifies potential code similarities and is intended to support human review. "
        "Similarity alone does not establish plagiarism or misconduct.")
