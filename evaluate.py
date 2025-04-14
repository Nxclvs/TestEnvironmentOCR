import os
import json
from difflib import SequenceMatcher

# Verzeichnisse
gpt_output_dir = 'outputs/gpt/'
textract_output_dir = 'outputs/textract/'
solution_dir = 'solutions/'
analysis_dir = 'outputs/analysis/'
os.makedirs(analysis_dir, exist_ok=True)

# Levenshtein-Ähnlichkeit
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Vergleich von zwei Dictionaries
def compare_dicts(dict1, dict2):
    correct = 0
    total = 0
    errors = []

    for key in dict1:
        total += 1
        if key in dict2:
            if dict1[key] == dict2[key]:
                correct += 1
            else:
                errors.append((key, dict1[key], dict2[key]))
        else:
            errors.append((key, dict1[key], 'MISSING'))

    for key in dict2:
        if key not in dict1:
            total += 1
            errors.append((key, 'MISSING', dict2[key]))

    accuracy = correct / total if total > 0 else 0
    return accuracy, errors

# Analyse der OCR Ergebnisse
def analyze_ocr(output_path, solution_path, output_name):
    with open(output_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)['data'][0]
    with open(solution_path, 'r', encoding='utf-8') as f:
        solution_data = json.load(f)[0]

    accuracy, errors = compare_dicts(ocr_data, solution_data)

    analysis = {
        'accuracy': accuracy,
        'errors': errors
    }

    analysis_path = os.path.join(analysis_dir, f'{output_name}.json')
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

    print(f'Analysis saved to {analysis_path}')

# Hauptlauf
for i in range(1, 9):
    solution_path = os.path.join(solution_dir, f'output_page_{i}.json')
    gpt_path = os.path.join(gpt_output_dir, f'gpt_output_page_{i}.json')
    gpt_noise_path = os.path.join(gpt_output_dir, f'gpt_output_page_{i}_noise.json')

    analyze_ocr(gpt_path, solution_path, f'gpt_analysis_page_{i}')
    analyze_ocr(gpt_noise_path, solution_path, f'gpt_analysis_page_{i}_noise')
