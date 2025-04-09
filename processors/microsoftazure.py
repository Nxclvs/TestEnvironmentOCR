import os
import sys
import time  # ⏱ Zeitmodul zum Messen der Laufzeit
sys.path.append(os.path.dirname(os.path.dirname((__file__))))
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentTable
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

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    with open(path, "rb") as file:
        file_data = file.read()

    print(f"📤 Sende Dokument an Azure: {path}")
    start_time = time.time()

    poller = client.begin_analyze_document(
        "prebuilt-layout",
        content_type="application/pdf",
        body=file_data
    )

    result: AnalyzeResult = poller.result()
    duration = time.time() - start_time
    print(f"Azure Antwort erhalten Verarbeitungszeit: {duration:.2f} Sekunden")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("📄 Volltext:\n")
        f.write(result.content or "")
        f.write("\n\n📋 Tabellen:\n")

        for i, table in enumerate(result.tables):
            f.write(f"\n--- Tabelle {i + 1} ---\n")
            
            current_row = -1
            row_cells = []

            for cell in sorted(table.cells, key=lambda c: (c.row_index, c.column_index)):
                if cell.row_index != current_row:
                    if row_cells:
                        f.write("\t".join(row_cells) + "\n")
                    row_cells = []
                    current_row = cell.row_index
                row_cells.append(cell.content.strip())

            if row_cells:
                f.write("\t".join(row_cells) + "\n")

        f.write(f"\n\n Gesamtverarbeitungszeit: {duration:.2f} Sekunden ---")

    print(f"Ergebnis gespeichert: {output_path}")


def run_azure_with_noise(path):
    output_path = os.path.join("outputs", "azure_" + os.path.basename(path).replace(".pdf", "_noise.txt"))

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    image_paths = modules.helpers.pdf_to_image(path)

    total_time = 0
    full_output = ""

    for idx, image_path in enumerate(image_paths):
        noisy_image_path = modules.helpers.add_noise_to_image(image_path)
        pdf_path = image_to_pdf(noisy_image_path)

        with open(pdf_path, "rb") as file:
            file_data = file.read()

        print(f" Sende verrauschtes Bild an Azure: {noisy_image_path}")
        start_time = time.time()

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            content_type="application/pdf",
            body=file_data
        )
        result: AnalyzeResult = poller.result()

        duration = time.time() - start_time
        total_time += duration
        print(f"Azure Antwort erhalten für Seite {idx + 1} Dauer: {duration:.2f} Sekunden")

        # Ergebnis zusammenbauen
        page_output = f"\n=== Seite {idx + 1} ===\n"
        page_output += " Volltext:\n"
        page_output += result.content or ""
        page_output += "\n\n📋 Tabellen:\n"

        for i, table in enumerate(result.tables):
            page_output += f"\n--- Tabelle {i + 1} ---\n"
            current_row = -1
            row_cells = []

            for cell in sorted(table.cells, key=lambda c: (c.row_index, c.column_index)):
                if cell.row_index != current_row:
                    if row_cells:
                        page_output += "\t".join(row_cells) + "\n"
                    row_cells = []
                    current_row = cell.row_index
                row_cells.append(cell.content.strip())

            if row_cells:
                page_output += "\t".join(row_cells) + "\n"

        page_output += f"\n Verarbeitungszeit für Seite: {duration:.2f} Sekunden\n"
        full_output += page_output

    full_output += f"\n Gesamtverarbeitungszeit für verrauschte Bilder: {total_time:.2f} Sekunden ---"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_output)

    print(f"Ergebnis gespeichert: {output_path}")


if __name__ == "__main__":
    PATH = r'testfiles\output_page_6.pdf'
    run_azure(PATH)
    run_azure_with_noise(PATH)
