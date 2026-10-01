import os, re, uuid
from fastapi import HTTPException
from .. import config
from ..analyzers.normalize import detect_language

def safe_name(name):
    base = os.path.basename((name or "").replace("\\", "/"))       # blocks path traversal
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)[:100].lstrip(".")
    return base or "file"

def validate_and_store(filename, raw: bytes):
    """Validate extension/size, decode text, store under a random name. Code is never executed."""
    name = safe_name(filename)
    ext = os.path.splitext(name.lower())[1]
    if ext not in config.ALLOWED_EXT:
        raise HTTPException(400, f"{name}: unsupported type '{ext}'. Allowed: {', '.join(sorted(config.ALLOWED_EXT))}")
    if len(raw) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"{name}: larger than {config.MAX_UPLOAD_BYTES // 1000} KB")
    if not raw.strip():
        raise HTTPException(400, f"{name}: file is empty")
    if b"\x00" in raw:
        raise HTTPException(400, f"{name}: binary content rejected")
    code = raw.decode("utf-8", errors="replace")
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    path = os.path.join(config.UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return name, detect_language(name), code, path
