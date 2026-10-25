"use client";

import Link from "next/link";
import { useState } from "react";
import ProgressView from "../components/ProgressView";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [voice, setVoice] = useState("none");
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [kitId, setKitId] = useState("");

  async function consumeBuild(response) {
    if (!response.ok || !response.body) throw new Error("The API could not start the build.");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const messages = buffer.split("\n\n");
      buffer = messages.pop() || "";
      for (const message of messages) {
        const line = message.split("\n").find((item) => item.startsWith("data: "));
        if (!line) continue;
        const event = JSON.parse(line.slice(6));
        setEvents((current) => [...current, event]);
        if (event.step === "done") setKitId(event.kit_id);
      }
      if (done) break;
    }
  }

  async function buildKit() {
    if (!file) return;
    setError(""); setKitId(""); setEvents([]);
    const form = new FormData();
    form.append("file", file); form.append("tts_provider", voice);
    try {
      await consumeBuild(await fetch(`${API_URL}/api/kits`, { method: "POST", body: form }));
    } catch (buildError) {
      setError(buildError.message);
    }
  }

  async function useSample() {
    setError(""); setKitId(""); setEvents([]);
    try {
      await consumeBuild(await fetch(`${API_URL}/api/samples/01_finance_money_basics.pdf`, { method: "POST" }));
    } catch (sampleError) {
      setError(sampleError.message);
    }
  }

  if (kitId) return <main className="view narrow"><h1>Your kit is ready.</h1><p className="lede">Your notes have been turned into a revision kit.</p><div className="btns"><Link className="btn main" href={`/kit/${kitId}`}>Open kit</Link><Link className="btn" href="/library">View library</Link></div></main>;
  return <main className="view narrow">
    <span className="chip">Running on this computer with gemma3:4b. No internet needed.</span>
    <h1>Make a kit</h1>
    <p className="lede">Choose a PDF, lecture slides, or notes. The file stays on your machine.</p>
    <label className="drop" htmlFor="study-file"><b>{file?.name || "Drop a PDF here, or choose a file"}</b><span>PDF, text or Markdown, up to about 30 pages</span><input id="study-file" type="file" accept=".pdf,.txt,.md" onChange={(event) => setFile(event.target.files?.[0] || null)} /></label>
    <fieldset><legend>Audio voice</legend><label><input type="radio" name="voice" value="piper" checked={voice === "piper"} onChange={() => setVoice("piper")} /> Piper (offline)</label><label><input type="radio" name="voice" value="none" checked={voice === "none"} onChange={() => setVoice("none")} /> No audio (low-storage mode)</label><label><input type="radio" name="voice" value="elevenlabs" checked={voice === "elevenlabs"} onChange={() => setVoice("elevenlabs")} /> ElevenLabs (optional)</label></fieldset>
    <div className="btns"><button className="btn main" disabled={!file} onClick={buildKit}>Build kit</button><button className="btn" type="button" onClick={useSample}>Use a sample instead</button></div>
    {error && <p className="notice error" role="alert">{error}</p>}
    {events.some((event) => event.step === "chunk_failed") && <p className="notice" role="status">Some sections were skipped, but the rest of the kit is available.</p>}
    {events.some((event) => event.step === "audio_failed") && <p className="notice" role="status">The kit was created without audio because the voice provider was unavailable.</p>}
    {events.length > 0 && <ProgressView events={events} />}
  </main>;
}
