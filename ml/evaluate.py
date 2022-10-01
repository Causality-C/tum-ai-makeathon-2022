"""Evaluation of the model."""
import azureml.core
from azureml.core import Workspace, Dataset
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
import torch
from pipeline import DiseaseDataset, device, criterion

subscription_id = 'c0e252b0-50d3-44e6-bb79-a007a94e3a9e'
resource_group = 'ml_rg'
workspace_name = 'machine_learning1'

ws = Workspace(subscription_id, resource_group, workspace_name)
ds1 = Dataset.get_by_name(ws, name='chexpert')

df_valid = ds1.to_pandas_dataframe()
df = df_valid
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

def calculate_metrics(pred, target, threshold=0.5):
    from sklearn.metrics import precision_score, recall_score, f1_score
    pred = np.array(pred > threshold, dtype=float)
    return {'micro/precision': precision_score(y_true=target, y_pred=pred, average='micro'),
            'micro/recall': recall_score(y_true=target, y_pred=pred, average='micro'),
            'micro/f1': f1_score(y_true=target, y_pred=pred, average='micro'),
            'macro/precision': precision_score(y_true=target, y_pred=pred, average='macro'),
            'macro/recall': recall_score(y_true=target, y_pred=pred, average='macro'),
            'macro/f1': f1_score(y_true=target, y_pred=pred, average='macro'),
            'samples/precision': precision_score(y_true=target, y_pred=pred, average='samples'),
            'samples/recall': recall_score(y_true=target, y_pred=pred, average='samples'),
            'samples/f1': f1_score(y_true=target, y_pred=pred, average='samples'),
            }
   
def validate(model, dataloader, criterion, val_data, device):
    """
    """
    print('Validating')
    model.eval()
    counter = 0
    val_running_loss = 0.0
    with torch.no_grad():
        model_result = []
        targets = []
        for data in dataloader:
            counter += 1
            data, targets = data['image'].to(device), data['label']
            outputs = model(data)
            model_result.extend(outputs.cpu().numpy())
            targets.extend(targets.cpu().numpy())
            # apply sigmoid activation to get all the outputs between 0 and 1
            outputs = torch.sigmoid(outputs)
            loss = criterion(outputs, targets)
            val_running_loss += loss.item()
        
        val_loss = val_running_loss / counter
        return val_loss    