import os
import json
import pandas as pd
from Levenshtein import distance as levenshtein_distance
from unidecode import unidecode
import re

# Verzeichnisse
MODEL = "textract"
OUTPUT_DIR = f"outputs/{MODEL}"
SOLUTION_DIR = "solutions"
ANALYSIS_DIR = f"analysis/{MODEL}"

metrics_data = []

def normalize(text):
    if not isinstance(text, str):
        return ""
    return unidecode(text.strip().lower())

def parse_textract_output(file_path):
    """Extrahiere die Key-Value Paare und Tabelleninhalte aus Textract-Output."""
    fields = {}
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()
    
    # Felder extrahieren
    for line in lines:
        if line.startswith("Field: Key:"):
            match = re.match(r"Field: Key: (.*?), Value: (.*)", line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                fields[key] = value
        elif line.startswith("Table["):
            match = re.match(r"Table\[(\d+)\]\[(\d+)\] = (.*)", line)
            if match:
                row_idx, col_idx, value = match.groups()
                fields[f"table_{row_idx}_{col_idx}"] = value.strip()
    return fields

def flatten_json(y):
    """Hilfsfunktion, falls die Lösung verschachtelt wäre."""
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], f'{name}{a}_')
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, f'{name}{i}_')
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def compare_dicts(pred, true):
    pred_flat = flatten_json(pred)
    true_flat = flatten_json(true)

    matched = 0
    total = len(true_flat)
    false_positives = 0
    false_negatives = 0
    total_lev_distance = 0

    for key in true_flat:
        norm_key = normalize(key)
        true_val = normalize(true_flat[key])
        pred_val = normalize(pred_flat.get(key, ""))

        lev = levenshtein_distance(true_val, pred_val)
        total_lev_distance += lev

        if true_val == pred_val:
            matched += 1
        else:
            false_negatives += 1

    # Zusätzliche Schlüssel ignorieren
    for key in pred_flat:
        if normalize(key) not in [normalize(k) for k in true_flat]:
            false_positives += 1

    precision = matched / (matched + false_positives) if (matched + false_positives) > 0 else 0
    recall = matched / total if total > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = matched / total if total > 0 else 0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "levenshtein_total": total_lev_distance
    }

# Hauptlogik
os.makedirs(ANALYSIS_DIR, exist_ok=True)

for i in range(1, 9):
    for noise in ["", "_noise"]:
        textract_file = os.path.join(OUTPUT_DIR, f"textract_output_page_{i}{noise}.txt")
        solution_file = os.path.join(SOLUTION_DIR, f"output_page_{i}.json")

        if not os.path.exists(textract_file) or not os.path.exists(solution_file):
            continue

        with open(solution_file, encoding="utf-8") as sf:
            solution_data = json.load(sf)
            if isinstance(solution_data, list):
                solution_data = solution_data[0]

        try:
            parsed_textract = parse_textract_output(textract_file)

            metrics = compare_dicts(parsed_textract, solution_data)
            metrics["document"] = f"output_page_{i}{noise}"
            metrics_data.append(metrics)

            # Speichere Einzelanalyse
            with open(os.path.join(ANALYSIS_DIR, f"textract_analysis_page_{i}{noise}.json"), "w", encoding="utf-8") as out:
                json.dump(metrics, out, indent=4, ensure_ascii=False)

            print(f"✅ Analysis saved: textract_analysis_page_{i}{noise}")

        except Exception as e:
            print(f"❌ Fehler bei Datei output_page_{i}{noise}: {e}")

# Zusammenfassung
df = pd.DataFrame(metrics_data)
df.set_index("document", inplace=True)
df.loc["Durchschnitt"] = df.mean(numeric_only=True)

excel_path = os.path.join(ANALYSIS_DIR, f"ocr_comparison_textract.xlsx")
df.to_excel(excel_path)
print(f"✅ Zusammenfassung gespeichert: {excel_path}")
