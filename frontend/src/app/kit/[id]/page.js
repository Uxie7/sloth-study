"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AudioPlayer from "../../components/AudioPlayer";
import FlashCard from "../../components/FlashCard";
import Quiz from "../../components/Quiz";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function KitPage({ params }) {
  const [kit, setKit] = useState(null);
  const [tab, setTab] = useState("summary");
  useEffect(() => { params.then(({ id }) => fetch(`${API_URL}/api/kits/${id}`).then((response) => response.ok ? response.json() : Promise.reject()).then(setKit).catch(() => setKit({ error: true }))); }, [params]);
  if (!kit) return <main className="view"><p className="lede">Loading kit...</p></main>;
  if (kit.error) return <main className="view"><h1>Kit not found</h1><Link className="btn" href="/library">Back to library</Link></main>;
  const tabs = ["summary", "cards", "quiz", "audio"];
  return <main className="view"><Link href="/library" className="note">← Your kits</Link><h1>{kit.title}</h1>
    <div className="tabs" role="tablist">{tabs.map((name) => <button className="tab" role="tab" aria-selected={tab === name} key={name} onClick={() => setTab(name)}>{name === "cards" ? "Flashcards" : name === "audio" ? "Audio brief" : name[0].toUpperCase() + name.slice(1)}</button>)}</div>
    {tab === "summary" && <div className="panel on"><ul className="sum">{kit.summary.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}</ul></div>}
    {tab === "cards" && <div className="panel on">{kit.flashcards.length ? <FlashCard cards={kit.flashcards} /> : <p className="note">No flashcards generated.</p>}</div>}
    {tab === "quiz" && <div className="panel on"><Quiz questions={kit.quiz} /></div>}
    {tab === "audio" && <div className="panel on"><AudioPlayer kitId={kit.id} script={kit.summary.brief_script} /></div>}
  </main>;
}
