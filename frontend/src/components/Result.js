import React from "react";
import PropTypes from "prop-types";
import { CSSTransitionGroup } from "react-transition-group";

function Result(props) {
  return (
    <CSSTransitionGroup
      className="container result"
      component="div"
      transitionName="fade"
      transitionEnterTimeout={800}
      transitionLeaveTimeout={500}
      transitionAppear
      transitionAppearTimeout={500}
    >
      <div>
        <h1>Quiz Summary for {props.quizResult.username}</h1>
        <h3>
          Performance: {props.quizResult.num_correct} /{" "}
          {props.quizResult.num_correct + props.quizResult.num_incorrect}
        </h3>
        <h3>New Score: {props.quizResult.new_score}</h3>
      </div>
    </CSSTransitionGroup>
  );
}

Result.propTypes = {
  quizResult: PropTypes.string.isRequired,
};

export default Result;
