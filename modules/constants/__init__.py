import os, sys

temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")

vision_ext_credentials = r"C:\Users\Niclas\Desktop\Dev\TestEnvironmentOCR\compact-nirvana-443809-u8-e7d4743c19c4.json"

model_list = [
    "deepseek",
    "gpt",
    "pixtral",
    "textract",
    "azure",
    "google_vision"
]

if __name__ == '__main__':
    print(output_dir)