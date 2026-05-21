"""
processor.py — обробка сирих вакансій.

Відповідає за:
  1. Нормалізацію та класифікацію title (category, level)
  2. Multi-hot encoding типу зайнятості
  3. Збереження обробленого файлу → data/final/

Запуск окремо:
    python pipeline/processor.py --input data/master/ukraine_vacancies_2026-05-18_merged.csv

Запуск як частина пайплайну:
    from pipeline.processor import run_processor
    run_processor(merged_path)
"""

import re
import os
import argparse
import pandas as pd
from datetime import datetime

# ── Шляхи ────────────────────────────────────────────────────────────────────

FINAL_DIR = "data/final"

# ── Маппінги ──────────────────────────────────────────────────────────────────

EXPERIENCE_LEVELS = {
    'Junior': [
        'junior', 'jr', 'intern', 'trainee', 'internship',
        'стажер', 'стажерка', 'молодший', 'початківець'
    ],
    'Middle': [
        'middle', 'mid', r'middle\+', r'mid\+', 'middle/senior',
        'midsr', r'middle\+\+', 'regular'
    ],
    'Senior': [
        'senior', 'sr', 'lead', 'principal', 'expert',
        'architect', 'head', 'chief', 'director',
        'провідний', 'старший'
    ],
}

# ВАЖЛИВО: порядок має значення — специфічніші категорії вище загальних
JOB_CATEGORIES = {

    # ── Дані (перед ML щоб 'data' не потрапив не туди) ──────────────────────
    'Data Analyst': [
        'data analyst', 'аналітик даних', 'bi analyst',
        'business intelligence analyst', 'product analyst',
        'marketing analyst', 'fraud data analyst',
        'data quality analyst', 'sql analyst', 'дата аналітик',
    ],
    'Data Engineer': [
        'data engineer', 'data integration', 'data platform',
        'dwh engineer', 'etl developer',
    ],
    'ML / AI Engineer': [
        'machine learning', 'ml engineer', 'ai engineer',
        'artificial intelligence', 'data scientist', 'data science',
        'computer vision', 'nlp engineer', 'llm engineer', 'rag',
    ],

    # ── QA (Automation перед Manual щоб 'qa automation' не впав у Manual) ───
    'QA Automation Engineer': [
        'automation qa', 'qa automation', 'aqa',
        'automation tester', 'test automation engineer',
    ],
    'QA Manual Engineer': [
        'manual qa', 'qa manual', 'qa tester', 'qa engineer',
        'тестувальник', 'quality assurance',
    ],

    # ── Розробка ─────────────────────────────────────────────────────────────
    'Full Stack Developer': [
        'fullstack', 'full-stack', 'full stack',
    ],
    'Frontend Developer': [
        'frontend', 'front-end', 'front end',
        'react developer', 'angular developer', 'vue developer',
        'javascript engineer', 'js engineer',
    ],
    'Backend Developer': [
        'backend', 'back-end', 'back end',
        'node.js developer', 'php developer', 'laravel developer',
        'symfony developer', 'golang developer', 'go developer',
        'ruby developer', 'rails developer', 'rust developer',
    ],
    'Mobile Developer': [
        'ios developer', 'android developer', 'flutter developer',
        'react native developer', 'mobile developer',
        'mobile engineer', 'maui developer',
    ],
    'Java Developer': [
        'java developer', 'java engineer', 'java architect',
        'spring developer',
    ],
    'Python Developer': [
        'python developer', 'python engineer',
        'django developer', 'flask developer', 'fastapi developer',
    ],
    '.NET Developer': [
        '.net developer', '.net engineer', 'c# developer',
        'c sharp developer', 'blazor developer', 'asp.net developer',
    ],
    'Software / Embedded Engineer': [
        'software engineer', 'software developer',
        r'c\+\+ developer', r'c\+\+ engineer', 'embedded engineer',
        'embedded developer', 'hardware engineer',
        'fpga engineer', 'firmware engineer', 'delphi developer',
    ],

    # ── Інфраструктура ───────────────────────────────────────────────────────
    'DevOps / SRE Engineer': [
        'devops engineer', 'sre engineer', 'site reliability engineer',
        'platform engineer', 'infrastructure engineer',
    ],
    'System Administrator / Network Engineer': [
        'system administrator', 'системний адміністратор', 'sysadmin',
        'network engineer', 'мережевий інженер',
        'database administrator', 'dba engineer',
        'windows administrator', 'linux administrator',
    ],
    'Cloud Engineer': [
        'cloud engineer', 'aws engineer', 'azure engineer',
        'gcp engineer', 'cloud architect',
    ],

    # ── Управління ───────────────────────────────────────────────────────────
    'Business Analyst': [
        'business analyst', 'бізнес-аналітик', 'бізнес аналітик',
        'it business analyst', 'system analyst', 'системний аналітик',
    ],

    # ── Дизайн ───────────────────────────────────────────────────────────────
    'UX/UI Designer': [
        'uiux designer', 'uxui designer', 'ux designer', 'ui designer',
        'product designer', 'web designer',
    ],
}

TYPE_MAPPING = {
    'Повний робочий день': 'full_time',
    'Часткова зайнятість': 'part_time',
    'Стажування':          'internship',
    'Тимчасова зайнятість':'temporary',
}

INTERNSHIP_PATTERNS = [
    'intern', 'internship', 'trainee',
    'стажер', 'стажерка',
]

PART_TIME_PATTERNS = [
    'part time', 'part-time', 'freelance', 'contract',
    'неповна зайнятість', 'часткова зайнятість',
]


# ── Нормалізація title ────────────────────────────────────────────────────────

def normalize_title(title: str) -> str:
    """Приводить назву вакансії до уніфікованого вигляду."""
    if not title or not isinstance(title, str):
        return ''

    title = title.lower()

    # Захищаємо сталі IT-терміни з косою рискою
    title = re.sub(r'\bui/ux\b',  'uiux',  title)
    title = re.sub(r'\bux/ui\b',  'uiux',  title)
    title = re.sub(r'\bci/cd\b',  'cicd',  title)
    title = re.sub(r'\bba/sa\b',  'basa',  title)
    title = re.sub(r'\bmid/sr\b', 'midsr', title)

    # Решту слешів → пробіл
    title = title.replace('/', ' ')

    # Видаляємо дужки та спецсимволи
    title = re.sub(r'[()\[\]{}]', '', title)
    title = re.sub(r'[^\w\s\-.#+]', ' ', title)
    title = re.sub(r'\s+', ' ', title)

    return title.strip()


# ── Визначення рівня ──────────────────────────────────────────────────────────

def extract_level(normalized_title: str) -> str:
    """
    Визначає рівень спеціалізації з нормалізованого title.
    """
    for level, patterns in EXPERIENCE_LEVELS.items():
        for pattern in patterns:
            if re.search(rf'\b{pattern}\b', normalized_title):
                return level
    return 'Middle'


# ── Визначення категорії ──────────────────────────────────────────────────────

def extract_category(normalized_title: str) -> str:
    """
    Визначає категорію з нормалізованого title.
    Повертає 'Other' якщо жоден патерн не підійшов.
    """
    for category, patterns in JOB_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, normalized_title):
                return category
    return 'Other'


# ── Обробка одного title ──────────────────────────────────────────────────────

def process_title(raw_title: str) -> dict:
    normalized = normalize_title(raw_title)
    return {
        'normalized_title': normalized,
        'level':            extract_level(normalized),
        'category':         extract_category(normalized),
    }


# ── Обробка типу зайнятості ───────────────────────────────────────────────────

def process_employment_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-hot encoding типу зайнятості.
    Додає колонки: full_time, part_time, internship, temporary.
    """
    df = df.copy()
    df['type'] = df['type'].fillna('Повний робочий день')

    # Ініціалізуємо колонки нулями
    for col in set(TYPE_MAPPING.values()):
        df[col] = 0

    # Encoding з поля 'type'
    for original, col in TYPE_MAPPING.items():
        mask = df['type'].str.contains(original, regex=False, na=False).astype(int)
        df[col] = df[col] | mask

    # Додаткове виявлення з назви вакансії
    title_lower = df['title'].str.lower()

    internship_mask = title_lower.str.contains(
        '|'.join(INTERNSHIP_PATTERNS), regex=True, na=False
    ).astype(int)
    df['internship'] = df['internship'] | internship_mask

    part_time_mask = title_lower.str.contains(
        '|'.join(PART_TIME_PATTERNS), regex=True, na=False
    ).astype(int)
    df['part_time'] = df['part_time'] | part_time_mask

    df = df.drop(columns=['type'])
    return df


# ── Головна функція ───────────────────────────────────────────────────────────

def run_processor(input_path: str) -> str:
    """
    Читає merged CSV, обробляє і зберігає у data/final/.
    Повертає шлях до готового файлу для run_pipeline.py.
    """
    os.makedirs(FINAL_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"PROCESSOR: читаємо {input_path}")
    print(f"{'='*60}")

    df = pd.read_csv(input_path, encoding='utf-8-sig')
    print(f"Завантажено рядків: {len(df)}")

    # 1. Прибираємо непотрібні колонки
    drop_cols = [c for c in ['city_query', 'keyword_query', 'source', 'link', 'snippet']
                 if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # 2. Нормалізація дат
    df['updated']      = df['updated'].astype(str).str[:10]
    df['collected_at'] = df['collected_at'].astype(str).str[:10]

    # 3. Обробка title → normalized_title, level, category
    print("Обробка title...")
    df[['normalized_title', 'level', 'category']] = (
        df['title'].apply(process_title).apply(pd.Series)
    )

    # 4. Фільтруємо 'Other'
    before = len(df)
    df = df[df['category'] != 'Other'].copy()
    print(f"Відфільтровано 'Other': {before - len(df)} рядків → залишилось {len(df)}")

    # 5. Тип зайнятості
    print("Обробка типу зайнятості...")
    df = process_employment_type(df)

    # 6. Фінальний порядок колонок
    final_cols = [
        'id', 'title', 'normalized_title', 'level', 'category',
        'company', 'location', 'salary',
        'full_time', 'part_time', 'internship', 'temporary',
        'updated', 'collected_at'
    ]
    # Додаємо тільки ті колонки що є в df
    df = df[[c for c in final_cols if c in df.columns]]

    # 7. Збереження
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = f"{FINAL_DIR}/ukraine_vacancies_{today}_final.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n[✓] Збережено: {output_path} ({len(df)} вакансій)")
    print(f"{'='*60}")

    return output_path


# ── Запуск окремо ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', required=True,
        help='Шлях до merged CSV файлу, напр. data/master/ukraine_vacancies_2026-05-18_merged.csv'
    )
    args = parser.parse_args()
    run_processor(args.input)
