import Link from "next/link";

export default function Home() {
  return (
    <main>
      <section className="hero">
        <div>
          <h1>Your notes, turned into a revision kit.</h1>
          <p className="lede">Drop in a PDF or lecture slides. Sloth Study reads them with an open model on your own computer and builds everything you need to revise. No internet, no account, no subscription.</p>
          <div className="btns"><Link className="btn main" href="/upload">Make a kit</Link><Link className="btn" href="/library">See the app</Link></div>
        </div>
        <div className="out" aria-label="What you get">
          <div><b>A summary</b><span>The key points on one screen.</span></div>
          <div><b>Flashcards</b><span>One fact per card, ready to flip.</span></div>
          <div><b>A scored quiz</b><span>Multiple choice, with explanations.</span></div>
          <div><b>A five-minute audio brief</b><span>Read aloud by a local voice.</span></div>
        </div>
      </section>
      <section className="band"><h2>Three steps, none of them yours</h2><div className="cols">
        <div><span>1</span><h3>Drop in your material</h3><p>A PDF, slides or messy notes. The file never leaves your machine.</p></div>
        <div><span>2</span><h3>Let Gemma do the boring bit</h3><p>An open model finds the facts, writes questions and makes a brief.</p></div>
        <div><span>3</span><h3>Revise when you feel like it</h3><p>Flip cards, take the quiz, or listen while you make tea.</p></div>
      </div></section>
      <section className="band"><h2>Why it runs on your machine</h2><div className="cols">
        <div><h3>Private by default</h3><p>Your notes stay in local files and SQLite. No account required.</p></div>
        <div><h3>Open and swappable</h3><p>Gemma, Piper and small adapters keep the stack yours.</p></div>
        <div><h3>Made for the lazy</h3><p>Ten minutes of setup saves hours of making cards by hand.</p></div>
      </div><div className="btns" style={{ marginTop: 48 }}><Link className="btn main" href="/upload">Make your first kit</Link></div></section>
    </main>
  );
}
