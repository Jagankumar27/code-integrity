import json
from itertools import combinations
from ..analyzers.similarity import analyze_batch
from ..models.models import Analysis, Comparison, Submission

def run_analysis(db, user, subs, pairs=None):
    """Runs the real engine on `subs` and persists an Analysis + Comparison rows."""
    items = [{"id": s.id, "filename": s.filename, "code": s.code} for s in subs]
    results = analyze_batch(items, pairs)
    an = Analysis(created_by=user.id, n_submissions=len(subs), n_pairs=len(results))
    db.add(an); db.flush()
    for r in results:
        db.add(Comparison(
            analysis_id=an.id, sub_a_id=r["a"], sub_b_id=r["b"], text_sim=r["text"], token_sim=r["token"],
            structural_sim=r["structural"], semantic_sim=r["semantic"], overall=r["overall"], risk=r["risk"],
            method=r["method"],
            details=json.dumps({"explanations": r["explanations"], "blocks": r["blocks"], "renames": r["renames"]})))
    db.commit()
    return an

def serialize(c, role="teacher", user_id=None, with_code=True):
    """Dict for API/PDF. Students see only their own code; the other party is anonymised."""
    d = c.d()
    out = {"id": c.id, "analysis_id": c.analysis_id, "method": c.method, "risk": c.risk,
           "scores": {"overall": c.overall, "text": c.text_sim, "token": c.token_sim,
                      "structural": c.structural_sim, "semantic": c.semantic_sim},
           "explanations": d.get("explanations", []), "renames": d.get("renames", [])}
    a, b, blocks = c.sub_a, c.sub_b, d.get("blocks", [])
    flip = role == "student" and b.user_id == user_id
    if flip:
        a, b = b, a
        blocks = [{"a": x["b"], "b": x["a"], "lines": x["lines"]} for x in blocks]
        out["renames"] = [{"a": r["b"], "b": r["a"], "count": r["count"]} for r in out["renames"]]
    hide = role == "student"
    out.update({"blocks": blocks,
                "a": {"id": a.id, "student": a.student_name, "filename": a.filename, "language": a.language,
                      "code": a.code if with_code else None},
                "b": {"id": b.id, "student": "Another submission" if hide else b.student_name,
                      "filename": "hidden" if hide else b.filename, "language": b.language,
                      "code": None if (hide or not with_code) else b.code}})
    if hide:
        out["renames"] = []
    return out
