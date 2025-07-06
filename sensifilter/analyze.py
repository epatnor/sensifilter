# scene.py

# Scene classifier using Places365 and ResNet18
import torch
from torchvision import models, transforms
from PIL import Image
import os
import urllib.request

# === Paths & constants ===
PLACES365_WEIGHTS_URL = "http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar"
PLACES365_LABELS_URL = "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"
WEIGHTS_PATH = os.path.join("models", "resnet18_places365.pth.tar")
LABELS_PATH = os.path.join("models", "categories_places365.txt")

# === Preprocessing for input images ===
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])


# === Load model, labels, and prepare ===
def _load_model():
    # Ladda etiketter om de saknas
    if not os.path.exists(LABELS_PATH):
        os.makedirs(os.path.dirname(LABELS_PATH), exist_ok=True)
        urllib.request.urlretrieve(PLACES365_LABELS_URL, LABELS_PATH)

    classes = [line.strip().split(' ')[0][3:] for line in open(LABELS_PATH)]
    
    # Ladda modellvikter om de saknas
    if not os.path.exists(WEIGHTS_PATH):
        os.makedirs(os.path.dirname(WEIGHTS_PATH), exist_ok=True)
        urllib.request.urlretrieve(PLACES365_WEIGHTS_URL, WEIGHTS_PATH)

    model = models.resnet18(num_classes=365)
    checkpoint = torch.load(WEIGHTS_PATH, map_location=torch.device('cpu'))
    state_dict = {str(k.replace("module.", "")): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()

    return model, classes


# === Klassificera en bild med Places365 ===
def classify_scene(image_path):
    model, classes = _load_model()

    img = Image.open(image_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0)  # Add batch dim

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        top_idx = probs.argmax().item()
        top_label = classes[top_idx]
        confidence = probs[top_idx].item()

    return f"{top_label} ({confidence:.2f})"
