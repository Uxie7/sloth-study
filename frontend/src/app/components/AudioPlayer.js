"use client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AudioPlayer({ kitId, script }) {
  return (
    <div>
      <audio controls className="audio" src={`${API_URL}/api/audio/${kitId}`} />
      <p className="script">{script}</p>
    </div>
  );
}
