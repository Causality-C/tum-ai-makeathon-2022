import React, { Component, useState } from "react";
import PropTypes from "prop-types";


export default class Login extends Component{
    // const [errorMessages, setErrorMessages] = useState({});
    // const [isSubmitted, setIsSubmitted] = useState(false);

    // const errors = {
    //     uname: "invalid username",
    //     pass: "invalid password"
    // };

    // const database = [
    //     {
    //     username: "user1",
    //     password: "pass1"
    //     },
    //     {
    //     username: "user2",
    //     password: "pass2"
    //     }
    // ];
    constructor(props) {
        super(props);

        this.database = [
            {
            username: "user1",
            password: "pass1"
            },
            {
            username: "user2",
            password: "pass2"
            }
        ];

        this.errors = {
            uname: "invalid username",
            pass: "invalid password"
        }

        [this.isSubmitted, this.setIsSubmitted] = useState(false);

        // Binding method
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    


    handleSubmit(event) {
        //Prevent page reload
        event.preventDefault();

        var { uname, pass } = document.forms[0];

        // Find user login info

        const userData = this.database.find((user) => user.username === uname.value);

        // Compare user info
        if (userData) {
            if (userData.password !== pass.value) {
                // Invalid password
                this.setErrorMessages({ name: "pass", message: this.errors.pass });
            } else {
                this.setIsSubmitted(true);
            }
        } else {
            // Username not found
            this.setErrorMessages({ name: "uname", message: this.errors.uname });
        }
    }

    // renderErrorMessage(name) {
    //     return name === this.errorMessages.name && (
    //         <div className="error">{this.errorMessages.message}</div>
    //     );
    // }

    render()
    {
        return (
            <div className="container form">
                <form onSubmit={this.handleSubmit}>
                    <div className="input-container">
                        <label>Username </label>
                        <input type="text" name="uname" required />
                    </div>
                    <div className="input-container">
                        <label>Password </label>
                        <input type="password" name="pass" required />
                    </div>
                    <div className="button-container">
                        <input type="submit" />
                    </div>
                </form>
            </div>
        )
        return (
            <div className="form">
                <form onSubmit={this.handleSubmit}>
                    <div className="input-container">
                    <label>Username </label>
                    <input type="text" name="uname" required />
                    {this.renderErrorMessage("uname")}
                    </div>
                    <div className="input-container">
                    <label>Password </label>
                    <input type="password" name="pass" required />
                    {this.renderErrorMessage("pass")}
                    </div>
                    <div className="button-container">
                    <input type="submit" />
                    </div>
                </form>
            </div>
    );
    }
}
