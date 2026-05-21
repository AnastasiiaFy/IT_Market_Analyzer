"""
GET /api/vacancies/stats?category=Frontend+Developer
    → динаміка вакансій, remote індекс, тип зайнятості для категорії

GET /api/vacancies/stats?category=Frontend+Developer&section=dynamics
    → тільки динаміка (для часткового оновлення на фронтенді)
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import Literal

router = APIRouter(tags=["Vacancies"])

VALID_SECTIONS = {"dynamics", "remote", "employment"}


@router.get("/vacancies/stats")
def get_vacancy_stats(
    request:  Request,
    category: str = Query(..., description="Категорія, напр. 'Frontend Developer'"),
    section:  str = Query(None, description="Опційно: dynamics | remote | employment"),
):
    """
    Повертає аналітику по вакансіях для обраної категорії.

    Без параметра section — повертає всі три секції одразу.
    З параметром section — повертає тільки потрібну секцію.

    Приклад відповіді (section=dynamics):
    {
      "category": "Frontend Developer",
      "vacancy_dynamics": {
        "monthly": [{"period": "2026-01", "label": "Січень 2026", "count": 240}],
        "weekly":  [{"period": "2026-05-12", "label": "12 тра", "count": 48}]
      }
    }
    """
    data = request.app.state.vacancy_stats
    if not data:
        raise HTTPException(status_code=503, detail="Дані ще не завантажені")

    # Перевіряємо чи існує категорія
    dynamics   = data.get("vacancy_dynamics", {})
    remote     = data.get("remote_index", {})
    employment = data.get("employment_type", {})

    all_categories = set(dynamics) | set(remote) | set(employment)
    if category not in all_categories:
        raise HTTPException(
            status_code=404,
            detail=f"Категорія '{category}' не знайдена. "
                   f"Доступні: {sorted(all_categories)}"
        )

    # Секційний запит
    if section:
        if section not in VALID_SECTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Невідома секція '{section}'. "
                       f"Доступні: {sorted(VALID_SECTIONS)}"
            )
        section_data = {
            "dynamics":   {"vacancy_dynamics":  dynamics.get(category, {})},
            "remote":     {"remote_index":       remote.get(category, {})},
            "employment": {"employment_type":    employment.get(category, {})},
        }
        return {"category": category, **section_data[section]}

    # Повна відповідь
    return {
        "category":        category,
        "generated_at":    data.get("generated_at"),
        "vacancy_dynamics": dynamics.get(category, {}),
        "remote_index":    remote.get(category, {}),
        "employment_type": employment.get(category, {}),
    }