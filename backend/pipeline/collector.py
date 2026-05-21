"""
collector.py — збір вакансій з Jooble API.

Відповідає за:
  1. Запити до Jooble API по містах
  2. Збереження raw snapshot (data/raw/)
  3. Merge з попереднім master (data/master/)

Запуск окремо:
    python pipeline/collector.py

Запуск як частина пайплайну:
    from pipeline.collector import run_collector
    run_collector()
"""

import json
import csv
import time
import re
import os
import glob
import http.client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Налаштування ──────────────────────────────────────────────────────────────

HOST = "ua.jooble.org"
API_KEY = os.getenv("JOOBLE_API_KEY")   # ключ з .env файлу
MAX_PAGES = 30
RESULTS_PER_PAGE = 30
PAUSE_BETWEEN_REQUESTS = 1.5
MAX_REQUESTS = 385
SEARCH_KEYWORD = "it"

UKRAINIAN_CITIES = [
    "Kyiv", "Lviv", "Kharkiv", "Dnipro", "Odesa",
    "Vinnytsia", "Ivano-Frankivsk", "Chernivtsi",
    "Cherkasy", "Ternopil", "Remote"
]

# Шляхи до папок — відносно кореня backend/
RAW_DIR    = "data/raw"
MASTER_DIR = "data/master"


# ── Допоміжні функції ─────────────────────────────────────────────────────────

def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(MASTER_DIR, exist_ok=True)


def clean_html(text: str) -> str:
    """Видаляє HTML теги та декодує спецсимволи."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    for old, new in {"&nbsp;": " ", "&amp;": "&", "&lt;": "<",
                     "&gt;": ">", "\\r\\n": " "}.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()


def find_latest_master() -> str | None:
    """Знаходить найсвіжіший master файл, ігноруючи сьогоднішній."""
    pattern    = os.path.join(MASTER_DIR, "ukraine_vacancies_*_merged.csv")
    candidates = [f for f in glob.glob(pattern) if _today() not in f]
    if not candidates:
        return None
    candidates.sort(reverse=True)
    latest = candidates[0]
    print(f"[✓] Знайдено попередній master: {latest}")
    return latest


# ── Запит до API ──────────────────────────────────────────────────────────────

def fetch_page(keyword: str, city: str, page: int) -> list[dict]:
    """Отримує одну сторінку вакансій з Jooble API."""
    try:
        connection = http.client.HTTPConnection(HOST)
        body = json.dumps({"keywords": keyword, "location": city, "page": page})
        connection.request("POST", f"/api/{API_KEY}", body,
                           {"Content-type": "application/json"})
        response = connection.getresponse()

        if response.status != 200:
            print(f"    [!] HTTP {response.status} | city={city} | page={page}")
            return []

        return json.loads(response.read().decode("utf-8")).get("jobs", [])

    except Exception as e:
        print(f"    [!] Помилка | city={city} | page={page}\n        {e}")
        return []


# ── Парсинг вакансії ──────────────────────────────────────────────────────────

def parse_vacancy(job: dict) -> dict:
    """Витягує і очищає поля з одного обʼєкта вакансії."""
    job_id = str(job.get("id", ""))
    if not job_id:
        # Резервний id якщо API не повернув
        job_id = (clean_html(job.get("title", ""))
                  + "_" + clean_html(job.get("company", ""))
                  + "_" + job.get("link", ""))
    return {
        "id":           job_id,
        "title":        clean_html(job.get("title", "")),
        "company":      clean_html(job.get("company", "")),
        "location":     clean_html(job.get("location", "")),
        "salary":       clean_html(job.get("salary", "")),
        "type":         clean_html(job.get("type", "")),
        "source":       job.get("source", ""),
        "link":         job.get("link", ""),
        "snippet":      clean_html(job.get("snippet", "")),
        "updated":      job.get("updated", "")[:10],
        "collected_at": _today(),
    }


# ── Збір вакансій ─────────────────────────────────────────────────────────────

def collect_all_vacancies() -> list[dict]:
    """Збирає вакансії по всіх містах і повертає дедублікований список."""
    all_vacancies = []
    seen_ids = set()
    current_request = 0
    global MAX_REQUESTS

    print("=" * 60)
    print("ПОЧАТОК ЗБОРУ ВАКАНСІЙ")
    print("=" * 60)

    for city in UKRAINIAN_CITIES:
        print(f"\n{'='*60}\nМІСТО: {city}\n{'='*60}")

        for page in range(1, MAX_PAGES + 1):

            if current_request >= MAX_REQUESTS:
                print("\n[STOP] Досягнуто ліміт запитів")
                return all_vacancies

            current_request += 1
            print(f"\nRequest #{current_request} | city={city} | page={page}")

            jobs = fetch_page(SEARCH_KEYWORD, city, page)

            if not jobs:
                print("      вакансій нема")
                break

            new_count  = 0
            dupl_count = 0

            for job in jobs:
                parsed = parse_vacancy(job)
                if parsed["id"] not in seen_ids:
                    seen_ids.add(parsed["id"])
                    all_vacancies.append(parsed)
                    new_count += 1
                else:
                    dupl_count += 1

            print(f"      +{new_count} нових | дублів={dupl_count}")

            if len(jobs) < RESULTS_PER_PAGE:
                print("      остання сторінка")
                break

            if new_count <= 3:
                print("      мало нових → stop")
                break

            time.sleep(PAUSE_BETWEEN_REQUESTS)

    MAX_REQUESTS -= current_request
    print(f"\n{'='*60}")
    print(f"ЗІБРАНО УНІКАЛЬНИХ: {len(all_vacancies)}")
    print(f"{'='*60}")
    return all_vacancies


# ── CSV утиліти ───────────────────────────────────────────────────────────────

def save_to_csv(vacancies: list[dict], filename: str):
    if not vacancies:
        print("Немає даних для збереження")
        return
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(vacancies[0].keys()))
        writer.writeheader()
        writer.writerows(vacancies)
    print(f"\n[✓] Збережено: {filename} ({len(vacancies)} вакансій)")


def load_csv(filename: str) -> list[dict]:
    if not os.path.exists(filename):
        print(f"[!] Файл не знайдено: {filename}")
        return []
    with open(filename, mode="r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ── Merge ─────────────────────────────────────────────────────────────────────

def merge_datasets(old_data: list[dict], new_data: list[dict]) -> list[dict]:
    """Обʼєднує старий master з новими вакансіями, без дублів."""
    merged   = []
    seen_ids = set()

    for row in old_data:
        if row["id"] not in seen_ids:
            seen_ids.add(row["id"])
            merged.append(row)

    new_unique = sum(
        1 for row in new_data
        if row["id"] not in seen_ids
        and not seen_ids.add(row["id"])  # side-effect: додає в seen_ids
        and merged.append(row) is None   # side-effect: додає в merged
    )

    print(f"\n{'='*60}\nMERGE РЕЗУЛЬТАТ")
    print(f"Старих:          {len(old_data)}")
    print(f"Нових:           {len(new_data)}")
    print(f"Нових унікальних:{new_unique}")
    print(f"Всього:          {len(merged)}")
    print(f"{'='*60}")
    return merged


# ── Точка входу ───────────────────────────────────────────────────────────────

def run_collector():
    """
    Головна функція колектора.
    Викликається з run_pipeline.py або напряму.
    """
    _ensure_dirs()
    today = _today()

    raw_path = f"{RAW_DIR}/ukraine_vacancies_{today}_raw.csv"
    merged_path = f"{MASTER_DIR}/ukraine_vacancies_{today}_merged.csv"

    # 1. Збір
    new_vacancies = collect_all_vacancies()

    # 2. Raw snapshot
    save_to_csv(new_vacancies, raw_path)

    # 3. Merge з попереднім master
    latest_master = find_latest_master()
    old_master    = load_csv(latest_master) if latest_master else []

    if not old_master:
        print("[i] Попереднього master не знайдено — створюємо з нуля")

    merged = merge_datasets(old_master, new_vacancies)

    # 4. Новий master
    save_to_csv(merged, merged_path)

    return merged_path   # повертаємо шлях для run_pipeline.py


if __name__ == "__main__":
    run_collector()
