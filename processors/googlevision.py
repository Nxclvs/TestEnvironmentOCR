import os
import sys
import json
import time 
import pandas as pd
from google.cloud import documentai
from typing import Sequence, List
import pdf2image
from PIL import Image
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from localconfig import config

import modules.constants 
import modules.helpers

if os.path.exists(modules.constants.vision_ext_credentials):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = modules.constants.vision_ext_credentials

PROJECT_ID = config.get("googlevision").get("project_id")
LOCATION = config.get("googlevision").get("location")
PROCESSOR_ID = config.get("googlevision").get("processor_id")
MIME_TYPE = "application/pdf"

def online_process(project_id=PROJECT_ID, location=LOCATION, processor_id=PROCESSOR_ID, file_path=None, mime_type=MIME_TYPE):
    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
    documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
    resource_name = documentai_client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as image:
        file_content = image.read()

    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    print(f"📤 Sende Dokument an Google Vision API: {file_path}")

    start_time = time.time()  
    result = documentai_client.process_document(request=request)
    end_time = time.time()  
    duration = end_time - start_time  

    print(f"✅ Google Vision Antwort erhalten! Verarbeitungszeit: {duration:.2f} Sekunden")

    return result.document, duration

def get_table_data(rows: Sequence[documentai.Document.Page.Table.TableRow], text: str) -> List[List[str]]:
    table_data = []
    for table_row in rows:
        current_row = []
        for cell in table_row.cells:
            cell_text = layout_to_text(cell.layout, text)
            current_row.append(cell_text.strip())
        table_data.append(current_row)
    return table_data

def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    return "".join(
        text[int(segment.start_index): int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )

def extract_tables(project_id: str, location: str, processor_id: str, file_path: str, mime_type: str):
    output_name = "google_vision_" + file_path.split("\\")[-1].replace(".pdf", ".json")
    output_name = os.path.join("outputs", output_name)

    total_start_time = time.time()  

    document, processing_time = online_process(project_id, location, processor_id, file_path, mime_type)

    extracted_data = {
        "full_text": document.text,
        "tables": []
    }

    # Extrahiere Tabellen
    for page in document.pages:
        for i, table in enumerate(page.tables):
            num_columns = len(table.header_rows[0].cells) if table.header_rows else 0
            num_rows = len(table.body_rows)

            header_rows = get_table_data(table.header_rows, document.text) if table.header_rows else []
            body_rows = get_table_data(table.body_rows, document.text) if table.body_rows else []

            extracted_data["tables"].append({
                "page_number": page.page_number,
                "table_index": i,
                "num_columns": num_columns,
                "num_rows": num_rows,
                "headers": header_rows,
                "rows": body_rows
            })

    total_end_time = time.time()  
    total_duration = total_end_time - total_start_time  

    extracted_data["total_processing_time_sec"] = total_duration  

    print(f"Google Vision fertig Gesamtzeit: {total_duration:.2f} Sekunden")
    return extracted_data, output_name

def image_to_pdf(image_path):
    try:
        with Image.open(image_path) as img:
            pdf_path = image_path.replace(".png", ".pdf")
            img.convert("RGB").save(pdf_path, "PDF", resolution=100.0)
            return pdf_path
    except Exception as e:
        return e

def run_vision(file_path):
    data, output_name = extract_tables(PROJECT_ID, LOCATION, PROCESSOR_ID, file_path, MIME_TYPE)
    with open(output_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def run_vision_with_noise(file_path):
    output_folder = modules.constants.temp_dir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_name = "google_vision_" + file_path.split("\\")[-1].replace(".pdf", "_noise.json")
    output_name = os.path.join("outputs", output_name)    

    images = pdf2image.convert_from_path(file_path)
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page{i+1}.png")
        img.save(image_path, "PNG")
        image_paths.append(image_path)

    total_time = 0

    for image_path in image_paths:
        noise_file_path = modules.helpers.add_noise_to_image(image_path)
        pdf_path = image_to_pdf(noise_file_path)

        data, no = extract_tables(PROJECT_ID, LOCATION, PROCESSOR_ID, pdf_path, MIME_TYPE)

        # Aktualisiere die Gesamtzeit
        total_time += data.get("total_processing_time_sec", 0)

        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"🔄 Verrauschte Bilder verarbeitet - Gesamtzeit: {total_time:.2f} Sekunden")

if __name__ == "__main__":
    FILE_PATH = r'testfiles\output_page_6.pdf'
    run_vision_with_noise(FILE_PATH)
