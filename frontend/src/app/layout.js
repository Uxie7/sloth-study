import "./globals.css";
import Header from "./components/Header";

export const metadata = {
  title: "Sloth Study: your notes, turned into a revision kit",
  description: "Turn local lecture notes into a private revision kit.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="wrap">
          <Header />
          {children}
          <footer>Sloth Study · local-first revision, one lazy step at a time.</footer>
        </div>
      </body>
    </html>
  );
}
