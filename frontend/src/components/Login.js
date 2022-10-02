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
    // props.load();
  }

  return (
    <div className="container form">
      <form onSubmit={handleSubmit}>
        <div className="input-container">
          <label>Username </label>
          <input
            type="text"
            name="uname"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            required
          />
        </div>
        <div className="input-container">
          <label>Password </label>
          <input
            type="password"
            name="pass"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="button-container">
          <input type="submit" />
        </div>
      </form>
    </div>
  );
}
