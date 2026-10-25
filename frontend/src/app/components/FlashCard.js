"use client";

import { useState } from "react";

export default function FlashCard({ cards, chunks }) {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [known, setKnown] = useState(0);
  const [showSource, setShowSource] = useState(false);

  const card = cards[index];
  const sourceText = chunks?.[card.source_chunk];

  function move(nextIndex) {
    setIndex((nextIndex + cards.length) % cards.length);
    setFlipped(false);
    setShowSource(false);
  }

  function gotIt() {
    setKnown((k) => Math.min(k + 1, cards.length));
    move(index + 1);
  }

  return (
    <div>
      <button
        className={`deck${flipped ? " flip" : ""}`}
        onClick={() => setFlipped((f) => !f)}
        aria-label="Flashcard, press to flip"
      >
        <div className="deck-in">
          <div className="face">
            <span>{card.question}</span>
            <small>Press to flip</small>
          </div>
          <div className="face back">
            <span>{card.answer}</span>
            <small>Answer</small>
          </div>
        </div>
      </button>

      <div className="ctl">
        <button className="btn" onClick={() => move(index - 1)}>Previous</button>
        <button className="btn" onClick={() => move(index + 1)}>Again</button>
        <button className="btn main" onClick={gotIt}>Got it</button>
        <span className="cnt">{index + 1} / {cards.length} &middot; {known} known</span>
      </div>

      {sourceText && (
        <div style={{ marginTop: 12 }}>
          <button
            className="btn"
            style={{ fontSize: 14, padding: "6px 14px" }}
            onClick={() => setShowSource((s) => !s)}
          >
            {showSource ? "Hide source" : "Show source"}
          </button>
          {showSource && (
            <blockquote className="source-quote">{sourceText}</blockquote>
          )}
        </div>
      )}
    </div>
  );
}
