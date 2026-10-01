import os
from ..models.models import User, Submission
from ..database.db import SessionLocal
from ..utils.files import validate_and_store
from .auth import hash_pw
from .pipeline import run_analysis

USERS = [("teacher", "Prof. Rao", "teacher123", "teacher"), ("alice", "Alice", "student123", "student"),
         ("bob", "Bob", "student123", "student"), ("carol", "Carol", "student123", "student"),
         ("dave", "Dave", "student123", "student"), ("eve", "Eve", "student123", "student")]

def seed_users(db):
    for u, n, p, r in USERS:
        if not db.query(User).filter_by(username=u).first():
            db.add(User(username=u, name=n, password_hash=hash_pw(p), role=r))
    db.commit()

def load_demo(db, teacher):
    """Uploads the 5 sample programs as the matching students, then runs the real engine."""
    folder = os.path.join(os.path.dirname(__file__), "..", "sample_data")
    subs = []
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".py"):
            continue
        owner = db.query(User).filter_by(username=fn.split("_")[0]).first()
        if db.query(Submission).filter_by(user_id=owner.id, filename=fn).first():
            subs.append(db.query(Submission).filter_by(user_id=owner.id, filename=fn).first()); continue
        with open(os.path.join(folder, fn), "rb") as f:
            name, lang, code, path = validate_and_store(fn, f.read())
        s = Submission(user_id=owner.id, student_name=owner.name, filename=name, stored_path=path, language=lang, code=code)
        db.add(s); subs.append(s)
    db.commit()
    return run_analysis(db, teacher, subs)

if __name__ == "__main__":  # python -m app.services.seed
    from ..database.db import Base, engine
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_users(db); print("Users seeded")
        load_demo(db, db.query(User).filter_by(role="teacher").first()); print("Demo analysed")
