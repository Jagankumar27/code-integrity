from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .database.db import Base, engine, SessionLocal
from .models import models  # noqa: F401  (register tables)
from .services.seed import seed_users

app = FastAPI(title="AI-Powered Code Integrity API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_users(db)

@app.get("/")
def root():
    return {"name": "AI-Powered Code Integrity", "docs": "/docs", "note": "Similarity indicates potential similarity only."}

@app.get("/health")
def health():
    return {"status": "ok"}
