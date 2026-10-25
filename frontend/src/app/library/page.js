import Link from "next/link";

export default function LibraryPage() {
  return <main className="view"><h1>Your kits</h1><p className="lede">Saved revision kits will appear here.</p><div className="list"><p className="note">No kits yet. Make one from a PDF to get started.</p></div><Link className="btn main" href="/upload">Make a new kit</Link></main>;
}
