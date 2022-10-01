import torch
import torchvision

def load_model(path):
    model = torch.load(path)
    return model

def inference_single_image(path, image):
    model = load_model(path)
    transform = torchvision.transforms.Compose([
            torchvision.transforms.ToPILImage(),
            # transforms.CenterCrop(320),
            torchvision.transforms.Resize((320, 320)),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.ConvertImageDtype(torch.float32)
            ])
    input = transform(image)
    prediction = model(input)
    return prediction