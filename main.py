from src.resume_parser import parse_resume
from src.vacancy_extractor import extract_vacancies

def main():
    print(">>> Parsing resume...")

    candidate = parse_resume("resume/example_resume.txt")
    print(f">>> Candidate profile ready for {candidate.desired_position}")

    vacancies = extract_vacancies(candidate)
    print(f">>> Found {len(vacancies)} from hh.ru")

if __name__ == "__main__":
    main()
