import React from "react";
import logo from "../doktor.png";
export default function QuizSelection(props) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        alignItems: "center",
      }}
    >
      <h1>Choose Your Dataset</h1>
      <select value={props.choice} onChange={props.handleChange}>
        {props.datasets.map((option) => (
          <option value={option.dataset_name} enum={option.images}>
            {option.dataset_name}
          </option>
        ))}
      </select>
      <h1># Images for the Quiz</h1>
      <input
        type="number"
        min="1"
        max={props.maxImages}
        value={props.numImages}
        onChange={props.handleNumImageChange}
      />
      <button onClick={props.handleFinish}>Submit</button>
      <img src={logo} height="400px" />
      <button
        onClick={() => {
          localStorage.clear();
          window.location.reload(false);
        }}
      >
        Logout
      </button>
    </div>
  );
}
