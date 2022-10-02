import React, { useState } from "react";
import { baseURL, postData } from "../util";

export default function Login(props) {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event) {
    //Prevent page reload
    event.preventDefault();
    postData(`${baseURL}auth/login`, "", {
      username: user,
      password: password,
    }).then((user) => {
      const { token, username } = user;
      localStorage.setItem("token", token);
      localStorage.setItem("user", username);
      props.load();
    });
  }

  return (
    <div className="container bg-transparent d-flex justify-content-center">
      <div className="container form">
        <form onSubmit={handleSubmit}>
          <div className="p-2 form-group-mb-2">
            <label>Username </label>
            <input
              className="form-control"
              type="text"
              class="form-control"
              name="uname"
              value={user}
              onChange={(e) => setUser(e.target.value)}
              required
            />
          </div>
          <div className="p-2 form-group-mb-2">
            <label>Password </label>
            <input
              className="form-control"
              type="password"
              class="form-control"
              name="pass"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="p-2 button-container">
            <button className="btn btn-primary" type="submit">
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
