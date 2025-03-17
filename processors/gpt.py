import sys, os
sys.path.append(os.path.dirname(os.path.dirname((__file__))))


import openai
import json
import pdf2image
import base64
from PIL import Image
from localconfig import config


client = openai.OpenAI(api_key=config.get("gpt").get("key"))


def pdf_to_image(pdf_path, output_folder = "temp"):
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
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        return base64.b64encode(image_data).decode("utf-8")


def extract_text_from_image(image_path):
    """Konvertiert ein Bild in Base64 und sendet es an GPT-4o zur Verarbeitung."""
    base64_image = encode_image_to_base64(image_path)

    print(f"Verarbeite Bild: {image_path}")

    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "Extrahiere die relevanten Informationen und gebe sie mir im JSON Format zurück."},
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

    extracted_data = response.choices[0].message.content
    return json.loads(extracted_data)


def process_pdf(pdf_path):
    image_paths = pdf_to_image(pdf_path)
    extracted_data = []

    for image_path in image_paths:
        print(f"Verarbeite {image_path}")
        extracted_data.append(extract_text_from_image(image_path))

    return extracted_data


if __name__ == "__main__":
    pdf_path = r"testfiles\output_page_1.pdf"
    json_data = process_pdf(pdf_path)
    with open("output.json", "w") as f:
        f.write(json.dumps(json_data, indent=4))
    print("Fertig!")