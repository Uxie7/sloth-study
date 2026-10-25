"use client";

import { useState } from "react";

export default function UploadPage() {
  const [fileName, setFileName] = useState("");
  return <main className="view narrow">
    <span className="chip">Running on this computer with gemma3:4b. No internet needed.</span>
    <h1>Make a kit</h1>
    <p className="lede">Choose a PDF, lecture slides, or notes. The build shell is ready for the Phase 2 API.</p>
    <label className="drop" htmlFor="study-file">
      <b>{fileName || "Drop a PDF here, or choose a file"}</b>
      <span>PDF, text or Markdown, up to about 30 pages</span>
      <input id="study-file" type="file" accept=".pdf,.txt,.md" onChange={(event) => setFileName(event.target.files?.[0]?.name || "")} />
    </label>
    <fieldset><legend>Audio voice</legend><label><input type="radio" name="voice" defaultChecked /> Piper (offline)</label><label><input type="radio" name="voice" /> ElevenLabs (optional)</label></fieldset>
    <div className="btns"><button className="btn main" disabled={!fileName}>Build kit</button><button className="btn" type="button">Use a sample instead</button></div>
  </main>;
}
