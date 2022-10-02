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
          <div className="form-group mb-2">
            <label>Username </label>
            <input
              className="form-control"
              type="text"
              name="uname"
              value={user}
              onChange={(e) => setUser(e.target.value)}
              required
            />
          </div>
          <div  className="form-group mb-2">
            <label>Password </label>
            <input
              className="form-control"
              type="password"
              name="pass"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" type="submit">
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}
// import React, { Component, useState } from "react";
// import PropTypes from "prop-types";

// export default class Login extends Component{
//     constructor(props) {
//         super(props);

//         this.database = [
//             {
//             username: "user1",
//             password: "pass1"
//             },
//             {
//             username: "user2",
//             password: "pass2"
//             }
//         ];

//         this.errors = {
//             uname: "invalid username",
//             pass: "invalid password"
//         }

//         // [this.isSubmitted, this.setIsSubmitted] = useState(false);

//         // Binding method
//         this.handleSubmit = this.handleSubmit.bind(this);
//     }

//     handleSubmit(event) {
//         //Prevent page reload
//         event.preventDefault();

//         var { uname, pass } = document.forms[0];

//         // Find user login info

//         const userData = this.database.find((user) => user.username === uname.value);

//         // Compare user info
//         if (userData) {
//             if (userData.password !== pass.value) {
//                 // Invalid password
//                 this.setErrorMessages({ name: "pass", message: this.errors.pass });
//             } else {
//                 this.setIsSubmitted(true);
//             }
//         } else {
//             // Username not found
//             this.setErrorMessages({ name: "uname", message: this.errors.uname });
//         }
//     }

//     // renderErrorMessage(name) {
//     //     return name === this.errorMessages.name && (
//     //         <div className="error">{this.errorMessages.message}</div>
//     //     );
//     // }

//     render()
//     {
//         return (
//             <div className="container bg-transparent d-flex justify-content-center">
//                 <form onSubmit={this.handleSubmit} className="">
//                     <div className="form-group mb-2">
//                         <label>Username </label>
//                         <input class="form-control" type="text" name="uname" required />
//                     </div>
//                     <div className="form-group mb-2">
//                         <label>Password </label>
//                         <input class="form-control" type="password" name="pass" required />
//                     </div>
//                     <button className="btn btn-primary" type="submit">Submit</button>
//                 </form>
//             </div>
//         )
//         return (
//             <div className="form">
//                 <form onSubmit={this.handleSubmit}>
//                     <div className="input-container">
//                     <label>Username </label>
//                     <input type="text" name="uname" required />
//                     {this.renderErrorMessage("uname")}
//                     </div>
//                     <div className="input-container">
//                     <label>Password </label>
//                     <input type="password" name="pass" required />
//                     {this.renderErrorMessage("pass")}
//                     </div>
//                     <div className="button-container">
//                     <input type="submit" />
//                     </div>
//                 </form>
//             </div>
//     );
//     }
// }
//
