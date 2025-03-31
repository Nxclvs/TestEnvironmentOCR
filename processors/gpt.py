import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time 
import openai
import json
import pdf2image
import base64
from PIL import Image
from localconfig import config
import modules.helpers
import modules.constants
client = openai.OpenAI(api_key=config.get("gpt").get("key"))

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

def encode_image_to_base64(image_path):
    """Kodiert das Bild als Base64 für die API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_text_from_image(image_path):
    """Konvertiert ein Bild in Base64 und sendet es an GPT-4o zur Verarbeitung."""
    base64_image = encode_image_to_base64(image_path)

    print(f"Sende Bild an GPT-4o: {image_path}")

    start_time = time.time() 

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Extrahiere die relevanten Informationen und gebe sie mir ohne zusätzlichen Text im JSON Format zurück. Verwende für die Beschriftung der Keys nur Kleinbuchstaben und Unterstriche, sowie keine Umlaute. Bei angekreuzten Kontrollkästchen füge diese bitte entsprechend mit zur Auswertung hinzu. Es sollten keine Elemente des Dokuments ausgelassen werden, egal ob diese ausgefüllt sind, oder nicht."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Hier ist das Bild mit den Daten:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=1000,
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    end_time = time.time()  
    duration = end_time - start_time  
    print(f"GPT-4o Antwort erhalten! Verarbeitungszeit: {duration:.2f} Sekunden")

    extracted_data = response.choices[0].message.content
    return json.loads(extracted_data), duration  

def process_pdf(pdf_path):
    """Verarbeitet eine PDF-Datei und misst die gesamte Verarbeitungszeit."""
    image_paths = pdf_to_image(pdf_path)
    extracted_data = []
    total_time = 0 

    for image_path in image_paths:
        result, duration = extract_text_from_image(image_path)
        extracted_data.append(result)
        total_time += duration  
    return extracted_data, total_time

def run_gpt(pdf_path):
    """Führt die Verarbeitung für eine PDF-Datei durch und speichert die Ergebnisse mit der Verarbeitungszeit."""
    output_name = "gpt_" + pdf_path.split("\\")[-1].replace(".pdf", ".json")
    output_name = os.path.join("outputs", output_name)

    extracted_data, total_time = process_pdf(pdf_path)

    # Speichere JSON-Ergebnisse + Zeitmessung
    result = {
        "data": extracted_data,
        "total_processing_time_sec": total_time  
    }

    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"GPT fertig - Gesamtzeit: {total_time:.2f} Sekunden")

def run_gpt_with_noise(pdf_path):
    """Führt die Verarbeitung mit verrauschten Bildern durch."""
    image_paths = [os.path.join(modules.constants.temp_dir, file) for file in os.listdir(modules.constants.temp_dir)]
    extracted_data = []
    total_time = 0 

    for image_path in image_paths:
        noisy_image_path = modules.helpers.add_noise_to_image(image_path)
        result, duration = extract_text_from_image(noisy_image_path)
        extracted_data.append(result)
        total_time += duration  

    output_name = "gpt_" + pdf_path.split("\\")[-1].replace(".pdf", "_noise.json")
    output_name = os.path.join("outputs", output_name)

    # Speichere Ergebnisse + Zeitmessung
    result = {
        "data": extracted_data,
        "total_processing_time_sec": total_time  
    }

    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"GPT fertig - Gesamtzeit: {total_time:.2f} Sekunden")



if __name__ == "__main__":
    pdf_path = r"testfiles\output_page_5.pdf"
    run_gpt_with_noise(pdf_path)
