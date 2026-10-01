import os
from collections import Counter
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import config
from ..database.db import get_db
from ..models.models import Comparison, Submission, User
from ..schemas.schemas import AnalyzeMany, AnalyzeOne, LoginIn
from ..services import auth, report, seed
from ..services.pipeline import run_analysis, serialize
from ..utils.files import validate_and_store, safe_name

router = APIRouter(prefix="/api")
HIGH = config.RISK_BANDS[2][0]  # lower bound of the "High" band

def sub_dict(s):
    return {"id": s.id, "student_name": s.student_name, "filename": s.filename, "language": s.language,
            "uploaded_at": s.uploaded_at.isoformat(), "lines": s.code.count("\n") + 1}

def latest_pairs(db, user):
    """Newest comparison for every submission pair (students: only pairs involving them)."""
    best = {}
    for c in db.query(Comparison).order_by(Comparison.id).all():
        if user.role == "student" and user.id not in (c.sub_a.user_id, c.sub_b.user_id):
            continue
        best[tuple(sorted((c.sub_a_id, c.sub_b_id)))] = c
    return list(best.values())

def get_comparison(db, cid, user):
    c = db.get(Comparison, cid)
    if not c or (user.role == "student" and user.id not in (c.sub_a.user_id, c.sub_b.user_id)):
        raise HTTPException(404, "Comparison not found")
    return c

@router.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter_by(username=body.username.strip().lower()).first()
    if not u or not auth.check_pw(body.password, u.password_hash):
        raise HTTPException(401, "Invalid username or password")
    return {"token": auth.make_token(u), "user": {"id": u.id, "name": u.name, "role": u.role, "username": u.username}}

@router.post("/submissions/upload")
async def upload(files: List[UploadFile] = File(...), student_name: Optional[str] = Form(None),
                 user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    if not files or len(files) > 50:
        raise HTTPException(400, "Upload between 1 and 50 files")
    out = []
    for f in files:
        raw = await f.read(config.MAX_UPLOAD_BYTES + 1)
        name, lang, code, path = validate_and_store(f.filename, raw)
        who = user.name if user.role == "student" else (student_name.strip()[:100] if student_name and len(files) == 1
                                                         else os.path.splitext(name)[0].replace("_", " ").title())
        s = Submission(user_id=user.id, student_name=who, filename=name, stored_path=path, language=lang, code=code)
        db.add(s); out.append(s)
    db.commit()
    return [sub_dict(s) for s in out]

@router.get("/submissions")
def submissions(user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    q = db.query(Submission).order_by(Submission.id.desc())
    if user.role == "student":
        q = q.filter_by(user_id=user.id)
    return [sub_dict(s) for s in q.all()]

@router.get("/submissions/{sid}")
def submission(sid: int, user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    s = db.get(Submission, sid)
    if not s or (user.role == "student" and s.user_id != user.id):
        raise HTTPException(404, "Submission not found")
    return {**sub_dict(s), "code": s.code}

@router.post("/analyze")
def analyze(body: AnalyzeOne, user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    """Compare one submission against the others (default: all other submissions of the same language)."""
    s = db.get(Submission, body.submission_id)
    if not s or (user.role == "student" and s.user_id != user.id):
        raise HTTPException(404, "Submission not found")
    others = db.query(Submission).filter(Submission.id != s.id, Submission.language == s.language)
    if body.compare_with:
        others = others.filter(Submission.id.in_(body.compare_with))
    others = others.all()
    if not others:
        raise HTTPException(400, "No other submissions in the same language to compare against")
    an = run_analysis(db, user, [s] + others, pairs=[(s.id, o.id) for o in others])
    return {"analysis_id": an.id, "pairs": an.n_pairs,
            "comparisons": [serialize(c, user.role, user.id, False) for c in an.comparisons]}

@router.post("/analyze/multiple")
def analyze_multiple(body: AnalyzeMany, user: User = Depends(auth.teacher_only), db: Session = Depends(get_db)):
    ids = list(dict.fromkeys(body.submission_ids))
    subs = db.query(Submission).filter(Submission.id.in_(ids)).all()
    if len(subs) < 2:
        raise HTTPException(400, "Select at least two valid submissions")
    an = run_analysis(db, user, subs)
    if an.n_pairs == 0:
        raise HTTPException(400, "No comparable pairs (files must share a language)")
    return {"analysis_id": an.id, "pairs": an.n_pairs}

@router.get("/comparisons")
def comparisons(user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    rows = sorted(latest_pairs(db, user), key=lambda c: -c.overall)
    return [serialize(c, user.role, user.id, False) for c in rows]

@router.get("/comparisons/{cid}")
def comparison(cid: int, user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    return serialize(get_comparison(db, cid, user), user.role, user.id, True)

@router.get("/matrix")
def matrix(user: User = Depends(auth.teacher_only), db: Session = Depends(get_db)):
    pairs = latest_pairs(db, user)
    subs = {}
    for c in pairs:
        subs[c.sub_a_id], subs[c.sub_b_id] = c.sub_a, c.sub_b
    ids = sorted(subs)
    cell = {}
    for c in pairs:
        v = {"overall": c.overall, "risk": c.risk, "comparison_id": c.id}
        cell[(c.sub_a_id, c.sub_b_id)] = cell[(c.sub_b_id, c.sub_a_id)] = v
    return {"labels": [subs[i].student_name for i in ids], "ids": ids,
            "cells": [[cell.get((i, j)) for j in ids] for i in ids]}

@router.get("/dashboard")
def dashboard(user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    pairs = latest_pairs(db, user)
    q = db.query(Submission)
    if user.role == "student":
        q = q.filter_by(user_id=user.id)
    subs = q.all()
    vals = [c.overall for c in pairs]
    dist = [{"range": f"{i}-{i + 10}", "count": sum(1 for v in vals if i <= v < i + 10 or (i == 90 and v == 100))} for i in range(0, 100, 10)]
    top = sorted(pairs, key=lambda c: -c.overall)[:5]
    hide = user.role == "student"
    name = lambda s, mine: s.student_name if (not hide or mine) else "Other"
    return {
        "role": user.role, "total_submissions": len(subs), "pairs_analyzed": len(pairs),
        "high_pairs": sum(1 for v in vals if v >= HIGH), "average_similarity": round(sum(vals) / len(vals), 1) if vals else 0,
        "languages": [{"name": k, "value": v} for k, v in Counter(s.language for s in subs).items()],
        "distribution": dist,
        "top_pairs": [{"id": c.id, "label": f"{name(c.sub_a, c.sub_a.user_id == user.id)} ↔ {name(c.sub_b, c.sub_b.user_id == user.id)}",
                       "overall": c.overall, "risk": c.risk} for c in top],
        "network": {"nodes": sorted({c.sub_a.student_name for c in pairs} | {c.sub_b.student_name for c in pairs}) if not hide else [],
                    "edges": [{"a": c.sub_a.student_name, "b": c.sub_b.student_name, "overall": c.overall, "id": c.id}
                              for c in pairs if c.overall >= config.RISK_BANDS[1][0]] if not hide else []},
        "bands": [{"label": b[2], "from": b[0], "to": min(b[1], 100)} for b in config.RISK_BANDS],
    }

@router.get("/reports/{cid}")
def report_pdf(cid: int, user: User = Depends(auth.current_user), db: Session = Depends(get_db)):
    c = get_comparison(db, cid, user)
    path = os.path.join(config.REPORT_DIR, f"integrity_report_{c.id}_{user.role}.pdf")
    report.build_pdf(serialize(c, user.role, user.id, False), path)
    return FileResponse(path, media_type="application/pdf", filename=f"integrity_report_{c.id}.pdf")

@router.post("/demo/load")
def demo(user: User = Depends(auth.teacher_only), db: Session = Depends(get_db)):
    an = seed.load_demo(db, user)
    return {"analysis_id": an.id, "pairs": an.n_pairs}
