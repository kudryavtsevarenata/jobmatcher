import ollama
import json
from src.models import MatchResult
from config import OLLAMA_MODEL

def match_vacancies(candidate, vacancies):
    vac_text = "\n".join([
        f"{i+1}. {v['title']} | {v['company']} | {v['salary']} | {v['url']}"
        for i, v in enumerate(vacancies)
    ])

    message = f"""
            Ты - профессиональный рекрутер.
            
            Кандидат:
            {candidate.model_dump_json(indent=2)}
            
            Вакансии (оцени каждую по совпадению 0-100%):
            {vac_text}
            
            Верни ТОЛЬКО JSON-массив (без текста до или после JSON массива) из 10 лучших вакансий, отсортированных по убыванию совпадения:
            [{{"title": "...", "company": "...", "salary": "...", "match_percent": 95, "reason": "причина одним предложением", "url": "..."}}]
            
            Для расчета процента и причины одним предложением необходимо зайти по ссылке на вакансию и соотнести требования 
            к кандидату с реальными навыками кандидата.
            
            Особые требования к данным:
            - значение в поле salary должно быть обязательно строковым
            - значение в поле match_percent должно быть обязательно целочисленным
            """

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{
            "role": "user",
            "content": message
        }]
    )

    json_str = response["message"]["content"].strip()
    json_str = json_str.removeprefix("```json").removesuffix("```").strip()

    data = json.loads(json_str)
    return [MatchResult(**item) for item in data]
