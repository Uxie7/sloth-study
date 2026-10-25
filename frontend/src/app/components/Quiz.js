"use client";

import { useState } from "react";

export default function Quiz({ questions }) {
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState([]);
  const question = questions[current];
  if (!question) return <p className="note">No quiz questions were generated.</p>;
  const selected = answers[current];
  const complete = current === questions.length - 1 && selected !== undefined;
  const score = answers.filter((answer, index) => answer === questions[index]?.correct_index).length;
  if (complete) return <div><h2>{score} / {questions.length}</h2><p className="note">Quiz complete. Review the explanations or try it again.</p><button className="btn main" onClick={() => { setCurrent(0); setAnswers([]); }}>Try again</button></div>;
  return <div><p className="qtext">{question.question}</p><div>
    {question.options.map((option, index) => <button className="opt" key={option} disabled={selected !== undefined} onClick={() => setAnswers([...answers.slice(0, current), index])}>{option}</button>)}
  </div><p className="note">{selected !== undefined ? question.explanation : ""}</p>
    {selected !== undefined && <button className="btn main" onClick={() => setCurrent(current + 1)}>Next question</button>}
    <span className="cnt">{current + 1} / {questions.length}</span>
  </div>;
}
