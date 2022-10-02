**Machine Learning**

**Training**
The Densenet121 is used as the backbone of the training. The training is a multilabel classification meaning that each image can have multiple labels assigned to it. The training has been done on roughly 120000 data and 3 epochs using binary cross entropy loss with a treshold of 0.4. 

**Folder Structure**
- data: Toy data for rapid prototyping
- model: saved models
- notebooks: jupyter notebooks for experimenting
- utils: utilities for dataclass and backend-ml API
