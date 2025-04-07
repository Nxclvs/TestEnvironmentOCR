import os
import sys
import time  # ⏱ Zeitmodul zum Messen der Laufzeit
sys.path.append(os.path.dirname(os.path.dirname((__file__))))
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from localconfig import config
import modules.helpers
import modules.constants 
from PIL import Image

endpoint = config.get("microsoftazure").get("endpoint")
key = config.get("microsoftazure").get("key")

def image_to_pdf(image_path):
    try:
        with Image.open(image_path) as img:
            pdf_path = image_path.replace(".png", ".pdf")
            img.convert("RGB").save(pdf_path, "PDF", resolution=100.0)
            return pdf_path
    except Exception as e:
        return e

def run_azure(path):
    output_path = os.path.join("outputs", "azure_" + os.path.basename(path).replace("pdf", "txt"))
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    with open(path, "rb") as file:  
        file_data = file.read()

    print(f"📤 Sende Dokument an Azure: {path}")
    start_time = time.time()  

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read", content_type="application/octet-stream", body=file_data
    )
    result: AnalyzeResult = poller.result()

    duration = time.time() - start_time  
    print(f"✅ Azure Antwort erhalten! Verarbeitungszeit: {duration:.2f} Sekunden")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(result.content))
        f.write(f"\n--- Gesamtverarbeitungszeit: {duration:.2f} Sekunden ---")
    print(f"✅ Ergebnis gespeichert: {output_path}")

def run_azure_with_noise(path):
    """Führt die Azure-Dokumentanalyse mit verrauschten Bildern durch."""
    output_path = os.path.join("outputs", "azure_" + os.path.basename(path).replace(".pdf", "_noise.txt"))
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    paths = modules.helpers.pdf_to_image(path)
    res = ""
    total_time = 0  

    for image in paths:
        noisy_image_path = modules.helpers.add_noise_to_image(image)
        pdf_path = image_to_pdf(noisy_image_path)

        with open(pdf_path, "rb") as file:
            file_data = file.read()

        print(f"📤 Sende verrauschtes Bild an Azure: {noisy_image_path}")
        start_time = time.time()  

        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-read", content_type="application/octet-stream", body=file_data
        )
        result: AnalyzeResult = poller.result()

        duration = time.time() - start_time  
        print(f"✅ Azure Antwort erhalten! Verarbeitungszeit: {duration:.2f} Sekunden")
        total_time += duration  

        res += str(result.content) + f"\n--- Verarbeitungszeit für Bild: {duration:.2f} Sekunden ---\n"

    res += f"\n--- Gesamtverarbeitungszeit: {total_time:.2f} Sekunden ---"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(res)

    print(f"✅ Verrauschte Bilder verarbeitet und gespeichert: {output_path}")

if __name__ == "__main__":
    PATH = r'testfiles\output_page_6.pdf'
    run_azure_with_noise(PATH)
