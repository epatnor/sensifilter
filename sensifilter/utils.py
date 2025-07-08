# utils.py

import cv2
import numpy as np
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


# Beräknar uppskattad andel hud i en bild baserat på RGB-tröskelregler
def estimate_skin_percent(image_path):
    image = load_image(image_path)
    pixels = list(image.getdata())
    skin_pixels = 0

    for pixel in pixels:
        r, g, b = pixel
        if (
            r > 95 and g > 40 and b > 20 and
            max(pixel) - min(pixel) > 15 and
            abs(r - g) > 15 and r > g and r > b
        ):
            skin_pixels += 1

    total_pixels = len(pixels)
    if total_pixels == 0:
        return 0.0

    return (skin_pixels / total_pixels) * 100
