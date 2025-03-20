from google.cloud import documentai_v1 as documentai

project_id = "835187183766"
location = "eu"
processor_id = "dd0c55be42d8d735"

file_path = r'testfiles/output_page_5.pdf'
mime_type = 'application/pdf'

opts = {
    "api_endpoint": f"{location}-documentai.googleapis.com"
}

client = documentai.DocumentProcessorServiceClient(
    client_options=opts
)

name = client.processor_path(
    project_id, location, processor_id
)

with open(file_path, 'rb') as image:
    image_content = image.read()

raw_document = documentai.RawDocument(
    content=image_content, mime_type=mime_type
)

request = documentai.ProcessRequest(
    name=name, raw_document=raw_document)

result = client.process_document(request)
with open("outputGOOGLE.json", "w", encoding="utf-8") as f:
    f.write(str(result))

document = result.document


def _extract_text(layout, document):
    """Extrahiert Text, der durch ein Layout-Objekt beschrieben wird."""
    text_segments = []
    for segment in layout.text_anchor.text_segments:
        start_index = segment.start_index
        end_index = segment.end_index
        text_segments.append(document.text[start_index:end_index])
    return ''.join(text_segments)


print(document.text)


for table in document.pages[0].tables:
    print("\nTabelle erkannt:")
    for row_idx, row in enumerate(table.header_rows):
        cells = []
        for cell in row.cells:
            cell_text = _extract_text(cell.layout, document)
            cells.append(cell_text)
        print(f"Header-Zeile {row_idx + 1}: {' | '.join(cells)}")

    for row_idx, row in enumerate(table.body_rows):
        cells = []
        for cell in row.cells:
            cell_text = _extract_text(cell.layout, document)
            cells.append(cell_text)
        print(f"Körper-Zeile {row_idx + 1}: {' | '.join(cells)}")
