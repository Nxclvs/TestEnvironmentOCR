import sys, os
sys.path.append(os.path.dirname(os.path.dirname((__file__)))) 

from localconfig import config
import json
import boto3
import pdf2image
import base64
from trp import Document
import time

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

    start_time = time.time()  # ⏱ Startzeit

    response = textract.analyze_document(
        Document={
            "Bytes": image_data
        },
        FeatureTypes=["TABLES", "FORMS"]
    )

    duration = time.time() - start_time  # ⏱ Dauer berechnen

    # response.json wird weiterhin gespeichert, falls du sie brauchst
    with open("response.json", "w") as f:
        json.dump(response, f, indent=2)

    doc = Document(response)
    output_lines = []

    output_lines.append(f"--- Auswertung für: {os.path.basename(pdf_path)} ---")

    for page in doc.pages:
        # Print lines and words
        # for line in page.lines:
        #     print("Line: {}".format(line.text))
        #     for word in line.words:
        #         print("Word: {}".format(word.text))

        # Print tables
        for table in page.tables:
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row.cells):
                    if cell.text != '' and cell.text:
                        output_lines.append("Table[{}][{}] = {}".format(r, c, cell.text))
            output_lines.append("\n")

        # Print fields
        for field in page.form.fields:
            if not field.value:
                output_lines.append("Field: Key: {}, Value: (no value)".format(field.key.text))
            else:
                output_lines.append("Field: Key: {}, Value: {}".format(field.key.text, field.value.text))

        # Get field by key
        # key = "Phone Number:"
        # field = page.form.getFieldByKey(key)
        # if(field):
        #     print("Field: Key: {}, Value: {}".format(field.key, field.value))

        # Search fields by key
        # key = "address"
        # fields = page.form.searchFieldsByKey(key)
        # for field in fields:
        #     print("Field: Key: {}, Value: {}".format(field.key, field.value))

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

    with open(output_path, "w", encoding="utf-8") as f:
        for line in all_lines:
            print(line)
            f.write(line + "\n")

    print(f"✅ Textract abgeschlossen! Ergebnisse in: {output_path}")

if __name__ == "__main__":
    pdf_path = r"testfiles\output_page_6.pdf"
    process_pdf_with_textract(pdf_path)
