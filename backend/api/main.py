"""
main.py — точка входу FastAPI.

Запуск:
    cd backend
    uvicorn api.main:app --reload

Документація API (автоматична):
    http://localhost:8000/docs
"""

import json
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import summary, vacancies, skills, salaries

# ── Шляхи до JSON файлів ──────────────────────────────────────────────────────

ANALYTICS_DIR = Path(__file__).parent.parent / "analytics"


# ── Завантаження даних при старті сервера ─────────────────────────────────────

def load_json(filename: str) -> dict:
    path = ANALYTICS_DIR / filename
    if not path.exists():
        print(f"  [!] Файл не знайдено: {path}")
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Завантажуємо всі JSON файли один раз при старті сервера.
    Зберігаємо в app.state — доступно у всіх роутерах.
    """
    print("Завантаження аналітики...")
    app.state.summary        = load_json("summary.json")
    app.state.vacancy_stats  = load_json("vacancy_stats.json")
    app.state.skill_map      = load_json("skill_map.json")
    app.state.salary_stats   = load_json("salary_stats.json")
    print("✅ Дані завантажено\n")
    yield
    # При зупинці сервера (якщо потрібне очищення)


# ── Ініціалізація FastAPI ─────────────────────────────────────────────────────

app = FastAPI(
    title="IT Jobs Analyzer API",
    description="API для аналізу IT вакансій та зарплат на ринку України",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — дозволяємо запити з фронтенду ─────────────────────────────────────
# Під час розробки дозволяємо localhost:3000 (Next.js dev server)
# На продакшні замінити origins на реальний домен

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Підключення роутерів ──────────────────────────────────────────────────────

app.include_router(summary.router,    prefix="/api")
app.include_router(vacancies.router,  prefix="/api")
app.include_router(skills.router,     prefix="/api")
app.include_router(salaries.router,   prefix="/api")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "IT Jobs Analyzer API"}