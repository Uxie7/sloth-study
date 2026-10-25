"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LibraryPage() {
  const [kits, setKits] = useState([]);
  useEffect(() => { fetch(`${API_URL}/api/kits`).then((response) => response.json()).then(setKits).catch(() => setKits([])); }, []);
  return <main className="view"><h1>Your kits</h1><p className="lede">Saved revision kits will appear here.</p><div className="list">{kits.length ? kits.map((kit) => <Link className="row" href={`/kit/${kit.id}`} key={kit.id}><b>{kit.title}</b><span>Open kit</span></Link>) : <p className="note">No kits yet. Make one from a PDF to get started.</p>}</div><Link className="btn main" href="/upload">Make a new kit</Link></main>;
}
