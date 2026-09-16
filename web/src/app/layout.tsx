import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { Source_Serif_4 } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const sourceSerif = Source_Serif_4({
  variable: "--font-source-serif",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CA4 Oyez — Fourth Circuit Oral Arguments",
  description:
    "Oral arguments, panels, and opinions from the U.S. Court of Appeals for the Fourth Circuit.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${sourceSerif.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <header className="bg-navy text-white border-b-4 border-gold">
          <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between gap-4">
            <Link href="/" className="flex items-baseline gap-2">
              <span className="font-display text-2xl tracking-tight">CA4 Oyez</span>
              <span className="text-xs uppercase tracking-widest text-white/60 hidden sm:inline">
                Fourth Circuit Oral Arguments
              </span>
            </Link>
            <nav className="flex gap-5 text-sm uppercase tracking-wide">
              <Link href="/" className="hover:text-gold transition-colors">
                Cases
              </Link>
              <Link href="/about" className="hover:text-gold transition-colors">
                About
              </Link>
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="bg-navy text-white/70 text-xs mt-16">
          <div className="mx-auto max-w-5xl px-4 py-6 space-y-1">
            <p>
              Unofficial, non-commercial project. Not affiliated with the U.S. Courts,
              the Fourth Circuit, or Oyez.org / the Legal Information Institute.
            </p>
            <p>
              Audio and opinions are sourced from{" "}
              <a
                href="https://www.ca4.uscourts.gov"
                className="underline hover:text-gold"
                target="_blank"
                rel="noreferrer"
              >
                ca4.uscourts.gov
              </a>
              , the Fourth Circuit&apos;s official public site.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
