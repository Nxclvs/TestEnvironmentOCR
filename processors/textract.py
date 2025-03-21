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

    with open("response.json", "w") as f:
        json.dump(response, f, indent=2)

    return response

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