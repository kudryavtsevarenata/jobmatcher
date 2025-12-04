import requests
from bs4 import BeautifulSoup
from config import MAX_VACANCIES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

EXPERIENCE_MAP = {
    (0, 1): "noExperience",
    (1, 3): "between1And3",
    (3, 6): "between3And6",
    (6, float('inf')): "moreThan6"
}

def get_experience_param(years: float):
    for (low, high), param in EXPERIENCE_MAP.items():
        if low <= years < high:
            return param
    return "between1And3"


def extract_vacancies(candidate) -> list:
    vacancies = []

    exp_param = get_experience_param(candidate.years_experience)

    salary_from = None
    if candidate.salary_expectation:
        try:
            salary_from = int(candidate.salary_expectation)
        except Exception as e:
            salary_from = None

    base_url = "https://hh.ru/search/vacancy"
    params = {
        "text": candidate.desired_position,
        "experience": exp_param,
        "order_by": "relevance",
        "items_on_page": "50",
        "no_magic": "true"
    }

    if salary_from:
        params["salary"] = str(salary_from)
        params["only_with_salary"] = "true"

    try:
        response = requests.get(base_url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup.find_all("div", {"data-qa": "vacancy-serp__vacancy"}):
            title_tag = item.find("span", {"data-qa": "serp-item__title-text"})
            href_tag = item.find("a", {"data-qa": "serp-item__title"})
            company_tag = item.find("span", {"data-qa": "vacancy-serp__vacancy-employer-text"})
            salary_tag = item.find("span", {"class": "magritte-text___pbpft_4-3-5 magritte-text_style-primary___AQ7MW_4-3-5 magritte-text_typography-label-1-regular___pi3R-_4-3-5"}) # TODO

            if title_tag:
                vacancies.append({
                    "title": title_tag.get_text(strip=True),
                    "company": company_tag.get_text(strip=True),
                    "salary": salary_tag.get_text(strip=True) if salary_tag else "N/A",
                    "url": href_tag["href"].split("?")[0],
                })
            if len(vacancies) >= MAX_VACANCIES:
                break
    except Exception as e:
        print(f">>> Error while parse hh.ru: {e}")

    return vacancies
