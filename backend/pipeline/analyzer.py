"""
analyzer.py — генерація аналітики з обробленого CSV.

Створює два файли:
  analytics/analytics/summary.json       ← для головної сторінки
  analytics/analytics/vacancy_stats.json ← повна аналітика

Запуск окремо:
    python pipeline/analyzer.py --input data/final/vacancies_2026-05-18_final.csv

Запуск як частина пайплайну:
    from pipeline.analyzer import run_analyzer
    run_analyzer(final_path)
"""

import os
import json
import argparse
from datetime import datetime
import pandas as pd

# ── Шляхи ────────────────────────────────────────────────────────────────────

ANALYTICS_DIR = "analytics"
SUMMARY_FILE = f"{ANALYTICS_DIR}/summary.json"
STATS_FILE = f"{ANALYTICS_DIR}/vacancy_stats.json"

CURRENT_YEAR    = datetime.now().year
TOP_N_CATEGORIES = 5


# ── Допоміжні функції ─────────────────────────────────────────────────────────

def safe_json(obj):
    """Конвертує numpy типи у стандартні Python типи для json.dump."""
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def save_json(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=safe_json)
    print(f"  [✓] Збережено: {path}")


def detect_remote(location: str) -> str:
    """
    Визначає тип роботи за полем location.
    Повертає: 'remote' | 'office'
    """
    if not isinstance(location, str):
        return "office"
    
    if location.lower().strip() == 'віддалено':
        return "remote"
    return "office"


# ── 1. Summary (головна сторінка) ─────────────────────────────────────────────

def build_summary(df: pd.DataFrame) -> dict:
    """
    Топ-5 категорій + загальна статистика для головної сторінки.

    Тренд рахується як різниця між поточним тижнем і попереднім
    на основі колонки collected_at (якщо є кілька тижнів збору)
    або updated (якщо збір тільки один).
    """
    print("\n  Генерація summary...")

    # Загальна статистика
    total_vacancies  = len(df)
    total_categories = df["category"].nunique()

    # Топ-5 категорій за кількістю вакансій
    category_counts = df["category"].value_counts()
    top5 = category_counts.head(TOP_N_CATEGORIES)

    # Тренд: порівнюємо останні 7 днів з попередніми 7 днями по updated
    df["updated"] = pd.to_datetime(df["updated"], errors="coerce")
    max_date   = df["updated"].max()
    week_ago   = max_date - pd.Timedelta(days=7)
    two_weeks  = max_date - pd.Timedelta(days=14)

    current_week = df[df["updated"] > week_ago]
    prev_week    = df[(df["updated"] > two_weeks) & (df["updated"] <= week_ago)]

    top_categories = []
    for category, count in top5.items():
        curr = len(current_week[current_week["category"] == category])
        prev = len(prev_week[prev_week["category"] == category])
        change = curr - prev

        if change > 0:
            trend = "up"
        elif change < 0:
            trend = "down"
        else:
            trend = "stable"

        top_categories.append({
            "category":    category,
            "count":       int(count),
            "curr_week":   int(curr),
            "prev_week":   int(prev),
            "change":      int(change),
            "trend":       trend,
        })

    return {
        "generated_at":       datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_vacancies":    int(total_vacancies),
        "total_categories":   int(total_categories),
        "top_categories":     top_categories,
    }


# ── 2. Динаміка вакансій у часі ───────────────────────────────────────────────

def build_vacancy_dynamics(df: pd.DataFrame) -> dict:
    """
    Для кожної категорії будує два ряди даних:
      - monthly: помісячна агрегація за поточний рік (для річного графіку)
      - weekly:  потижнева агрегація за останні 8 тижнів (для детального графіку)

    Поле updated використовується як дата вакансії.
    """
    print("  Генерація vacancy_dynamics...")

    df = df.copy()
    df["updated"] = pd.to_datetime(df["updated"], errors="coerce")

    # Фільтруємо поточний рік
    current_year_df = df[df["updated"].dt.year == CURRENT_YEAR].copy()
    current_year_df["month"]     = current_year_df["updated"].dt.to_period("M").astype(str)
    current_year_df["week_start"] = (
        current_year_df["updated"]
        - pd.to_timedelta(current_year_df["updated"].dt.dayofweek, unit="D")
    ).dt.strftime("%Y-%m-%d")

    dynamics = {}

    for category in df["category"].unique():
        cat_df      = current_year_df[current_year_df["category"] == category]
        cat_all_df  = df[df["category"] == category]

        # Місячна динаміка (весь поточний рік)
        monthly_counts = (
            cat_df.groupby("month")
            .size()
            .reset_index(name="count")
            .sort_values("month")
        )

        monthly = [
            {
                "period":  row["month"],          # "2026-01"
                "label":   _month_label(row["month"]),  # "Січень"
                "count":   int(row["count"]),
            }
            for _, row in monthly_counts.iterrows()
        ]

        # Потижнева динаміка (останні 8 тижнів)
        max_date    = cat_all_df["updated"].max()
        eight_weeks = max_date - pd.Timedelta(weeks=8)
        recent_df   = cat_df[cat_df["updated"] >= eight_weeks]

        weekly_counts = (
            recent_df.groupby("week_start")
            .size()
            .reset_index(name="count")
            .sort_values("week_start")
        )

        weekly = [
            {
                "period": row["week_start"],    # "2026-03-17"
                "label":  _week_label(row["week_start"]),  # "17 бер"
                "count":  int(row["count"]),
            }
            for _, row in weekly_counts.iterrows()
        ]

        dynamics[category] = {
            "monthly": monthly,
            "weekly":  weekly,
        }

    return dynamics


def _month_label(period: str) -> str:
    """"2026-01" → "Січень 2026" """
    months_uk = {
        "01": "Січень", "02": "Лютий",  "03": "Березень",
        "04": "Квітень","05": "Травень", "06": "Червень",
        "07": "Липень", "08": "Серпень", "09": "Вересень",
        "10": "Жовтень","11": "Листопад","12": "Грудень",
    }
    try:
        year, month = period.split("-")
        return f"{months_uk.get(month, month)} {year}"
    except Exception:
        return period


def _week_label(date_str: str) -> str:
    """"2026-03-17" → "17 бер" """
    months_short = {
        1:"січ", 2:"лют", 3:"бер", 4:"кві", 5:"тра", 6:"чер",
        7:"лип", 8:"сер", 9:"вер", 10:"жов", 11:"лис", 12:"гру",
    }
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{d.day} {months_short[d.month]}"
    except Exception:
        return date_str


# ── 3. Remote індекс ──────────────────────────────────────────────────────────

def build_remote_index(df: pd.DataFrame) -> dict:
    """
    Для кожної категорії рахує відсоток remote та office вакансій.
    """
    print("  Генерація remote_index...")

    df = df.copy()
    df["work_type"] = df["location"].apply(detect_remote)

    remote_index = {}

    for category in df["category"].unique():
        cat_df = df[df["category"] == category]
        total  = len(cat_df)
        if total == 0:
            continue

        remote_count = int((cat_df["work_type"] == "remote").sum())
        office_count = total - remote_count

        remote_index[category] = {
            "total":          total,
            "remote_count":   remote_count,
            "office_count":   office_count,
            "remote_percent": round(remote_count / total * 100),
            "office_percent": round(office_count / total * 100),
            "note":           "визначено за полем location",
        }

    return remote_index


# ── 4. Тип зайнятості ─────────────────────────────────────────────────────────

def build_employment_type(df: pd.DataFrame) -> dict:
    """
    Для кожної категорії рахує розподіл full_time / part_time / internship / temporary.
    """
    print("  Генерація employment_type...")

    employment = {}

    for category in df["category"].unique():
        cat_df = df[df["category"] == category]
        total  = len(cat_df)
        if total == 0:
            continue

        result = {}
        for col in ["full_time", "part_time", "internship", "temporary"]:
            if col in cat_df.columns:
                count = int(cat_df[col].sum())
                result[col] = {
                    "count":   count,
                    "percent": round(count / total * 100),
                }

        employment[category] = {
            "total": total,
            **result,
        }

    return employment


# ── Головна функція ───────────────────────────────────────────────────────────

def run_analyzer(input_path: str):
    """
    Читає final CSV і генерує обидва JSON файли аналітики.
    """
    os.makedirs(ANALYTICS_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"ANALYZER: читаємо {input_path}")
    print(f"{'='*60}")

    df = pd.read_csv(input_path, encoding="utf-8-sig")
    print(f"Завантажено вакансій: {len(df)}")

    # ── summary.json ─────────────────────────────────────────────────────────
    summary = build_summary(df)
    save_json(summary, SUMMARY_FILE)

    # ── vacancy_stats.json ───────────────────────────────────────────────────
    vacancy_stats = {
        "generated_at":       datetime.now().strftime("%Y-%m-%d %H:%M"),
        "vacancies_analyzed": len(df),
        "vacancy_dynamics":   build_vacancy_dynamics(df),
        "remote_index":       build_remote_index(df),
        "employment_type":    build_employment_type(df),
    }
    save_json(vacancy_stats, STATS_FILE)

    print(f"\n{'='*60}")
    print(f"✅ Аналітику згенеровано")
    print(f"   {SUMMARY_FILE}")
    print(f"   {STATS_FILE}")
    print(f"{'='*60}")


# ── Запуск окремо ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", required=True,
        help="Шлях до final CSV"
    )
    args = parser.parse_args()
    run_analyzer(args.input)