import ollama
from config import OLLAMA_MODEL
from src.models import Candidate

def extract_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_resume(path: str) -> Candidate:
    text = extract_text(path)

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
                        Извлеки из резюме ТОЛЬКО JSON (без ``` и текста):

                        {{
                          "desired_position": "position name",
                          "hard_skills": ["skill 1", "skill 2", ...],
                          "years_experience": 0.5,
                          "salary_expectation": 20000
                        }}
                        
                        desired_position - желаемая должность
                        
                        hard_skills - навыки
                        
                        years_experience - годы опыта числом
                        
                        salary_expectation - минимальная ожидаемая зарплата числом
                        
                        Резюме:
                        {text[:12000]}
                    """
        }]
    )
    answer = response["message"]["content"]

    json_str = answer.strip()
    json_str = json_str.removeprefix("```json").removesuffix("```").strip()

    return Candidate.model_validate_json(json_str)
