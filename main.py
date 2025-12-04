from src.resume_parser import parse_resume
from src.vacancy_extractor import extract_vacancies
from src.llm_matcher import match_vacancies
from src.report_generator import generate_report

def main():
    print(">>> Parsing resume...")

    candidate = parse_resume("resume/example_resume.txt")
    print(f">>> Candidate profile ready for {candidate.desired_position}")

    vacancies = extract_vacancies(candidate)
    print(f">>> Found {len(vacancies)} from hh.ru")

    matches = match_vacancies(candidate, vacancies)
    print(f">>> Found {len(matches)} best matches")

    generate_report(candidate, matches)
    print(">>> Report in results/JobMatch_Report.pdf")

if __name__ == "__main__":
    main()
