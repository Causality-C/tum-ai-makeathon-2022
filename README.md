# Diagnostics. Let's quiz

## General 

The `diagnostics. Let's quiz` app is a game for medical students, where they can
train in an interactive manner. In order to make the CT Diagnosis training more
interactive, our app provides quizzes for the students where they can test their
knowledge of how to accurately interpret a CT scan.

The app is built with Flask (Backend) and React (Frontend)

## How to start the application
### Backend

Prerequisites:
- python3

In order for the backend to successfully connect to the AWS Services, you need
to create a .env file.
```bash
cd backend;
touch .env;
```

In the .env file, please provide the following information:
```env
AWS_ACCESS_KEY=[AWS_ACCESS_KEY]
AWS_SECRET_KEY=[AWS_SECRET_KEY]
JWT_SALT='alsdjflasdfjsadlfjlsfjaksjfohioh'
MODEL_PATH="ml_dev/densenet121_valid.pth"
```
For a live demo, please contact us, in order to provide you with the
AWS_ACCESS_KEY, AWS_SECRET_KEY.

After that, while int the backend folder, create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install the requirements:
```bash
pip install -r requirements.txt
```

Now you can start the backend server with:
```bash
flask run --no-debugger --no-reload -p 4100
```

### Frontend
After successfully starting the backend, you can now start the frontend.

Prerequisites:
- npm

Install the npm packages througb:
```bash
cd frontend; npm install
```

Start the node server through:
```bash
npm start
```

Now you can open http://localhost:3000 in your web browser and your application
is running! 


# How to play the game
Open the web browser and log into the game with the following example User:
Login: NotJeffreys
Password: abc123

While the registration API for signing up is present, the frontend does not yet
have a registration view.

After that you land on the Quiz Selection Page, where you can select the dataset
that you want to be using and you can select the number of images you would like
to practice your medical training on.

After clicking on submit you will be forwarded to the Quiz. Now it's your time
to shine and choose the disease that you can identify in the picture.

After completing the last Quiz Question you will be redirected to a page where
you can see your results and you can see how your rating has changed.


## AI & Machine Learning

**Machine Learning**

**Training**
The Densenet121 is used as the backbone of the training. The training is a multilabel classification meaning that each image can have multiple labels assigned to it. The training has been done on roughly 120000 data and 3 epochs using binary cross entropy loss with a treshold of 0.4 and tested on roughly 250 samples. 

**Folder Structure**
- data: Toy data for rapid prototyping
- model: saved models
- notebooks: jupyter notebooks for experimenting
- utils: utilities for dataclass and backend-ml API

**Results**
The following shows the ROC curve of the training for each class

![alt text](https://github.com/Causality-C/tum-ai-makeathon-2022/blob/ml-dev/ml/roc_curve.jpg?raw=true)




