"use client";

import { useState } from "react";

export default function FlashCard({ cards }) {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const card = cards[index];
  function move(nextIndex) {
    setIndex((nextIndex + cards.length) % cards.length);
    setFlipped(false);
  }
  return <button className={`deck${flipped ? " flip" : ""}`} onClick={() => setFlipped(!flipped)} aria-label="Flashcard, press to flip">
    <span className="deck-in">
      <span className="face"><span>{card.question}</span><small>Press to flip</small></span>
      <span className="face back"><span>{card.answer}</span><small>Answer</small></span>
    </span>
    <span className="ctl">
      <span className="btn" role="button" onClick={(event) => { event.stopPropagation(); move(index - 1); }}>Previous</span>
      <span className="btn main" role="button" onClick={(event) => { event.stopPropagation(); move(index + 1); }}>Next</span>
      <span className="cnt">{index + 1} / {cards.length}</span>
    </span>
  </button>;
}
