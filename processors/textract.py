import sys, os
sys.path.append(os.path.dirname(os.path.dirname((__file__)))) 

from localconfig import config
import json
import boto3
import pdf2image
import base64
from trp import Document
import time
import modules.helpers
import modules.constants

textract = boto3.client(
    'textract',
    aws_access_key_id=config.get("aws").get("access_key_id"),
    aws_secret_access_key=config.get("aws").get("secret_access"),
    region_name="eu-central-1"
)

def pdf_to_images(pdf_path, output_folder="temp"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = pdf2image.convert_from_path(pdf_path)
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page{i+1}.png")
        img.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

def analyze_document_textract(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    start_time = time.time()  

    response = textract.analyze_document(
        Document={
            "Bytes": image_data
        },
        FeatureTypes=["TABLES", "FORMS"]
    )

    duration = time.time() - start_time  

    doc = Document(response)
    output_lines = []

    for page in doc.pages:
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if cell.text != '' and cell.text:
                        output_lines.append("Table[{}][{}] = {}".format(r, c, cell.text))
            output_lines.append("\n")


        for field in page.form.fields:
            if not field.value:
                output_lines.append("Field: Key: {}, Value: (no value)".format(field.key.text))
            else:
                output_lines.append("Field: Key: {}, Value: {}".format(field.key.text, field.value.text))

    return output_lines, duration

def process_pdf_with_textract(pdf_path):
    image_paths = pdf_to_images(pdf_path)
    all_lines = []
    total_time = 0  

    for image_path in image_paths:
        print(f"Processing {image_path} with Textract")
        extracted_lines, duration = analyze_document_textract(image_path)
        total_time += duration
        all_lines.extend(extracted_lines)

    all_lines.append(f"\n--- Gesamtverarbeitungszeit: {total_time:.2f} Sekunden ---")

    output_name = "textract_" + os.path.basename(pdf_path).replace(".pdf", ".txt")
    output_path = os.path.join("outputs", output_name)

    print("Textract abgeschlossen")

    return output_path, all_lines


def run_textract(pdf_path):
    output, lines = process_pdf_with_textract(pdf_path)
    with open(output, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def run_textract_with_noise(pdf_path):
    all_lines = []
    total_time = 0

    output_name = "textract_" + os.path.basename(pdf_path).replace(".pdf", "_noise.txt")
    output_path = os.path.join("outputs", output_name)

    image_paths = [os.path.join(modules.constants.temp_dir, file) for file in os.listdir(modules.constants.temp_dir)]

    for image_path in image_paths:
        noisy_image_path = modules.helpers.add_noise_to_image(image_path)
        extracted_lines, duration = analyze_document_textract(noisy_image_path)
        total_time += duration
        all_lines.extend(extracted_lines)

    all_lines.append(f"\n--- Gesamtverarbeitungszeit: {total_time:.2f} Sekunden ---")

    with open(output_path, "w", encoding="utf-8") as f:
        for line in all_lines:
            f.write(line + "\n")

    print("Textract Noise abgeschlossen")


if __name__ == "__main__":
    pass
