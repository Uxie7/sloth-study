export default function AudioPlayer({ kitId, script }) {
  return <div>
    <audio controls className="audio" src={`/api/audio/${kitId}`} />
    <p className="script">{script}</p>
  </div>;
}
