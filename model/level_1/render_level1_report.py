from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from level_1_analysis import load_data_session

from level_1_analysis import *
import os

def create_report(session_id):
    template_path = "./template/structure_niveau_1.tex"
    report_path = f"./report/session_{session_id}/level_1_report_{session_id}.tex"

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    session_info, dicts, dfs = load_data_session(session_id)

    # Replace placeholders with actual data (to be implemented later)
    report_content = template_content.replace("[Nom du circuit]", session_info['track'])
    report_content = report_content.replace("[Date]", session_info['date'])
    report_content = report_content.replace("[Essais Libres / Qualification / Course]", "Essais Libres")
    report_content = report_content.replace("[Identifiant voiture]", session_info['car'])
    report_content = report_content.replace("[Nom pilote]", session_info['driver'])
    report_content = report_content.replace("[XX]", "10")
    report_content = report_content.replace("[Temps]", "1:35.678")
    report_content = report_content.replace("[XX °C / XX °C]", "25 °C / 30 °C")
    # Add more replacements as needed

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_content)

    print(f"Report generated at {report_path}")

if __name__ == "__main__":
    create_report(29)