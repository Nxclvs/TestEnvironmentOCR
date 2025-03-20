import json
import re

def extract_json(output: dict):
    try:
        # Extrahiere den "result"-Wert
        raw_result = output.get("result", "")
        
        # Entferne die Codeblock-Markierung
        json_match = re.search(r'```json\n(.*?)\n```', raw_result, re.DOTALL)
        
        if json_match:
            clean_json = json_match.group(1)
            
            # Konvertiere in ein Dictionary
            parsed_json = json.loads(clean_json)
            return parsed_json
        else:
            print("Kein gültiger JSON-Block gefunden.")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON-Dekodierungsfehler: {e}")
        return None

# Beispieloutput
output = {
    "result": "```json\n{\n \"Name\": \"Sagfurl\",\n \"Vorname\": \"Isa\",\n \"PersonalNr\": \"42093663\",\n \"Bereich/Fakultat\": \"Dann bro\",\n \"Urlaubsjahr\": \"2023\",\n \"Zusatzurlaub & Schwerbeh\": \"0\",\n \"Gesamturlaubt\": \"30\",\n \"Stand\": \"01/2023\"\n}\n```"
}

# JSON extrahieren und anzeigen
parsed_data = extract_json(output)
print(json.dumps(parsed_data, indent=4, ensure_ascii=False))
