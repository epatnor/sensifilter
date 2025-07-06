# utils.py

from PIL import Image

# === Ladda bild och konvertera till RGB ===
def load_image(image_path):
    with Image.open(image_path) as img:
        return img.convert("RGB")

# === Ändra storlek på bild (t.ex. inför modellinmatning) ===
def resize_image(image, size=(224, 224)):
    return image.resize(size)
