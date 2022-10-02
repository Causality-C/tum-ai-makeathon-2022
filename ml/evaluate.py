"""Evaluation of the model."""
import azureml.core
from azureml.core import Workspace
from azureml import core
from tqdm import tqdm
import numpy as np
from torch.utils.data import DataLoader
import torch
from ml_utils import DiseaseDataset

subscription_id = 'c0e252b0-50d3-44e6-bb79-a007a94e3a9e'
resource_group = 'ml_rg'
workspace_name = 'machine_learning1'

ws = Workspace(subscription_id, resource_group, workspace_name)
ds1 = core.Dataset.get_by_name(ws, name='chexpert')

df_valid = ds1.to_pandas_dataframe()
df = df_valid.copy()
for i, p in enumerate(df_valid["Path"]):
    df["Path"][i] = p[20:]


######  TEST DATA  ######
# Test Labels
labels = list(df.columns[5:])
label_arr_test = df[labels].to_numpy()

# Test Data Loader
batch_size = 5
test_data = DiseaseDataset('valid', label_arr_test)
test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

######   MODEL  ######
model_path = "models/densenet121_valid.pth"
model = torch.load(model_path)

# def calculate_metrics(pred, target, threshold=0.5):
#     from sklearn.metrics import precision_score, recall_score, f1_score
#     pred = np.array(pred > threshold, dtype=float)
#     return {'micro/precision': precision_score(y_true=target, y_pred=pred, average='micro'),
#             'micro/recall': recall_score(y_true=target, y_pred=pred, average='micro'),
#             'micro/f1': f1_score(y_true=target, y_pred=pred, average='micro'),
#             'macro/precision': precision_score(y_true=target, y_pred=pred, average='macro'),
#             'macro/recall': recall_score(y_true=target, y_pred=pred, average='macro'),
#             'macro/f1': f1_score(y_true=target, y_pred=pred, average='macro'),
#             'samples/precision': precision_score(y_true=target, y_pred=pred, average='samples'),
#             'samples/recall': recall_score(y_true=target, y_pred=pred, average='samples'),
#             'samples/f1': f1_score(y_true=target, y_pred=pred, average='samples'),
#             }
   
def validate(model, dataloader, criterion=torch.nn.BCELoss(), threshold=0.5):
    """
    """
    print('Validating')
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model.eval()
    counter = 0
    val_running_loss = 0.0
    with torch.no_grad():
        model_result = []
        target_list = []
        for data in dataloader:
            counter += 1
            data, target = data['image'].to(device), data['label'].to(device)
            outputs = model(data)
            pred = np.array(outputs.cpu().numpy() > threshold, dtype=float)
            model_result.extend(pred)
            target_list.extend(target.cpu().numpy())
            # apply sigmoid activation to get all the outputs between 0 and 1
            loss = criterion(outputs, target)
            val_running_loss += loss.item()
        
        val_loss = val_running_loss / counter
        return val_loss, model_result


test_loss, predictions = validate(model, test_loader)

print(test_loss)