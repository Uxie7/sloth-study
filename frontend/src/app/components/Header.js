import Link from "next/link";

export default function Header() {
  return (
    <header>
      <Link className="logo" href="/">Sloth Study</Link>
      <nav aria-label="Main">
        <Link href="/">Home</Link>
        <Link href="/library">Library</Link>
        <Link href="/upload">New kit</Link>
      </nav>
    </header>
  );
}
