import pdfkit
import os
from jinja2 import Environment, FileSystemLoader
from datetime import date

from config import REPORT_PATH

env = Environment(loader=FileSystemLoader("templates"))

def generate_report(candidate, matches):
    os.makedirs("results", exist_ok=True)

    template = env.get_template("report.html")
    html = template.render(candidate=candidate, matches=matches, date=date.today().strftime("%d.%m.%Y"))

    temp_html = "results/temp_report.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html)

    pdfkit.from_file(temp_html, REPORT_PATH)
