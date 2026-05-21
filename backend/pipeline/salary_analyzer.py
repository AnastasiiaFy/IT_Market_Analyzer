"""
salary_analyzer.py — аналіз зарплат на основі даних DOU.

Джерело: https://github.com/devua/csv/tree/master/salaries
При публікації обов'язково вказуйте DOU як джерело з активним посиланням.

Що генерує:
  analytics/salary_stats.json:
    - квантильні межі (25%, 50%, 75%) по рівнях
    - гістограма кількості анкет по діапазонах зарплат

Запуск окремо (після появи нових даних DOU — двічі на рік):
    python pipeline/salary_analyzer.py --data-dir data/dou_salaries/
"""

import os
import re
import json
import glob
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

# ── Шляхи ────────────────────────────────────────────────────────────────────

ANALYTICS_DIR = "analytics"
OUTPUT_FILE   = f"{ANALYTICS_DIR}/salary_stats.json"
DOU_DATA_DIR  = "data/dou_salaries"


# ── Назви колонок DOU ─────────────────────────────────────────────────────────

COL_DATE      = "Submitted at"
COL_SALARY    = "ЗАРПЛАТА / СУМАРНИЙ ДОХІД в IT у $$$ за місяць, лише ставка \nЧИСТИМИ - після сплати податків"
COL_TITLE     = "Тайтл"
COL_CATEGORY  = "Категорії"
COL_POSITION  = "Почніть вводити і оберіть вашу ОСНОВНУ посаду зі списку"
COL_LANGUAGE  = "Основна мова програмування"
COL_LOCATION  = "Україна  / закордон"

# ── Твої категорії (повний список) ────────────────────────────────────────────

MY_CATEGORIES = [
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Mobile Developer",
    "Java Developer",
    "Python Developer",
    ".NET Developer",
    "Software / Embedded Engineer",
    "Data Analyst",
    "Data Engineer",
    "ML / AI Engineer",
    "DevOps / SRE Engineer",
    "System Administrator / Network Engineer",
    "QA Manual Engineer",
    "QA Automation Engineer",
    "Business Analyst",
    "UX/UI Designer",
]



# ── Маппінг рівнів DOU → твої рівні ──────────────────────────────────────────

LEVEL_MAPPING = {
    "Intern/Trainee":                             "Junior",
    "Junior":                                     "Junior",
    
    "Middle":                                     "Middle",
    "Staff":                                      "Middle",
    "Architect":                                  "Middle",

    "Senior":                                     "Senior",
    "Lead":                                       "Senior",
    "Technical Lead":                             "Senior",
    "CEO / C-level (Chief) / Director / VP)":     "Senior",
    "Team Lead (for SE & QA: Lead + Team Lead)":  "Senior",
    "Principal":                                  "Senior",
    "Head":                                       "Senior",
    "Consultant / External Expert ":              "Senior"
}


# ── Назви категорій DOU ───────────────────────────────────────────────────────

DOU_SE       = "Software Engineer / Developer (frontend, backend, mobile, gamedev, embedded etc)"
DOU_QA       = "QA"
DOU_ANALYST  = "Analyst"
DOU_DATA_SCI = "Data Science"
DOU_DEVOPS   = "DevOps & SRE"
DOU_SECURITY = "Security"
COL_SE_SPECIALIZATION = "Спеціалізації: SE"


# ── Визначення категорії для одного рядка ─────────────────────────────────────

def map_category(row: pd.Series) -> str | None:
    dou_cat = str(row.get(COL_CATEGORY, "") or "").strip()
    position = str(row.get(COL_POSITION, "") or "").strip()
    language = str(row.get(COL_LANGUAGE, "") or "").strip()
    se_spec = str(row.get(COL_SE_SPECIALIZATION, "") or "").strip()

    # ==========================================================
    # SOFTWARE ENGINEER
    # ==========================================================

    if dou_cat == DOU_SE:

        # ---------- Спеціалізації ----------

        if se_spec == "Front-end розробка":
            return "Frontend Developer"

        if se_spec == "Back-end розробка":
            return "Backend Developer"

        if se_spec in [
            "Full Stack розробка",
            "Платформна / BI / low-code розробка (Salesforce, SAP, 1C тощо)"
        ]:
            return "Full Stack Developer"

        if se_spec == "Mobile розробка":
            return "Mobile Developer"

        if se_spec == "Database розробка":
            return "Data Engineer"

        if se_spec in [
            "Embedded",
            "Systems & Infrastructure",
            "Інше"
        ]:
            return "Software / Embedded Engineer"

        # ---------- Мовні категорії ----------

        if language in ["Java", "Kotlin", "Scala"]:
            return "Java Developer"

        if language == "Python":
            return "Python Developer"

        if language in ["C# NET", "C#  NET", "C#.NET"]:
            return ".NET Developer"

        return None

    # ==========================================================
    # DATA SCIENCE
    # ==========================================================

    if dou_cat == "Data Science":
        return "ML / AI Engineer"

    # ==========================================================
    # DEVOPS
    # ==========================================================

    if dou_cat == "DevOps & SRE":
        return "DevOps / SRE Engineer"

    # ==========================================================
    # SECURITY
    # ==========================================================

    if dou_cat == "Security":
        return "System Administrator / Network Engineer"

    # ==========================================================
    # ANALYST
    # ==========================================================

    if dou_cat == "Analyst":
        if position == "Business Analyst (BA)":
            return "Business Analyst"

        return "Data Analyst"

    # ==========================================================
    # QA
    # ==========================================================

    if dou_cat == "QA":
        manual_roles = {
            "Manual QA", "General QA", "Support QA", "Data QA", "Qality Control of Content Moderation",
            "QA Manager / QC Manager", "QA Manager  QC Manager"
        }

        automation_roles = {
            "Automation QA / AQA", "Automation QA  AQA", "SDET (Software Development Engineer in Test)",
            "Performance QA",  "Embedded QA", "Head of QA", "QA Lead"
        }

        if position in manual_roles:
            return "QA Manual Engineer"

        if position in automation_roles:
            return "QA Automation Engineer"

        return None

    # ==========================================================
    # DESIGN
    # ==========================================================

    if dou_cat in [ "UI/UX Design", "Game Design"]:
        return "UX/UI Designer"

    return None


def map_level(title: str) -> str | None:
    return LEVEL_MAPPING.get(str(title).strip())


# ── Завантаження файлів ───────────────────────────────────────────────────────
def load_dou_files(data_dir: str) -> pd.DataFrame:
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"CSV файл не знайдено у {data_dir}\n"
            f"Завантаж файл з https://github.com/devua/csv/tree/master/salaries"
        )

    if len(csv_files) > 1:
        raise ValueError( f"Очікувався один CSV файл у {data_dir}, але знайдено {len(csv_files)}")

    csv_file = csv_files[0]

    print(f"  [✓] Знайдено файл: {os.path.basename(csv_file)}")

    try:
        df = pd.read_csv(csv_file, encoding="utf-8")
        print(f"  [✓] Завантажено {len(df)} рядків")
    except Exception as e:
        raise RuntimeError(f"Не вдалося прочитати файл {csv_file}: {e}")

    # Парсимо дату 
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")

    # Тільки Україна
    if COL_LOCATION in df.columns:
        df = df[df[COL_LOCATION].str.strip().str.contains("В Україні", na=False)]

    df[COL_SALARY] = pd.to_numeric(df[COL_SALARY], errors="coerce")

    return df


# ── Аналітика ─────────────────────────────────────────────────────────────────

def calc_quantiles(salaries: pd.Series) -> dict:
    return {
        "q25":    int(salaries.quantile(0.25)),
        "median": int(salaries.median()),
        "q75":    int(salaries.quantile(0.75)),
        "mean":   int(salaries.mean()),
        "min":    int(salaries.min()),
        "max":    int(salaries.max()),
        "count":  int(len(salaries)),
    }


# Фіксовані діапазони для гістограми — однакові для всіх категорій,
# щоб графіки були порівнянними між собою
SALARY_BINS = [0, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 7000, 10000, 30001]

def calc_histogram(salaries: pd.Series) -> list[dict]:
    """
    Гістограма кількості анкет по фіксованих діапазонах зарплат.
    Приклад: {"range_from": 0, "range_to": 500, "label": "$0–500", "count": 12}
    """
    counts, edges = np.histogram(salaries, bins=SALARY_BINS)
    result = []
    for i in range(len(counts)):
        if counts[i] == 0:
            continue
        range_to = edges[i + 1]
        label = (
            f"${int(edges[i])}–{int(range_to)}"
            if range_to < 30001
            else f"${int(edges[i])}+"
        )
        result.append({
            "range_from": int(edges[i]),
            "range_to":   int(range_to) if range_to < 30001 else None,
            "label":      label,
            "count":      int(counts[i]),
        })
    return result


# ── Головна функція ───────────────────────────────────────────────────────────

def run_salary_analyzer(data_dir: str = DOU_DATA_DIR) -> str:
    os.makedirs(ANALYTICS_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"SALARY ANALYZER: завантажуємо дані DOU")
    print(f"{'='*60}\n")

    df = load_dou_files(data_dir)

    df["my_category"] = df.apply(map_category, axis=1)
    df["my_level"]    = df[COL_TITLE].apply(map_level)
    df = df.dropna(subset=["my_category", "my_level"])

    # Залишаємо тільки категорії з MY_CATEGORIES
    df = df[df["my_category"].isin(MY_CATEGORIES)]
    print(f"\nРядків після маппінгу: {len(df)}")

    salary_stats = {}

    for category in MY_CATEGORIES:
        cat_df = df[df["my_category"] == category]

        print(f"\n  {category} ({len(cat_df)} записів)")
        by_level = {}

        for level in ["Junior", "Middle", "Senior"]:
            level_df  = cat_df[cat_df["my_level"] == level]
            salaries  = level_df[COL_SALARY].dropna()

            print(f"    {level}: {len(salaries)} анкет, "
                  f"медіана=${int(salaries.median())}")

            by_level[level] = {
                **calc_quantiles(salaries),
                "histogram": calc_histogram(salaries),
            }

        # Загальна гістограма по категорії (всі рівні разом)
        all_salaries = cat_df[COL_SALARY].dropna()

        salary_stats[category] = {
            "total_records": int(len(cat_df)),
            "by_level":      by_level,
            "overall": {
                **calc_quantiles(all_salaries),
                "histogram": calc_histogram(all_salaries),
            },
        }

    # Зберігаємо
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "colected_at": df[COL_DATE].max().strftime("%Y-%m"),
        "source":       "DOU Salary Survey",
        "source_url":   "https://github.com/devua/csv/tree/master/salaries",
        "source_note":  (
            "Дані опитування DOU. "
            "При публікації обов'язково вказуйте DOU як джерело з активним посиланням."
        ),
        "location":     "В Україні",
        "currency":     "USD",
        "mapping_note": (
            "TypeScript/JavaScript → Frontend Developer (включає Node.js розробників). "
            "Точніший розподіл неможливий через структуру даних DOU."
        ),
        "salary_stats": salary_stats,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Збережено: {OUTPUT_FILE}")
    print(f"   Категорій: {len(salary_stats)} з {len(MY_CATEGORIES)}")
    print(f"{'='*60}")

    return OUTPUT_FILE


# ── Запуск окремо ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=DOU_DATA_DIR,
        help="Папка з CSV файлом DOU (default: data/dou_salaries/)"
    )
    args = parser.parse_args()
    run_salary_analyzer(args.data_dir)