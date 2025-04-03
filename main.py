from processors.gpt import run_gpt, run_gpt_with_noise
from processors.pixtral import run_pixtral, run_pixtral_with_noise
from processors.textract import run_textract, run_textract_with_noise
import modules.constants
import modules.helpers

paths = [
    r"testfiles\output_page_1.pdf",
    r"testfiles\output_page_2.pdf",
    r"testfiles\output_page_3.pdf",
    r"testfiles\output_page_4.pdf",
    r"testfiles\output_page_5.pdf",
    r"testfiles\output_page_6.pdf",
    r"testfiles\output_page_7.pdf",
    r"testfiles\output_page_8.pdf",
]

for path in paths:
    run_gpt(path)
    run_gpt_with_noise(path)
    modules.helpers.clear_temp_folder()
    run_pixtral(path)
    run_pixtral_with_noise(path)
    modules.helpers.clear_temp_folder()

modules.helpers.sort_outputs()