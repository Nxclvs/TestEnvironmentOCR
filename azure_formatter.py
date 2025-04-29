import os
import pandas as pd
import json
from Levenshtein import distance as levenshtein_distance

# Verzeichnisse
model = "azure"
output_dir = "outputs/azure"
solution_dir = "solutions"
analysis_dir = f"analysis/{model}"
os.makedirs(analysis_dir, exist_ok=True)

metrics_data = []

def normalize(text):
    if not isinstance(text, str):
        return ""
    return text.strip().lower()

def calculate_metrics(prediction_text, solution_text):
    pred_words = prediction_text.split()
    sol_words = solution_text.split()

    matched = 0
    total_solution = len(sol_words)
    total_predicted = len(pred_words)

    for word in sol_words:
        if word in pred_words:
            matched += 1

    precision = matched / total_predicted if total_predicted else 0
    recall = matched / total_solution if total_solution else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0
    accuracy = matched / total_solution if total_solution else 0
    levenshtein_total = levenshtein_distance(prediction_text, solution_text)

    return accuracy, precision, recall, f1, levenshtein_total

# Jetzt pro Datei durchlaufen
for i in range(1, 9):
    for noise in ["", "_noise"]:
        prediction_file = os.path.join(output_dir, f"azure_output_page_{i}{noise}.txt")
        solution_file = os.path.join(solution_dir, f"output_page_{i}.json")

        if not os.path.exists(prediction_file) or not os.path.exists(solution_file):
            continue

        with open(prediction_file, encoding="utf-8") as pf, open(solution_file, encoding="utf-8") as sf:
            pred_text = pf.read().split("--- Gesamtverarbeitungszeit")[0].strip()  # Nur OCR-Content
            solution_json = json.load(sf)
            if isinstance(solution_json, list):
                solution_json = solution_json[0]

            # Lösungstext zusammenbauen
            solution_text = " ".join(str(v) for v in solution_json.values())

            # Metriken berechnen
            accuracy, precision, recall, f1, levenshtein_total = calculate_metrics(pred_text, solution_text)

            metrics = {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "levenshtein_total": levenshtein_total,
                "document": f"output_page_{i}{noise}"
            }
            metrics_data.append(metrics)

            # Einzelergebnis als JSON speichern
            single_result_path = os.path.join(analysis_dir, f"azure_analysis_page_{i}{noise}.json")
            with open(single_result_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=4, ensure_ascii=False)

            print(f"✅ Analyse gespeichert: {single_result_path}")

# Alle Ergebnisse in eine Excel zusammenfassen
df = pd.DataFrame(metrics_data)
df.set_index("document", inplace=True)
df.loc["Durchschnitt"] = df.mean(numeric_only=True)
excel_path = os.path.join(analysis_dir, f"ocr_comparison_{model}.xlsx")
df.to_excel(excel_path)

print(f"✅ Zusammenfassung exportiert: {excel_path}")
