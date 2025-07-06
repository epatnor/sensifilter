# scene.py

import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os
import urllib.request

# === Paths ===
MODEL_PATH = os.path.join(os.path.dirname(__file__), "resnet18_places365.pth.tar")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "categories_places365.txt")


# === Ladda etiketter från Places365 ===
def load_labels():
    if not os.path.exists(LABELS_PATH):
        url = "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"
        urllib.request.urlretrieve(url, LABELS_PATH)

    with open(LABELS_PATH) as f:
        return [line.strip().split(" ")[0][3:] for line in f]


# === Ladda Places365-modellen ===
def load_model():
    if not os.path.exists(MODEL_PATH):
        url = "http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar"
        urllib.request.urlretrieve(url, MODEL_PATH)

    # 👇 Viktigt! Rätt antal klasser
    model = models.resnet18(num_classes=365)

    # Ta bort "module." från keys om modellen är tränad med DataParallel
    checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
    state_dict = {k.replace("module.", ""): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()
    return model


# === Förbehandling av bild ===
def transform_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    img = Image.open(image_path).convert('RGB')
    return transform(img).unsqueeze(0)


# === Klassificera scen i bild ===
def classify_scene(image_path):
    model = load_model()
    labels = load_labels()
    input_tensor = transform_image(image_path)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        top_idx = probs.argmax().item()
        top_label = labels[top_idx]
        confidence = probs[top_idx].item()

    return f"{top_label} ({confidence:.2f})"
