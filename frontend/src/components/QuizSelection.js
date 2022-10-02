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
      <h1 className="mt-4">Choose Your Dataset</h1>
      <div className="d-flex justify-content-center w-25 form-outline">
        <select
          className="w-50 form-select"
          value={props.choice}
          onChange={props.handleChange}
        >
          {props.datasets.map((option) => (
            <option value={option.dataset_name} enum={option.images}>
              {option.dataset_name}
            </option>
          ))}
        </select>
      </div>

      <h1 className="mt-4"># Images for the Quiz</h1>
      <div className="d-flex justify-content-center w-25 form-outline">
        <input
          className="w-50   form-control"
          style={{ marginBottom: "10px" }}
          type="number"
          for="typeNumber"
          min="1"
          max={props.maxImages}
          value={props.numImages}
          onChange={props.handleNumImageChange}
        />
      </div>

      <button className="btn btn-primary" onClick={props.handleFinish}>
        Submit
      </button>
    </div>
  );
}
