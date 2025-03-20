from processors.gpt import run_gpt
from processors.pixtral import run_pixtral      

paths = [
    r"testfiles\output_page_6.pdf",
    r"testfiles\output_page_7.pdf",
    r"testfiles\output_page_8.pdf",
]

for path in paths:
    run_gpt(path)
    run_pixtral(path)
