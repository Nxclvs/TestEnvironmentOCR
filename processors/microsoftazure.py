import os
import sys
sys.path.append(os.path.dirname(os.path.dirname((__file__))))
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from localconfig import config
import time

endpoint = config.get("microsoftazure").get("endpoint")
key = config.get("microsoftazure").get("key")

def analyze_layout(path):

    output_path = os.path.join("outputs", "azure_" + os.path.basename(path).replace("pdf", "txt"))

    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    with open (r"testfiles\output_page_6.pdf", "rb") as file:  
        file_data = file.read()

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", content_type="application/octet-stream", body=file_data
    )

    result: AnalyzeResult = poller.result()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(result.content))


if __name__ == "__main__":
    PATH = r'testfiles\output_page_6.pdf'
    analyze_layout(PATH)