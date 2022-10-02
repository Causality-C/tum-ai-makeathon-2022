import torch
import torchvision


def load_model(path):
    device = torch.device("cpu")
    model = torch.load(path, map_location=device)
    return model


def inference_single_image(path, image):
    model = load_model(path)
    transform = torchvision.transforms.Compose(
        [
            torchvision.transforms.ToTensor(),
            # transforms.CenterCrop(320),
            torchvision.transforms.Resize((320, 320)),
            torchvision.transforms.ConvertImageDtype(torch.float32),
        ]
    )
    input = transform(image)
    if len(input.shape) < 4:
        input = torch.unsqueeze(input, dim=0)
    prediction = model(input)
    return prediction
