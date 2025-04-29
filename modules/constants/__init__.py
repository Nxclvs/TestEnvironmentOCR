import os, sys

temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")

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