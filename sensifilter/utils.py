# utils.py

import cv2
import numpy as np
from PIL import Image


# PIL-RGB (för basic analys)
def load_image(image_path):
    with Image.open(image_path) as img:
        return img.convert("RGB")


# OpenCV-BGR (för YOLO/boxes)
def load_image_bgr(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    return image


def resize_image(image, size=(224, 224)):
    """
    Resizes an image to a given size.
    """
    return image.resize(size)


def estimate_skin_percent(image_path):
    """
    Naiv uppskattning av hudpixlar baserat på färgintervall i RGB.
    Returnerar % av bilden som tros vara hud.
    """
    image = load_image(image_path)
    pixels = list(image.getdata())
    skin_pixels = 0

    for pixel in pixels:
        r, g, b = pixel
        if (r > 95 and g > 40 and b > 20 and
            max(pixel) - min(pixel) > 15 and
            abs(r - g) > 15 and r > g and r > b):
            skin_pixels += 1

    total_pixels = len(pixels)
    if total_pixels == 0:
        return 0.0

    return (skin_pixels / total_pixels) * 100


# === YCrCb skin detection for boundingbox crops ===
def detect_skin(image_bgr):
    """
    Returnerar en binär mask av hudregioner i en BGR-bild med YCrCb-färgmodell.
    """
    img_ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    lower = np.array([0, 133, 77], dtype=np.uint8)
    upper = np.array([255, 173, 127], dtype=np.uint8)
    mask = cv2.inRange(img_ycrcb, lower, upper)
    return mask
