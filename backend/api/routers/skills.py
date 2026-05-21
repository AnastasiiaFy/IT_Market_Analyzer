"""
GET /api/skills/map?category=Frontend+Developer
    → skill map для всіх рівнів категорії

GET /api/skills/map?category=Frontend+Developer&level=Middle
    → skill map тільки для одного рівня
"""

from fastapi import APIRouter, Request, HTTPException, Query

router = APIRouter(tags=["Skills"])

VALID_LEVELS = {"Junior", "Middle", "Senior"}


@router.get("/skills/map")
def get_skill_map(
    request:  Request,
    category: str = Query(..., description="Категорія, напр. 'Python Developer'"),
    level:    str = Query(None, description="Опційно: Junior | Middle | Senior"),
):
    """
    Повертає skill map для категорії.

    Структура відповіді:
    {
      "category": "Python Developer",
      "generated_at": "2026-05-18",
      "note": "...",
      "skill_map": {
        "Junior": {
          "total_vacancies": 89,
          "must_have": {
            "from_titles": ["Django, ...],
            "base_stack":  ["Python", ...]
          },
          "nice_to_have": { ... }
        },
        "Middle": { ... }
      }
    }
    """
    data = request.app.state.skill_map
    if not data:
        raise HTTPException(status_code=503, detail="Дані ще не завантажені")

    skill_map = data.get("skill_map", {})

    if category not in skill_map:
        raise HTTPException(
            status_code=404,
            detail=f"Категорія '{category}' не знайдена. "
                   f"Доступні: {sorted(skill_map.keys())}"
        )

    category_data = skill_map[category]

    # Фільтр по рівню
    if level:
        if level not in VALID_LEVELS:
            raise HTTPException(
                status_code=400,
                detail=f"Невідомий рівень '{level}'. "
                       f"Доступні: {sorted(VALID_LEVELS)}"
            )
        if level not in category_data:
            raise HTTPException(
                status_code=404,
                detail=f"Рівень '{level}' не знайдено для '{category}'"
            )
        return {
            "category":     category,
            "level":        level,
            "generated_at": data.get("generated_at"),
            "note":         data.get("note"),
            "data":         category_data[level],
        }

    # Всі рівні
    return {
        "category":     category,
        "generated_at": data.get("generated_at"),
        "note":         data.get("note"),
        "skill_map":    category_data,
    }