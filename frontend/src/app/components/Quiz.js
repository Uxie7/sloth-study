"use client";

import { useState } from "react";

export default function Quiz({ questions, chunks }) {
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [showSource, setShowSource] = useState(false);
  const question = questions[current];
  if (!question) return <p className="note">No quiz questions were generated.</p>;
  const selected = answers[current];
  const complete = current === questions.length - 1 && selected !== undefined;
  const score = answers.filter((answer, index) => answer === questions[index]?.correct_index).length;
  const sourceText = chunks?.[question.source_chunk];
  if (complete) return <div><h2 style={{ font: "400 clamp(26px,3.2vw,36px)/1.2 var(--serif)", margin: "0 0 12px" }}>{score} / {questions.length}</h2><p className="note">Quiz complete. Try it again.</p><button className="btn main" onClick={() => { setCurrent(0); setAnswers([]); setShowSource(false); }}>Try again</button></div>;
  function optClass(i) {
    if (selected === undefined) return "opt";
    if (i === question.correct_index) return "opt right";
    if (i === selected) return "opt wrong";
    return "opt";
  }
  return <div><p className="qtext">{question.question}</p><div>
    {question.options.map((option, i) => <button className={optClass(i)} key={option} disabled={selected !== undefined} onClick={() => { setAnswers([...answers.slice(0, current), i]); setShowSource(false); }}>{option}</button>)}
  </div><p className="note">{selected !== undefined ? question.explanation : ""}</p>
    {selected !== undefined && sourceText && <div style={{ marginBottom: 14 }}><button className="btn" style={{ fontSize: 14, padding: "6px 14px" }} onClick={() => setShowSource((s) => !s)}>{showSource ? "Hide source" : "Show source"}</button>{showSource && <blockquote className="source-quote">{sourceText}</blockquote>}</div>}
    {selected !== undefined && <button className="btn main" onClick={() => { setCurrent(current + 1); setShowSource(false); }}>{current === questions.length - 1 ? "See score" : "Next question"}</button>}
    <span className="cnt">{current + 1} / {questions.length}</span>
  </div>;
}
