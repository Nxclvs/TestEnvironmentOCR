import os
import sys
import base64
import requests
import pdf2image
from mistralai import Mistral

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from localconfig import config

API_KEY = config.get("pixtral").get("key")
OCR_URL = "https://api.mistral.ai/v1/ocr"

def pdf_to_image(pdf_path, output_folder="temp"):
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
    """Encodes the image as Base64 for the API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_request(encoded_image):
    """Sends an OCR request to the Mistral API using a base64-encoded image."""
    client = Mistral(api_key=API_KEY)
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{encoded_image}"
        }
    )

    if ocr_response.status_code == 200:
        return ocr_response.json()  # Assuming the response is JSON
    else:
        return {"error": ocr_response.text}

def process_file(path):
    image_paths = pdf_to_image(path)
    extracted_data = []

    for image_path in image_paths:
        print(f"Processing {image_path}")
        encoded_image = encode_image(image_path)
        extracted_data.append(process_request(encoded_image))

    return extracted_data

if __name__ == "__main__":
    path = r"C:\Users\Niclas Wienzek\Desktop\Dev\TestEnvironmentOCR\testfiles\output_page_3.pdf"
    data = process_file(path)
    print(data)  # Output the OCR results
