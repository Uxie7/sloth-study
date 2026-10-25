"use client";

export default function ProgressView({ events }) {
  const latest = events.at(-1);
  return <section className="progress-view">
    <p className="lede">{latest?.note || "Preparing your study kit..."}</p>
    <div className="pbar"><i style={{ width: `${latest?.pct || 0}%` }} /></div>
    <ol className="steps">
      {events.map((event, index) => <li className={index === events.length - 1 ? "now" : "done"} key={`${event.step}-${index}`}>{event.note}</li>)}
    </ol>
  </section>;
}
