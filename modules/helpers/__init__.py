import numpy as np
from PIL import Image
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname((__file__))))

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
    temp_folder = r'temp'
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')

    print("temp folder cleared")

if __name__ == "__main__":
    pass
