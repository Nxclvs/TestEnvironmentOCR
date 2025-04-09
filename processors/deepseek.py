import json
import re
import os

def extract_json(output: dict):
    try:

        json_match = re.search(r'json\s*({.*})', output, re.DOTALL)

        if json_match:
            clean_json = json_match.group(1)

            clean_json = re.sub(r'(\d+),(\d+)', r'\1.\2', clean_json)

            parsed_json = json.loads(clean_json)
            return parsed_json
        else:
            print("Kein gültiger JSON-Block gefunden.")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON-Dekodierungsfehler: {e}")
        return None

if __name__ =="__main__":
    while True:
        output = input("Gib den JSON-Block ein: ")
        page_num = input("Gib die Seitennummer ein: ")
        
        output_path = os.path.join("outputs", f"deepseek_output_page_{page_num}.json")

        parsed_data = extract_json(output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(parsed_data, indent=4, ensure_ascii=False))

        print("Erfolgreich ausgeführt")