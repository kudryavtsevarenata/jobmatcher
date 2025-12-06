import argparse
from pathlib import Path
import sys

from src.resume_parser import parse_resume
from src.vacancy_extractor import extract_vacancies
from src.llm_matcher import match_vacancies
from src.report_generator import generate_report

def main(resume_path: str, output_dir: str):
    print(">>> Parsing resume...")

    candidate = parse_resume(resume_path)
    print(f">>> Candidate profile ready for {candidate.desired_position}")

    vacancies = extract_vacancies(candidate)
    print(f">>> Found {len(vacancies)} from hh.ru")

    matches = match_vacancies(candidate, vacancies)
    print(f">>> Found {len(matches)} best matches")

    generate_report(candidate, matches, output_dir)
    print(f">>> Report in {output_dir}/JobMatch_Report.pdf")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Анализ резюме и подбор вакансий с hh.ru'
    )

    parser.add_argument(
        '-r', '--resume',
        type=str,
        default='resume/example_resume.txt',
        help='Путь к файлу резюме (по умолчанию: resume/example_resume.txt)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='results',
        help='Директория для сохранения результатов (по умолчанию: results)'
    )

    args = parser.parse_args()

    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"Ошибка: файл '{resume_path}' не найден")
        sys.exit(1)

    main(args.resume, args.output)
