import React, { Component } from "react";
import Quiz from "./components/Quiz";
import Result from "./components/Result";
import QuizSelection from "./components/QuizSelection";
import Login from "./components/Login";
import "./App.css";
import { getData, postData, baseURL, putData } from "./util";

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      counter: 0,
      questionId: 1,
      question: "",
      answerOptions: [],
      answer: "",
      answersCount: {},
      userAnswers: [],
      result: "",
      questionSet: null,
      quizAnswers: [],
      gameOptions: "",
      firstChoice: "",
      maxImages: 0,
      numImages: 0,
    };

    this.handleAnswerSelected = this.handleAnswerSelected.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.initiateGame = this.initiateGame.bind(this);
    this.loadDataset = this.loadDataset.bind(this);
  }

  loadDataset() {
    getData(`${baseURL}dataset/datasets`)
      .then((data) => {
        const parsedData = data.map((item) => {
          return {
            dataset_name: item.dataset_name,
            images: parseInt(item.images),
          };
        });
        this.setState({
          gameOptions: parsedData,
          firstChoice: parsedData[0].dataset_name,
          maxImages: parsedData[0].images,
        });
      })
      .catch((e) => {
        console.log(e);
      });
  }
  componentDidMount() {
    if (localStorage.getItem("token")) {
      this.loadDataset();
    }
  }

  initiateGame() {
    postData(`${baseURL}dataset/create_game`, localStorage.getItem("token"), {
      images: parseInt(this.state.numImages),
      dataset: this.state.firstChoice,
    })
      .then((data) => {
        const { true_labels, dataset_name, bucket_url, answer_choices } = data;
        this.setState({
          dataset: dataset_name,
          quizAnswers: true_labels,
        });

        // Set Questions and Answers Object
        const qa = true_labels.map((label, i) => ({
          question: "Classify the following image",
          answers: this.shuffleArray(
            answer_choices[i].map((option) => {
              return { content: option, type: option };
            })
          ),
          answer: label,
          img: `${bucket_url}/${i}.jpeg`,
        }));
        // Set the question and answer options
        this.setState({
          questionSet: qa,
          question: qa[this.state.counter]["question"],
          answerOptions: qa[this.state.counter]["answers"],
        });
      })
      .catch((e) => {
        console.log(e);
      });
  }

  shuffleArray(array) {
    var currentIndex = array.length,
      temporaryValue,
      randomIndex;

    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;

      // And swap it with the current element.
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }

    return array;
  }

  handleAnswerSelected(event) {
    this.state.userAnswers.push(event.currentTarget.value);

    if (this.state.questionId < this.state.questionSet.length) {
      setTimeout(() => this.setNextQuestion(), 300);
    } else {
      setTimeout(() => this.getResults(), 300);
    }
  }

  setNextQuestion() {
    const counter = this.state.counter + 1;
    const questionId = this.state.questionId + 1;

    this.setState({
      counter: counter,
      questionId: questionId,
      question: this.state.questionSet[counter].question,
      answerOptions: this.state.questionSet[counter].answers,
      answer: "",
    });
  }
  handleChange(e) {
    // Get the number of images in the dataset
    const res = this.state.gameOptions.filter((obj) => {
      return obj.dataset_name === e.target.value;
    })[0]["images"];
    this.setState({ firstChoice: e.target.value, maxImages: res });
  }
  getResults() {
    // Replace logic with ones we call
    putData(`${baseURL}dataset/game_end`, localStorage.getItem("token"), {
      correct: this.state.quizAnswers,
      received: this.state.userAnswers,
    }).then((data) => {
      this.setState({ result: data });
    });
  }

  renderQuiz() {
    return (
      <Quiz
        answer={this.state.answer}
        answerOptions={this.state.answerOptions}
        questionId={this.state.questionId}
        question={this.state.question}
        questionTotal={this.state.questionSet.length}
        onAnswerSelected={this.handleAnswerSelected}
      />
    );
  }

  renderResult() {
    return <Result quizResult={this.state.result} />;
  }

  render() {
    return (
      <div className="App">
        <div className="App-header d-flex justify-content-between align-items-center">
          <img src="/logo.png" className="logo" width={400} height={400} />
          {this.state.questionSet && (
            <img
              src={this.state.questionSet[this.state.counter].img}
              alt="logo"
              height="30%"
            />
          )}
          {localStorage.getItem("user") && (
            <div>
              <h2 style={{ marginBottom: "20px" }}>
                User: {localStorage.getItem("user")}
              </h2>
              <button
                className="btn btn-primary"
                onClick={() => {
                  localStorage.clear();
                  window.location.reload(false);
                }}
              >
                Logout
              </button>
            </div>
          )}
        </div>
        {this.state.questionSet ? (
          this.state.result ? (
            this.renderResult()
          ) : (
            this.renderQuiz()
          )
        ) : this.state.gameOptions ? (
          <div>
            <QuizSelection
              choice={this.state.firstChoice}
              handleChange={this.handleChange}
              datasets={this.state.gameOptions}
              maxImages={this.state.maxImages}
              numImages={this.state.numImages}
              handleNumImageChange={(e) =>
                this.setState({ numImages: e.target.value })
              }
              handleFinish={this.initiateGame}
            />
          </div>
        ) : (
          <Login load={this.loadDataset} />
        )}
      </div>
    );
  }
}

export default App;
