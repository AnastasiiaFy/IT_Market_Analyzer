"""
skills_extractor.py — витягування технологій з назв вакансій і генерація skill_map.json.

Логіка:
  1. Для кожної вакансії витягуємо технології з normalized_title через TECH_PATTERNS
  2. Групуємо за (category, level) і рахуємо Counter()
  3. Додаємо BASE_STACK (експертний словник) окремим полем
  4. Зберігаємо skill_map.json у analytics/analytics/

Запуск окремо:
    python pipeline/skills_extractor.py --input data/final/vacancies_2026-05-18_final.csv

Запуск як частина пайплайну:
    from pipeline.skills_extractor import run_skills_extractor
    run_skills_extractor(final_path)
"""

# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
from collections import Counter
from datetime import datetime

import pandas as pd

# ── Шляхи ────────────────────────────────────────────────────────────────────

ANALYTICS_DIR = "analytics"
OUTPUT_FILE   = f"{ANALYTICS_DIR}/skill_map.json"
LEVELS_ORDER  = ["Junior", "Middle", "Senior"]

MUST_HAVE_THRESHOLD = 5


# ── Словник технологій ────────────────────────────────────────────────────────
# Формат: "Канонічна назва": [патерни для re.search в normalized_title]

TECH_PATTERNS = {
    # Мови програмування
    "Python":        [r"python"],
    "JavaScript":    [r"javascript", r"\bjs\b"],
    "TypeScript":    [r"typescript", r"\bts\b"],
    "PHP":           [r"\bphp\b"],
    "Java":          [r"\bjava\b"],
    "Kotlin":        [r"kotlin"],
    "Swift":         [r"swift"],
    "Go":            [r"\bgolang\b", r"\bgo\b developer", r"\bgo\b engineer"],
    "Rust":          [r"\brust\b"],
    "Ruby":          [r"\bruby\b"],
    "C#":            [r"\bc#\b", r"\bc sharp\b"],
    "C++":           [r"c\+\+"],
    "Scala":         [r"\bscala\b"],
    "Dart":          [r"\bdart\b"],

    # Frontend фреймворки
    "React":         [r"\breact\b"],
    "Vue":           [r"\bvue\b"],
    "Angular":       [r"\bangular\b"],
    "Next.js":       [r"next\.js", r"nextjs"],
    "Nuxt.js":       [r"nuxt\.js", r"nuxtjs"],
    "Svelte":        [r"\bsvelte\b"],

    # Backend фреймворки
    "Node.js":       [r"node\.js", r"\bnodejs\b"],
    "Django":        [r"\bdjango\b"],
    "FastAPI":       [r"fastapi"],
    "Flask":         [r"\bflask\b"],
    "Laravel":       [r"laravel"],
    "Symfony":       [r"symfony"],
    "Spring":        [r"\bspring\b"],
    "Rails":         [r"\brails\b", r"ruby on rails"],
    "ASP.NET":       [r"asp\.net"],
    ".NET":          [r"\.net\b"],
    "NestJS":        [r"nestjs", r"nest\.js"],

    # Мобільна розробка
    "Flutter":       [r"flutter"],
    "React Native":  [r"react native"],
    "MAUI":          [r"\bmaui\b"],

    # Бази даних
    "PostgreSQL":    [r"postgresql", r"\bpostgres\b"],
    "MySQL":         [r"mysql"],
    "MongoDB":       [r"mongodb", r"\bmongo\b"],
    "Redis":         [r"\bredis\b"],
    "Elasticsearch": [r"elasticsearch"],
    "Oracle":        [r"\boracle\b"],
    "MSSQL":         [r"mssql", r"sql server"],
    "ClickHouse":    [r"clickhouse"],

    # DevOps / Cloud
    "Docker":        [r"\bdocker\b"],
    "Kubernetes":    [r"kubernetes", r"\bk8s\b"],
    "AWS":           [r"\baws\b"],
    "GCP":           [r"\bgcp\b", r"google cloud"],
    "Azure":         [r"\bazure\b"],
    "Terraform":     [r"terraform"],
    "Ansible":       [r"ansible"],

    # Data / ML
    "TensorFlow":    [r"tensorflow"],
    "PyTorch":       [r"pytorch"],
    "Spark":         [r"\bspark\b"],
    "Airflow":       [r"airflow"],
    "dbt":           [r"\bdbt\b"],
    "Tableau":       [r"tableau"],
    "Power BI":      [r"power bi"],

    # QA інструменти
    "Selenium":      [r"selenium"],
    "Cypress":       [r"cypress"],
    "Playwright":    [r"playwright"],
    "Appium":        [r"appium"],

    # Інші
    "GraphQL":       [r"graphql"],
    "Kafka":         [r"\bkafka\b"],
    "Figma":         [r"\bfigma\b"],
}



BASE_STACK = {
    "Data Analyst": {
        "Junior": [
            "SQL", "Excel", "Python/R", "Візуалізація даних",
            "Основи статистики", "Power BI/Tableau"
        ],
        "Middle": [
            "Tableau/Power BI", "Статистика",
            "A/B тестування", "ETL основи",
            "Pandas", "Бізнес-метрики"
        ],
        "Senior": [
            "ML основи", "Бізнес-аналітика",
            "Прогнозування", "Data storytelling",
            "Аналітична стратегія", "Менторинг"
        ],
    },

    "Data Engineer": {
        "Junior": [
            "SQL", "Python", "Git", "ETL основи",
            "PostgreSQL", "Linux основи"
        ],
        "Middle": [
            "Spark", "Airflow", "dbt",
            "Data Warehouse", "Docker",
            "Хмарні платформи"
        ],
        "Senior": [
            "Архітектура даних", "Kafka",
            "Streaming systems", "Kubernetes",
            "Data Lake", "Оптимізація пайплайнів"
        ],
    },

    "ML / AI Engineer": {
        "Junior": [
            "Python", "Математика/Статистика",
            "Pandas", "Scikit-learn",
            "NumPy", "Git"
        ],
        "Middle": [
            "TensorFlow/PyTorch", "Docker",
            "SQL", "MLOps основи",
            "Feature Engineering", "FastAPI/Flask"
        ],
        "Senior": [
            "Архітектура ML систем", "MLOps",
            "LLM", "Хмарні платформи",
            "Kubernetes", "Distributed Training"
        ],
    },

    "QA Manual Engineer": {
        "Junior": [
            "Тест-дизайн", "Баг-репорти",
            "Jira", "SQL основи",
            "SDLC/STLC", "Основи API"
        ],
        "Middle": [
            "SQL", "API тестування",
            "Postman", "Charles/Fiddler",
            "Тестова документація", "Тестування БД"
        ],
        "Senior": [
            "Тест-стратегія", "Управління QA командою",
            "Метрики якості", "Risk management",
            "Побудова QA процесів"
        ],
    },

    "QA Automation Engineer": {
        "Junior": [
            "Selenium/Cypress", "Git",
            "Основи програмування", "Тест-дизайн",
            "ООП", "API тестування"
        ],
        "Middle": [
            "Selenium/Cypress/Playwright",
            "Java/Python/JavaScript",
            "CI/CD", "Docker",
            "Test Frameworks"
        ],
        "Senior": [
            "Архітектура тест-фреймворку",
            "Управління QA командою",
            "Performance testing",
            "TestOps", "Автоматизація процесів"
        ],
    },

    "Full Stack Developer": {
        "Junior": [
            "HTML", "CSS", "JavaScript",
            "Git", "SQL", "REST API",
            "React/Vue", "Node.js основи"
        ],
        "Middle": [
            "TypeScript", "Docker",
            "JWT/Auth", "NoSQL",
            "Тестування", "CI/CD"
        ],
        "Senior": [
            "Архітектура систем", "Мікросервіси",
            "System Design", "Kubernetes",
            "Оптимізація продуктивності",
            "Менторинг"
        ],
    },

    "Frontend Developer": {
        "Junior": [
            "HTML", "CSS", "JavaScript",
            "Git", "React/Vue/Angular",
            "REST API", "Адаптивна верстка"
        ],
        "Middle": [
            "TypeScript", "Webpack/Vite",
            "Тестування", "State Management",
            "Next.js/Nuxt"
        ],
        "Senior": [
            "Архітектура фронтенду", "CI/CD",
            "Оптимізація продуктивності",
            "Design Systems", "SSR/SSG",
            "Менторинг"
        ],
    },

    "Backend Developer": {
        "Junior": [
            "Git", "SQL", "REST API",
            "Linux основи", "ООП",
            "Node.js/Java/Python"
        ],
        "Middle": [
            "SQL/NoSQL", "Docker",
            "CI/CD", "Тестування",
            "Redis", "Message Brokers"
        ],
        "Senior": [
            "System Design", "Мікросервіси",
            "Kubernetes", "Безпека",
            "Масштабування", "Event-driven architecture"
        ],
    },

    "Mobile Developer": {
        "Junior": [
            "Git", "REST API",
            "Основи мобільної розробки",
            "Kotlin/Swift/Flutter",
            "ООП"
        ],
        "Middle": [
            "Тестування", "CI/CD",
            "Публікація в сторах",
            "Firebase", "Архітектурні патерни"
        ],
        "Senior": [
            "Архітектура мобільних додатків",
            "Оптимізація", "Безпека",
            "Performance tuning",
            "Менторинг"
        ],
    },

    "Java Developer": {
        "Junior": [
            "Java", "Git", "SQL",
            "ООП", "Spring основи",
            "Maven/Gradle"
        ],
        "Middle": [
            "Spring Boot", "SQL/NoSQL",
            "Docker", "Тестування",
            "Hibernate", "REST API"
        ],
        "Senior": [
            "Spring", "Мікросервіси",
            "Архітектура", "Kubernetes",
            "Kafka", "System Design"
        ],
    },

    "Python Developer": {
        "Junior": [
            "Python", "Git", "SQL",
            "ООП основи", "HTTP/REST",
            "Linux основи"
        ],
        "Middle": [
            "Django/FastAPI",
            "PostgreSQL", "Docker",
            "Тестування", "Redis"
        ],
        "Senior": [
            "Архітектура", "Мікросервіси",
            "Kubernetes", "CI/CD",
            "Async programming", "System Design"
        ],
    },

    ".NET Developer": {
        "Junior": [
            "C#", ".NET", "Git",
            "SQL", "ООП",
            "ASP.NET основи"
        ],
        "Middle": [
            "ASP.NET", "PostgreSQL/MSSQL",
            "Docker", "Тестування",
            "Entity Framework", "REST API"
        ],
        "Senior": [
            "Архітектура", "Мікросервіси",
            "Azure/AWS", "Kubernetes",
            "System Design", "Message Brokers"
        ],
    },

    "Software / Embedded Engineer": {
        "Junior": [
            "C/C++", "Git", "Linux",
            "Мікроконтролери", "Основи електроніки",
            "UART/I2C/SPI"
        ],
        "Middle": [
            "RTOS", "STM32/ESP32",
            "Embedded Linux", "Debugging",
            "ARM Architecture", "IoT основи"
        ],
        "Senior": [
            "Архітектура embedded систем",
            "Real-time systems",
            "Оптимізація продуктивності",
            "Безпека embedded систем",
            "Hardware/Software integration"
        ],
    },

    "DevOps / SRE Engineer": {
        "Junior": [
            "Linux", "Git", "Docker",
            "Bash", "Основи мереж",
            "CI/CD основи"
        ],
        "Middle": [
            "Kubernetes", "CI/CD",
            "Terraform", "AWS/GCP/Azure",
            "Моніторинг", "Ansible"
        ],
        "Senior": [
            "Архітектура хмарних систем",
            "SRE практики", "Безпека",
            "Observability", "Disaster Recovery",
            "Cost Optimization"
        ],
    },

    "System Administrator / Network Engineer": {
        "Junior": [
            "Linux/Windows Server",
            "TCP/IP", "DNS/DHCP",
            "Bash/PowerShell",
            "Основи мереж", "Віртуалізація"
        ],
        "Middle": [
            "Cisco/MikroTik", "VPN",
            "Active Directory", "Моніторинг",
            "Firewall", "Virtualization"
        ],
        "Senior": [
            "Архітектура мереж",
            "High Availability",
            "Network Security",
            "Infrastructure Automation",
            "Disaster Recovery"
        ],
    },

    "Cloud Engineer": {
        "Junior": [
            "Linux", "Git", "Docker",
            "AWS/Azure/GCP",
            "Основи мереж", "Terraform основи"
        ],
        "Middle": [
            "Kubernetes", "Terraform",
            "CI/CD", "Monitoring",
            "Cloud Security", "Serverless"
        ],
        "Senior": [
            "Архітектура хмарних систем",
            "Multi-cloud", "Cost Optimization",
            "Disaster Recovery",
            "Infrastructure as Code strategy"
        ],
    },

    "Business Analyst": {
        "Junior": [
            "Вимоги", "BPMN",
            "Jira", "SQL основи",
            "User Stories", "Confluence"
        ],
        "Middle": [
            "SQL", "Jira/Confluence",
            "Прототипування", "UML",
            "Stakeholder management",
            "BRD/SRS документація"
        ],
        "Senior": [
            "Бізнес-стратегія",
            "Архітектура процесів",
            "Управління вимогами",
            "Process Optimization",
            "Менторинг"
        ],
    },

    "UX/UI Designer": {
        "Junior": [
            "Figma", "UX основи",
            "Прототипування", "Композиція",
            "Typography", "Color theory"
        ],
        "Middle": [
            "UX дослідження",
            "Дизайн-системи",
            "Юзабіліті тестування",
            "Auto Layout", "Responsive Design"
        ],
        "Senior": [
            "Дизайн-стратегія",
            "Управління командою",
            "Product Thinking",
            "Accessibility", "DesignOps"
        ],
    },
}



# ── Витягування технологій з одного title ─────────────────────────────────────

def extract_techs_from_title(normalized_title: str) -> list[str]:
    """
    Шукає технології в normalized_title за TECH_PATTERNS.
    Повертає список канонічних назв знайдених технологій.

    Приклад:
        "junior node.js developer"       → ["Node.js"]
        "senior python django engineer"  → ["Python", "Django"]
        "junior backend developer"       → []
    """
    found = []
    for tech_name, patterns in TECH_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized_title, re.IGNORECASE):
                found.append(tech_name)
                break  # не дублюємо одну технологію
    return found


# ── Агрегація по групі ────────────────────────────────────────────────────────

def aggregate_group(titles: list[str]) -> Counter:
    """Рахує частоту кожної технології по списку normalized_title."""
    counter = Counter()
    for title in titles:
        counter.update(extract_techs_from_title(title))
    return counter


# ── Форматування списку скілів (must_have і nice_to_have.) ────────────────────────────────────────────────
def split_must_nice(
    counter: Counter,
    total: int,
    threshold_pct: int = MUST_HAVE_THRESHOLD
):
    """
    Розділяє навички на must_have і nice_to_have.
    """

    must = []
    nice = []

    for skill, count in counter.most_common():

        if count < 2:
            continue

        pct = round(count / total * 100) if total > 0 else 0

        entry = {
            "skill": skill,
            "count": count,
            "percent": pct,
        }

        if pct >= threshold_pct:
            must.append(entry)
        else:
            nice.append(entry)

    return must, nice


# ──────────────────────────────────────────────────────────────────────────────
# DEDUPLICATION
# ──────────────────────────────────────────────────────────────────────────────

def deduplicate_skill_objects( skills: list[dict], already_seen: set[str]) -> list[dict]:
    """
    Видаляє навички які вже були на попередніх рівнях.
    """

    result = []

    for item in skills:

        skill_lower = item["skill"].lower()

        if skill_lower in already_seen:
            continue

        result.append(item)

    return result


def deduplicate_base_stack( base_stack: list[str], current_from_titles: set[str], already_seen: set[str]) -> list[str]:
    """
    Видаляє:
      1. навички що вже є у from_titles
      2. навички що вже були на попередніх рівнях
    """

    result = []

    current_from_titles = {
        s.lower()
        for s in current_from_titles
    }

    for skill in base_stack:

        skill_lower = skill.lower()

        if skill_lower in current_from_titles:
            continue

        if skill_lower in already_seen:
            continue

        result.append(skill)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# BUILD CATEGORY MAP
# ──────────────────────────────────────────────────────────────────────────────
def build_category_skill_map(category: str, df_cat: pd.DataFrame) -> dict:

    result = {}

    # GLOBAL skill history
    # використовується для deduplicate між рівнями
    previous_all_skills = set()

    for level in LEVELS_ORDER:

        level_df = df_cat[df_cat["level"] == level]

        if level_df.empty:
            continue

        titles = (
            level_df["normalized_title"]
            .dropna()
            .tolist()
        )

        total = len(titles)

        counter = aggregate_group(titles)

        # MUST / NICE
        must_from, nice_from = split_must_nice(counter, total)

        # REMOVE duplicates from previous levels
        must_from = deduplicate_skill_objects(
            must_from,
            previous_all_skills
        )

        nice_from = deduplicate_skill_objects(
            nice_from,
            previous_all_skills
        )

        # CURRENT from_titles skills
        current_from_titles = {
            item["skill"]
            for item in must_from + nice_from
        }

        # RAW BASE STACK
        raw_base = (
            BASE_STACK
            .get(category, {})
            .get(level, [])
        )

        # CLEAN BASE STACK
        clean_base = deduplicate_base_stack(
            raw_base,
            current_from_titles,
            previous_all_skills
        )

        # UPDATE history
        previous_all_skills.update(
            s["skill"].lower()
            for s in must_from + nice_from
        )

        previous_all_skills.update(
            s.lower()
            for s in clean_base
        )

        result[level] = {
            "total_vacancies": total,

            "must_have": {
                "from_titles": must_from,
                "base_stack": clean_base,
            },

            "nice_to_have": {
                "from_titles": nice_from,
                "base_stack": [],
            },
        }

    return result


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def run_skills_extractor(input_path: str) -> str:

    os.makedirs(ANALYTICS_DIR, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"SKILLS EXTRACTOR")
    print(f"{'=' * 60}")

    print(f"\nЧитаємо: {input_path}")

    df = pd.read_csv(
        input_path,
        encoding="utf-8-sig"
    )

    print(f"Завантажено вакансій: {len(df)}")

    required = {
        "normalized_title",
        "category",
        "level"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Відсутні колонки: {missing}"
        )

    skill_map = {}

    categories = df["category"].unique()

    print(f"Категорій: {len(categories)}")

    for category in categories:

        print(f"\n→ {category}")

        cat_df = df[
            df["category"] == category
        ]

        skill_map[category] = build_category_skill_map(
            category,
            cat_df
        )

    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d"),

        "vacancies_analyzed": len(df),

        "must_have_threshold_pct": MUST_HAVE_THRESHOLD,

        "note": (
            "from_titles — технології витягнуті з назв вакансій. "
            "base_stack — експертний словник базових навичок. "
            "Навички між рівнями не дублюються."
        ),

        "skill_map": skill_map,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"\n✅ Збережено: {OUTPUT_FILE}")

    return OUTPUT_FILE


# ── Запуск окремо ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", required=True,
        help="Шлях до final CSV"
    )
    args = parser.parse_args()
    run_skills_extractor(args.input)