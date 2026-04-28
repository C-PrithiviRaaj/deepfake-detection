import os
import numpy as np
from PIL import Image

def generate_dummy_dataset(base_dir="dataset", num_images_per_class=20, img_size=(128, 128)):
    """
    Generates a dummy dataset of random noise images for testing the pipeline.
    Real datasets like FaceForensics++ are huge and require permission to download.
    """
    classes = ["real", "fake"]
    
    for cls in classes:
        dir_path = os.path.join(base_dir, cls)
        os.makedirs(dir_path, exist_ok=True)
        
        for i in range(num_images_per_class):
            # Generate random noise image
            img_array = np.random.randint(0, 256, (img_size[0], img_size[1], 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(os.path.join(dir_path, f"{cls}_{i}.jpg"))
            
    print(f"✅ Dummy dataset generated in '{base_dir}' with {num_images_per_class} images per class.")
    print("For a real dataset, please download FaceForensics++ or Celeb-DF, extract them, and place them in dataset/real and dataset/fake.")

if __name__ == "__main__":
    generate_dummy_dataset()
