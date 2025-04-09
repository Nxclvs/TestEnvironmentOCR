import os
import json
import pandas as pd
from Levenshtein import distance as levenshtein_distance
from unidecode import unidecode

# Verzeichnisse
MODEL = "deepseek"
OUTPUT_DIR = f"outputs/{MODEL}"
SOLUTION_DIR = "solutions"
ANALYSIS_DIR = f"analysis/{MODEL}"

metrics_data = []

def normalize(text):
    if not isinstance(text, str):
        return ""
    return unidecode(text.strip().lower())

def flatten_json(y):
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

def compare_json(pred, true):
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

    # Zusätzliche Schlüssel im Prediction-JSON ignorieren, aber für Statistik notieren
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
for i in range(1, 9):
    for noise in ["", "_noise"]:
        ocr_file = os.path.join(OUTPUT_DIR, f"{MODEL}_output_page_{i}{noise}.json")
        solution_file = os.path.join(SOLUTION_DIR, f"output_page_{i}.json")
        if not os.path.exists(ocr_file) or not os.path.exists(solution_file):
            continue

        with open(ocr_file, encoding="utf-8") as gf, open(solution_file, encoding="utf-8") as sf:
            try:
                gpt_data = json.load(gf)
                solution_data = json.load(sf)

                if isinstance(gpt_data, list):
                    gpt_data = gpt_data[0]
                if isinstance(solution_data, list):
                    solution_data = solution_data[0]

                metrics = compare_json(gpt_data, solution_data)
                metrics["document"] = f"output_page_{i}{noise}"
                metrics_data.append(metrics)

                # Als JSON speichern
                os.makedirs(ANALYSIS_DIR, exist_ok=True)
                with open(os.path.join(ANALYSIS_DIR, f"{MODEL}_analysis_page_{i}{noise}.json"), "w", encoding="utf-8") as out:
                    json.dump(metrics, out, indent=4, ensure_ascii=False)

                print(f"Analysis saved: {MODEL}_analysis_page_{i}{noise}")

            except Exception as e:
                print(f"Fehler bei Datei output_page_{i}{noise}: {e}")

df = pd.DataFrame(metrics_data)
df.set_index("document", inplace=True)
df.loc["Durchschnitt"] = df.mean(numeric_only=True)
for metric in ["accuracy", "precision", "recall", "f1_score"]:
    df[f"{metric}_abweichung"] = df[metric] - df.loc["Durchschnitt", metric]

def bewertung(row):
    if row["accuracy"] < 0.6:
        return "🟥 schlecht"
    elif row["accuracy"] < 0.8:
        return "🟨 mittel"
    else:
        return "🟩 gut"

df["bewertung_accuracy"] = df.apply(bewertung, axis=1)

os.makedirs(ANALYSIS_DIR, exist_ok=True)
excel_path = os.path.join(ANALYSIS_DIR, f"ocr_comparison_{MODEL}.xlsx")
df.to_excel(excel_path)

print(f"Excel exportiert nach: {excel_path}")

