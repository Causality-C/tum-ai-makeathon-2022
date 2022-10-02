import torch
import torchvision
import os
import cv2


class Model:
    def __init__(self) -> None:
        self.model = None
        self.pred_classes = [
            "No Finding",
            "Enlarged Cardiomediastinum",
            "Cardiomegaly",
            "Lung Opacity",
            "Lung Lesion",
            "Edema",
            "Consolidation",
            "Pneumonia",
            "Atelectasis",
            "Pneumothorax",
            "Pleural Effusion",
            "Pleural Other",
            "Fracture",
            "Support Devices",
        ]
        pass

    def load_model(self, path):
        device = torch.device("cpu")
        self.model = torch.load(path, map_location=device)
        return

    def inference_multiple_images(self, dir):
        dir_list = os.listdir(dir)
        predictions = []
        for file in dir_list:
            img_loc = os.path.join(dir, file)
            img = cv2.imread(img_loc)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # extract the prediction with highest value
            prediction = self.pred_classes[
                torch.argmax(self.inference_single_image(img))
            ]
            predictions.append(prediction)
        return predictions

    def inference_single_image(self, image):
        if not self.model:
            return False
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
        prediction = self.model(input)
        return prediction
