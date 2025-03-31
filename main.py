from processors.gpt import run_gpt, run_gpt_with_noise
from processors.pixtral import run_pixtral      
import modules.helpers

paths = [
    r"testfiles\output_page_6.pdf"
]

for path in paths:
    run_gpt(path)
    run_gpt_with_noise(path)
    modules.helpers.clear_temp_folder()