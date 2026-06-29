import os
import shutil
import random

# Correct paths
source_dir = r"C:\Users\Admin\Desktop\plantvillage\color"
dest_dir = r"C:\Users\Admin\Desktop\leaf-cnn-rebuild\data"

# 10 diseases with exact folder names
disease_map = {
    "Healthy":          "Potato___healthy",
    "Early_Blight":     "Potato___Early_blight",
    "Late_Blight":      "Potato___Late_blight",
    "Bacterial_Spot":   "Pepper,_bell___Bacterial_spot",
    "Powdery_Mildew":   "Squash___Powdery_mildew",
    "Rust":             "Corn_(maize)___Common_rust_",
    "Leaf_Spot":        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Apple_Scab":       "Apple___Apple_scab",
    "Mosaic_Virus":     "Tomato___Tomato_mosaic_virus",
    "Septoria_Leaf_Spot": "Tomato___Septoria_leaf_spot"
}

random.seed(42)

for class_name, source_folder in disease_map.items():
    source_path = os.path.join(source_dir, source_folder)

    if not os.path.exists(source_path):
        print(f"NOT FOUND: {source_path}")
        continue

    images = os.listdir(source_path)
    random.shuffle(images)

    split = int(0.8 * len(images))
    train_imgs = images[:split]
    val_imgs = images[split:]

    for split_name, split_imgs in [("train", train_imgs), ("val", val_imgs)]:
        dest_path = os.path.join(dest_dir, split_name, class_name)
        os.makedirs(dest_path, exist_ok=True)
        for img in split_imgs:
            shutil.copy(
                os.path.join(source_path, img),
                os.path.join(dest_path, img)
            )

    print(f"Done: {class_name} — train: {len(train_imgs)}, val: {len(val_imgs)}")

print("\nAll done!")