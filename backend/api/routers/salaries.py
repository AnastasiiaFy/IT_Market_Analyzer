"""
GET /api/salaries?category=Frontend+Developer
    → зарплатна аналітика для категорії (квантилі + гістограма)

GET /api/salaries?category=Frontend+Developer&level=Middle
    → зарплатна аналітика тільки для одного рівня
"""

from fastapi import APIRouter, Request, HTTPException, Query

router = APIRouter(tags=["Salaries"])

VALID_LEVELS = {"Junior", "Middle", "Senior"}


@router.get("/salaries")
def get_salaries(
    request:  Request,
    category: str = Query(..., description="Категорія, напр. 'Frontend Developer'"),
    level:    str = Query(None, description="Опційно: Junior | Middle | Senior"),
):
    """
    Повертає зарплатну аналітику для категорії з даних DOU.

    Структура відповіді:
    {
      "category": "Frontend Developer",
      "source": "DOU Salary Survey",
      "source_url": "https://github.com/devua/csv/...",
      "currency": "USD",
      "total_records": 420,
      "by_level": {
        "Junior": {
          "q25": 800, "median": 1200, "q75": 1800,
          "count": 89,
          "histogram": [
            {"range_from": 500, "range_to": 1000, "label": "$500–1000", "count": 31}
          ]
        }
      },
      "overall": {
        "histogram": [...],   ← всі рівні разом
        "median": 2800
      }
    }
    """
    data = request.app.state.salary_stats
    if not data:
        raise HTTPException(status_code=503, detail="Дані ще не завантажені")

    stats = data.get("salary_stats", {})

    if category not in stats:
        raise HTTPException(
            status_code=404,
            detail=f"Категорія '{category}' не знайдена або замало даних. "
                   f"Доступні: {sorted(stats.keys())}"
        )

    cat_data = stats[category]

    # Метадані джерела — важливо показувати на фронтенді
    meta = {
        "source":       data.get("source"),
        "source_url":   data.get("source_url"),
        "source_note":  data.get("source_note"),
        "currency":     data.get("currency", "USD"),
        "years_range":  data.get("years_range"),
    }

    # Фільтр по рівню
    if level:
        if level not in VALID_LEVELS:
            raise HTTPException(
                status_code=400,
                detail=f"Невідомий рівень '{level}'. "
                       f"Доступні: {sorted(VALID_LEVELS)}"
            )
        level_data = cat_data.get("by_level", {}).get(level)
        if not level_data:
            raise HTTPException(
                status_code=404,
                detail=f"Дані для рівня '{level}' у категорії '{category}' відсутні"
            )
        return {
            "category": category,
            "level":    level,
            **meta,
            "data":     level_data,
        }

    # Всі рівні
    return {
        "category":      category,
        "total_records": cat_data.get("total_records"),
        **meta,
        "by_level":      cat_data.get("by_level", {}),
        "overall":       cat_data.get("overall", {}),
    }