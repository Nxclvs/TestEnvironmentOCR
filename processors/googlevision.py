from google.cloud import documentai
import pandas as pd
from typing import Sequence, List
import sys, os
sys.path.append(os.path.dirname(os.path.dirname((__file__))))
from localconfig import config



def online_process(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
) -> documentai.Document:
    """Processes a document using the Document AI Online Processing API."""

    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)

    resource_name = documentai_client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as image:
        image_content = image.read()

    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    result = documentai_client.process_document(request=request)

    return result.document


def get_table_data(
    rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
) -> List[List[str]]:
    """Get Text from table cells"""

    table_data: List[List[str]] = []
    for table_row in rows:
        current_row: List[str] = []
        for cell in table_row.cells:
            cell_text: str = layout_to_text(cell.layout, text)
            current_row.append(cell_text.strip())
        table_data.append(current_row)

    return table_data


def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string."""

    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )


def extract_tables(
    project_id: str, location: str, processor_id: str, file_path: str, mime_type: str
) -> None:
    """Extracts table data from a document using the Document AI Online Processing API
    and prints the table data to the console and a text file."""

    output_file = os.path.join("outputs", "google_vision_{}".format(file_path.split("\\")[-1].replace(".pdf", ".txt")))
    original_stdout = sys.stdout
    sys.stdout = open(output_file, 'w', encoding="utf-8")

    try:
        document = online_process(project_id, location, processor_id, file_path, mime_type)

        print(f"Full document text: {document.text}\n")

        for page in document.pages:
            print(f"\n\n**** Page {page.page_number} ****")
            print(f"Found {len(page.tables)} table(s):")

            for i, table in enumerate(page.tables):
                num_columns = len(table.header_rows[0].cells)
                num_rows = len(table.body_rows)
                print(f"Table {i} with {num_columns} columns and {num_rows} rows:")

                header_rows = get_table_data(table.header_rows, document.text)
                body_rows = get_table_data(table.body_rows, document.text)

                df = pd.DataFrame(columns=header_rows[0], data=body_rows)
                print(df.to_string())

    finally:
        sys.stdout.close()
        sys.stdout = original_stdout

    print(f"Output written to {output_file}")


PROJECT_ID = config.get("googlevision").get("project_id")
LOCATION = config.get("googlevision").get("location")
PROCESSOR_ID = config.get("googlevision").get("processor_id")
FILE_PATH = r'testfiles\output_page_1.pdf'
MIME_TYPE = "application/pdf"

extract_tables(PROJECT_ID, LOCATION, PROCESSOR_ID, FILE_PATH, MIME_TYPE)
