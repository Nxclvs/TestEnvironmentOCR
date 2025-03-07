import sys, os
sys.path.append(os.path.dirname(os.path.dirname((__file__)))) 

from localconfig import config
import json
import boto3
import pdf2image
import base64

textract = boto3.client(
    'textract',
    aws_access_key_id=config.get("aws").get("access_key_id"),
    aws_secret_access_key=config.get("aws").get("secret_access"),
    region_name="eu-central-1"
    )

def pdf_to_images(pdf_path, output_folder = "temp"):
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

    response = textract.analyze_document(
        Document={
            "Bytes": image_data
        },
        FeatureTypes=["TABLES", "FORMS"]
    )

    with open("response.txt", "w") as f:
        json.dump(response, f, indent=2)

    # Key-Value-Paare extrahieren
    key_value_pairs = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "Relationships" in block:
            key = None
            value = None
            for rel in block["Relationships"]:
                if rel["Type"] == "CHILD":
                    for child_id in rel["Ids"]:
                        child_block = next(
                            (b for b in response["Blocks"] if b["Id"] == child_id),
                            None
                        )
                        if child_block and "Text" in child_block:
                            if "EntityTypes" in block and "KEY" in block["EntityTypes"]:
                                key = child_block["Text"]
                            elif "EntityTypes" in block and "VALUE" in block["EntityTypes"]:
                                value = child_block["Text"]
            if key and value:
                key_value_pairs[key] = value

    # Urlaubsanträge aus Tabellen extrahieren
    urlaubsantraege = []
    for block in response["Blocks"]:
        if block["BlockType"] == "TABLE":
            table_rows = []
            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    row_data = []
                    for cell_id in rel["Ids"]:
                        cell_block = next(
                            (b for b in response["Blocks"] if b["Id"] == cell_id),
                            None
                        )
                        if cell_block and "Text" in cell_block:
                            row_data.append(cell_block["Text"])
                    if row_data:
                        table_rows.append(row_data)

            # Falls die Tabelle Zeilen enthält, parse sie als Urlaubsanträge
            if table_rows:
                for row in table_rows[1:]:  # Erste Zeile oft Header, daher ignorieren
                    try:
                        urlaubsantraege.append({
                            "von": row[0],
                            "bis": row[1],
                            "beantragte_Tage": int(row[2]),
                            "Rest_Tage": int(row[3]),
                            "Antragsteller": row[4],
                            "befürwortet": True,  # Textract gibt das nicht direkt an
                            "genehmigt": True
                        })
                    except (IndexError, ValueError):
                        continue  # Falls ein Fehler in der Zeile ist, überspringe sie

    # JSON im GPT-4o-Format erstellen
    formatted_json = {
        "Name": key_value_pairs.get("Name", ""),
        "Vorname": key_value_pairs.get("Vorname", ""),
        "Personalnummer": key_value_pairs.get("Personalnr.", ""),
        "Bereich/Fakultät": key_value_pairs.get("Bereich/Fakultät", ""),
        "Gleitzeit": key_value_pairs.get("Gleitzeit", "") == "Ja",
        "Urlaubsjahr": int(key_value_pairs.get("Urlaubsjahr", "0")),
        "Zusatzurlaub_Schwerbehinderung": int(key_value_pairs.get("Zusatzurlaub f. Schwerbeh.", "0")),
        "Gesamturlaub": int(key_value_pairs.get("Gesamturlaub", "0")),
        "Urlaubsanträge": urlaubsantraege,
        "Hinweis": key_value_pairs.get(
            "Hinweis", "Der Urlaub soll grundsätzlich im laufenden Kalenderjahr, spätestens jedoch bis zum 30.09. des Folgejahres genommen werden."
        )
    }

    return formatted_json

def process_pdf_with_textract(pdf_path):
    image_paths = pdf_to_images(pdf_path)
    extracted_data = []

    for image_path in image_paths:
        print(f"Processing {image_path} with Textract")
        extracted_text = analyze_document_textract(image_path)

        formatted_json = {
            "image": image_path,
            "extracted_text": extracted_text
        }

        extracted_data.append(formatted_json)

    return extracted_data

if __name__ == "__main__":
    pdf_path = r"testfiles\output_page_1.pdf"
    json_data = process_pdf_with_textract(pdf_path)
    print(json_data)