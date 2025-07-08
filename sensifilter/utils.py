# utils.py

import cv2
from PIL import Image


# Laddar bild som PIL-RGB (för analys som BLIP eller captioning)
def load_image(image_path):
    with Image.open(image_path) as img:
        return img.convert("RGB")


# Laddar bild som OpenCV-BGR (för YOLO, boxar m.m.)
def load_image_bgr(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    return image


# Skalar en PIL-bild till angiven storlek (används av vissa modeller)
def resize_image(image, size=(224, 224)):
    return image.resize(size)
