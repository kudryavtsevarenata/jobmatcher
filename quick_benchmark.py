import time
import requests
import psutil
import json
import threading
from collections import deque

def get_ollama_memory_usage():
    total_memory_mb = 0

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            pinfo = proc.info
            process_name = pinfo['name'].lower()

            if 'ollama' in process_name and pinfo['memory_info']:
                rss_mb = pinfo['memory_info'].rss / 1024 / 1024
                total_memory_mb += rss_mb

        except Exception:
            continue

    return total_memory_mb

class MemoryMonitor:
    def __init__(self, monitor_interval=0.05):
        self.memory_samples = deque(maxlen=1000)
        self.monitoring = False
        self.interval = monitor_interval
        self.peak_memory = 0
        self.thread = None

    def _monitor_thread(self):
        while self.monitoring:
            mem_mb = get_ollama_memory_usage()
            self.memory_samples.append({
                'timestamp': time.time(),
                'memory_mb': mem_mb
            })
            if mem_mb > self.peak_memory:
                self.peak_memory = mem_mb
            time.sleep(self.interval)

    def start(self):
        self.monitoring = True
        self.peak_memory = 0
        self.thread = threading.Thread(target=self._monitor_thread)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=2)

    def get_peak_memory(self):
        return self.peak_memory

    def get_average_memory(self):
        if not self.memory_samples:
            return 0

        memories = [sample['memory_mb'] for sample in self.memory_samples]
        return sum(memories) / len(memories)

def quick_model_test(model_name: str):
    prompt = """Проанализируй резюме и верни JSON с навыками:

Кандидат: Python разработчик с 3 годами опыта.
Навыки: Python, FastAPI, PostgreSQL, Docker, Git, Linux.
Опыт: 3 года в backend-разработке.

Верни JSON: {"skills": ["список"], "experience_years": число}"""

    memory_monitor = MemoryMonitor(monitor_interval=0.03)

    memory_monitor.start()

    start_time = time.time()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200}
            },
            timeout=60
        )

        end_time = time.time()

        memory_monitor.stop()

        response_time = end_time - start_time
        data = response.json()

        peak_memory = memory_monitor.get_peak_memory()
        average_memory = memory_monitor.get_average_memory()

        print(f"Время ответа: {response_time:.2f} сек")
        print(f"Пиковая память Ollama: {peak_memory:.1f} MB")
        print(f"Средняя память Ollama: {average_memory:.1f} MB")

        try:
            result_text = data.get('response', '{}')
            if '{' in result_text and '}' in result_text:
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                json_str = result_text[start_idx:end_idx]
                parsed_json = json.loads(json_str)
                skills_count = len(parsed_json.get('skills', []))
                exp_years = parsed_json.get('experience_years', 0)
                print(f"JSON валиден: {skills_count} навыков, опыт {exp_years} лет")
            else:
                print("JSON не найден в ответе")
                print(f"Ответ модели: {result_text[:200]}")
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            print(f"Ошибка анализа ответа: {e}")
        return {
            "model": model_name,
            "time": response_time,
            "peak_memory": peak_memory,
            "average_memory": average_memory,
        }

    except Exception as e:
        print(e)

    memory_monitor.stop()


def main():
    models = ["llama3.2:3b", "gemma2:9b", "qwen2.5:7b"]
    results = []

    for i, model in enumerate(models):
        print(f"\nTesting {model}")

        if i > 0:
            time.sleep(5)

        result = quick_model_test(model)
        results.append(result)

        if model != models[-1]:
            time.sleep(15)

    print(f"\n{'Модель':<20} {'Время (сек)':<12} {'Память пик (MB)':<15} {'Память ср (MB)':<15}")
    print("-" * 70)
    for r in results:
        print(f"{r['model']:<20} "
              f"{r['time']:<12.2f} "
              f"{r['peak_memory']:<15.1f} "
              f"{r['average_memory']:<15.1f} ")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"benchmark_results_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "system_info": {
                "cpu_cores": psutil.cpu_count(),
                "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "available_memory_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nРезультаты сохранены в {output_file}")


if __name__ == "__main__":
    main()
