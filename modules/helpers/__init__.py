import numpy as np
from PIL import Image
import os
import sys
import shutil
import pdf2image

sys.path.append(os.path.dirname(os.path.dirname((__file__))))

import constants

def add_noise_to_image(path):
    output_path = r'temp\verrauschtes_bild.png'

    original_image = Image.open(path)
    image_array = np.array(original_image)

    mean = 0
    std_dev = 50  # Standardabweichung 
    gaussian_noise = np.random.normal(mean, std_dev, image_array.shape).astype(np.int16)

    noisy_image_array = image_array.astype(np.int16) + gaussian_noise
    noisy_image_array = np.clip(noisy_image_array, 0, 255).astype(np.uint8)

    noisy_image = Image.fromarray(noisy_image_array)
    noisy_image.save(output_path)
    
    return output_path


def clear_temp_folder():
    for filename in os.listdir(constants.temp_dir):
        file_path = os.path.join(constants.temp_dir, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')

    print("temp folder cleared")

def sort_outputs():
    for model in constants.model_list:
        if not os.path.exists(os.path.join(constants.output_dir, model)):
            os.makedirs(os.path.join(constants.output_dir, model))
    
    for file in os.listdir(constants.output_dir):
        if os.path.isfile(os.path.join(constants.output_dir, file)):
            for model in constants.model_list:
                if model in file:
                    shutil.move(os.path.join(constants.output_dir, file), os.path.join(constants.output_dir, model, file))

def pdf_to_image(pdf_path, output_folder="temp"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = pdf2image.convert_from_path(pdf_path)
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page{i+1}.png")
        img.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

if __name__ == "__main__":
    sort_outputs()
    