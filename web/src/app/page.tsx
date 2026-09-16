import Link from "next/link";
import { getAllCases, isUsingSampleData } from "@/lib/cases";

function formatDate(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function Home() {
  const cases = getAllCases();
  const usingSample = isUsingSampleData();

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      {usingSample && (
        <div className="mb-8 rounded border border-gold bg-gold/10 px-4 py-3 text-sm">
          Showing sample placeholder data. Run{" "}
          <code className="font-mono text-xs">scraper/build_dataset.py</code> to
          populate <code className="font-mono text-xs">data/cases.json</code> with
          real Fourth Circuit cases.
        </div>
      )}

      <h1 className="font-display text-3xl mb-1">Fourth Circuit Oral Arguments</h1>
      <p className="text-muted mb-8">
        Cases argued before the U.S. Court of Appeals for the Fourth Circuit,
        2026&ndash;present.
      </p>

      <ul className="divide-y divide-border border-t border-b border-border">
        {cases.map((c) => (
          <li key={c.docket_number}>
            <Link
              href={`/cases/${c.docket_number}`}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-4 group"
            >
              <div>
                <div className="font-display text-lg group-hover:text-red transition-colors">
                  {c.case_name}
                </div>
                <div className="text-sm text-muted">
                  No. {c.docket_number} &middot; Argued {formatDate(c.argument_date)}
                </div>
              </div>
              <div className="text-sm shrink-0">
                {c.opinion ? (
                  <span className="inline-block px-2 py-1 rounded bg-navy/5 text-navy border border-navy/20">
                    Decided &middot; {c.opinion.decision}
                  </span>
                ) : (
                  <span className="inline-block px-2 py-1 rounded bg-gold/10 text-gold border border-gold/40">
                    Decision pending
                  </span>
                )}
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
