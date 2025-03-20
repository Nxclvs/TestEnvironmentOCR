import os
import sys
import json
import base64
import requests
import pdf2image
from mistralai import Mistral

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from localconfig import config

API_KEY = config.get("pixtral").get("key")

def pdf_to_image(pdf_path, output_folder="temp"):
    """Konvertiert PDF in Bilder und speichert sie als PNG."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = pdf2image.convert_from_path(pdf_path)
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page{i+1}.png")
        img.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

def encode_image(image_path):
    """Kodiert das Bild als Base64 für die API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def clean_json_response(response_text):
    """Bereinigt die JSON-Antwort, indem Markdown-Codeblöcke entfernt und in JSON umgewandelt werden."""
    try:
        response_text = response_text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)  # Konvertiere in echtes JSON
    except json.JSONDecodeError:
        print("Fehler beim Parsen der JSON-Antwort")
        return None

def process_request(encoded_image):
    """Sendet eine OCR-Anfrage an die Mistral API."""
    client = Mistral(api_key=API_KEY)
    ocr_response = client.chat.complete(
        model="pixtral-large-latest",
        messages=[
            {"role": "system", "content": "Extrahiere die relevanten Informationen und gebe sie mir ohne zusätzlichen Text im JSON Format zurück. Verwende für die Beschriftung der Keys nur Kleinbuchstaben und Unterstriche, sowie keine Umlaute. Bei angekreuzten Kontrollkästchen füge diese bitte entsprechend mit zur Auswertung hinzu. Es sollten keine ausgefüllten oder angekreuzten Elemente ausgelassen werden."},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ],
    )

    if ocr_response:
        return clean_json_response(ocr_response.choices[0].message.content)
    else:
        return None

def process_file(path):
    """Verarbeitet eine PDF-Datei und extrahiert OCR-Daten."""
    image_paths = pdf_to_image(path)
    extracted_data = []

    for image_path in image_paths:
        print(f"Verarbeite {image_path} mit Pixtral-Large")
        encoded_image = encode_image(image_path)
        extracted_json = process_request(encoded_image)

        if extracted_json:
            extracted_data.append(extracted_json)

    return extracted_data

def run_pixtral(path):
    output_name = "pixtral_" + path.split("\\")[-1].replace(".pdf", ".json")
    output_name = os.path.join("outputs", output_name)
    json_data = process_file(path)
    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    print("Pixtral fertig!")




if __name__ == "__main__":
    path = r"testfiles\output_page_7.pdf"
    output_name = "pixtral_" + path.split("\\")[-1].replace(".pdf", ".json")
    output_name = os.path.join("outputs", output_name)
    data = process_file(path)

    # Speichere die JSON-Daten richtig formatiert
    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Pixtral fertig!")

