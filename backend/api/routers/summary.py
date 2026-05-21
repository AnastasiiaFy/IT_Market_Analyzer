"""
GET /api/summary       → дані для головної сторінки (топ-5 категорій)
"""

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(tags=["Summary"])


@router.get("/summary")
def get_summary(request: Request):
    """
    Повертає дані для головної сторінки:
    - топ-5 категорій за кількістю вакансій з трендом
    """
    data = request.app.state.summary
    if not data:
        raise HTTPException(status_code=503, detail="Дані ще не завантажені")
    return data
