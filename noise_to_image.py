import numpy as np
from PIL import Image

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


if __name__ == "__main__":
    pass

