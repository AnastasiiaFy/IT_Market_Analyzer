"""
run_pipeline.py — запускає весь пайплайн по черзі.

Порядок виконання:
  1. collector.py      → збір вакансій → data/raw/ + data/master/
  2. processor.py      → обробка даних → data/final/
  3. skills_extractor.py → витягування скілів → skill_map.json у analytics/
  4. analyzer.py       → генерація аналітики → analytics/ (summary.json - топ5 категорій за кількістю вакансій; vacancy_stats.json - повна аналітика)
  5. salary_analyzer.py → аналіз зарплат на основі даних DOU (analytics/salary_stats.json) 

Запуск:
    cd backend
    python pipeline/run_pipeline.py
"""

from collector import run_collector
from processor import run_processor        
from skills_extractor import run_skills_extractor 
from analyzer import run_analyzer         
from salary_analyzer import run_salary_analyzer

from datetime import datetime


def main():
    start = datetime.now()
    print(f"\n{'='*60}")
    print(f"ЗАПУСК ПАЙПЛАЙНУ: {start.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # Крок 1: збір
    # print("КРОК 1: Збір вакансій")
    # merged_path = run_collector()
    # print(f"[✓] Колектор завершено → {merged_path}\n")

    #merged_path = "data/master/ukraine_vacancies_2026-05-18_merged.csv"

    # Крок 2: обробка 
    #print("КРОК 2: Обробка даних")
    #final_path = run_processor(merged_path)
    #print(f"[✓] Процесор завершено → {final_path}\n")

    final_path = "data/final/ukraine_vacancies_2026-05-18_final.csv"

    # Крок 3: скіли 
    print("КРОК 3: Витягування скілів")
    final_path = run_skills_extractor(final_path)
    print(f"[✓] Скіли витягнуто → {final_path}\n")

    # Крок 4: аналітика 
    #print("КРОК 4: Генерація аналітики")
    #run_analyzer(final_path)
    #print("[✓] Аналітику згенеровано\n")

    # Крок 5: зарплати
    #print("КРОК 5: Генерація зарплатної аналітики DOU")
    #salary_file = run_salary_analyzer()
    #print(f"[✓] Зарплатну аналітику згенеровано → {salary_file}\n")

    elapsed = (datetime.now() - start).seconds
    print(f"{'='*60}")
    print(f"ПАЙПЛАЙН ЗАВЕРШЕНО за {elapsed} сек")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()