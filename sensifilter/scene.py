# scene.py

import torch
import torchvision.transforms as transforms
from PIL import Image
import os

# === Ladda Places365-klasser och etiketter vid första körning ===
def load_labels():
    file_path = os.path.join(os.path.dirname(__file__), "categories_places365.txt")
    if not os.path.exists(file_path):
        import urllib.request
        url = "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"
        urllib.request.urlretrieve(url, file_path)
    with open(file_path) as f:
        return [line.strip().split(" ")[0][3:] for line in f]

# === Ladda Places365-modellen (ResNet18) ===
def load_model():
    model_file = os.path.join(os.path.dirname(__file__), "resnet18_places365.pth.tar")
    if not os.path.exists(model_file):
        import urllib.request
        url = "http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar"
        urllib.request.urlretrieve(url, model_file)

    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
    checkpoint = torch.load(model_file, map_location=torch.device('cpu'))
    state_dict = {str(k.replace("module.", "")): v for k, v in checkpoint["state_dict"].items()}
    model.load_state_dict(state_dict)
    model.eval()
    return model

# === Standardtransform för Places365-bilder ===
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

# === Klassificera scenen i bilden och returnera toppetikett ===
def classify_scene(image_path):
    model = load_model()
    labels = load_labels()
    input_tensor = transform_image(image_path)
    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.nn.functional.softmax(logits, dim=1)
        top_idx = torch.argmax(probs).item()
        top_label = labels[top_idx]
        return top_label
