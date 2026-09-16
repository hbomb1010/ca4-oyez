import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllCases, getCase } from "@/lib/cases";

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso + "T00:00:00").toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

const KIND_LABEL: Record<string, string> = {
  majority: "Opinion of the Court",
  concurrence: "Concurring Opinion",
  dissent: "Dissenting Opinion",
  "concurrence/dissent": "Opinion Concurring in Part and Dissenting in Part",
};

export function generateStaticParams() {
  return getAllCases().map((c) => ({ docket: c.docket_number }));
}

export default async function CasePage({
  params,
}: {
  params: Promise<{ docket: string }>;
}) {
  const { docket } = await params;
  const c = getCase(docket);
  if (!c) notFound();

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <Link href="/" className="text-sm text-muted hover:text-red">
        &larr; All cases
      </Link>

      <h1 className="font-display text-4xl mt-3 mb-2">{c.case_name}</h1>
      <p className="text-muted mb-8">
        No. {c.docket_number} &middot; U.S. Court of Appeals for the Fourth Circuit
      </p>

      <div className="grid md:grid-cols-[1fr_280px] gap-10">
        <div className="space-y-10 min-w-0">
          <section>
            <h2 className="font-display text-xl border-b border-border pb-2 mb-4">
              Media
            </h2>
            <div className="bg-card border border-border rounded p-4">
              <p className="text-xs uppercase tracking-widest text-muted mb-2">
                Oral Argument &mdash; {formatDate(c.argument_date)}
              </p>
              <audio controls className="w-full" src={c.audio_url} />
              <p className="mt-2 text-xs text-muted">
                Source:{" "}
                <a
                  href={c.audio_url}
                  className="underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  ca4.uscourts.gov
                </a>
              </p>
            </div>
          </section>

          {(c.facts_of_the_case || c.question_presented || c.conclusion_summary) && (
            <section className="space-y-6">
              {c.facts_of_the_case && (
                <div>
                  <h2 className="font-display text-xl mb-2">Facts of the case</h2>
                  <p className="leading-relaxed">{c.facts_of_the_case}</p>
                </div>
              )}
              {c.question_presented && (
                <div>
                  <h2 className="font-display text-xl mb-2">Question</h2>
                  <p className="leading-relaxed">{c.question_presented}</p>
                </div>
              )}
            </section>
          )}

          {c.opinion ? (
            <section>
              <h2 className="font-display text-xl border-b border-border pb-2 mb-4">
                Opinions
              </h2>

              <div className="mb-4 text-sm text-muted">
                {c.opinion.published ? "Published" : "Unpublished"} opinion issued{" "}
                {formatDate(c.opinion.date_issued)} &middot; {c.opinion.decision}
                {c.opinion.pdf_url && (
                  <>
                    {" "}
                    &middot;{" "}
                    <a
                      href={c.opinion.pdf_url}
                      className="underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      view PDF
                    </a>
                  </>
                )}
              </div>

              {c.conclusion_summary && (
                <p className="leading-relaxed mb-6">{c.conclusion_summary}</p>
              )}

              {c.opinion.sections && c.opinion.sections.length > 0 ? (
                <div className="space-y-8">
                  {c.opinion.sections.map((s, i) => (
                    <div key={i} className="border-l-2 border-gold pl-4">
                      <h3 className="font-display text-lg">
                        {KIND_LABEL[s.kind] ?? s.kind} &mdash;{" "}
                        <span className="text-muted">{s.author}</span>
                      </h3>
                      <p className="mt-2 whitespace-pre-line leading-relaxed text-sm">
                        {s.text}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted italic">
                  Full opinion text not yet parsed &mdash; see the PDF link above.
                </p>
              )}
            </section>
          ) : (
            <section>
              <h2 className="font-display text-xl border-b border-border pb-2 mb-4">
                Opinion
              </h2>
              <p className="text-muted italic">Decision pending.</p>
            </section>
          )}
        </div>

        <aside className="space-y-6 text-sm">
          <div>
            <h3 className="uppercase tracking-widest text-xs text-muted mb-1">
              Panel
            </h3>
            <ul>
              {c.panel.map((judge) => (
                <li key={judge}>{judge}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="uppercase tracking-widest text-xs text-muted mb-1">
              Counsel
            </h3>
            <ul>
              {c.counsel.map((name) => (
                <li key={name}>{name}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="uppercase tracking-widest text-xs text-muted mb-1">
              Argued
            </h3>
            <p>{formatDate(c.argument_date)}</p>
          </div>

          {c.opinion && (
            <>
              <div>
                <h3 className="uppercase tracking-widest text-xs text-muted mb-1">
                  Decided
                </h3>
                <p>{formatDate(c.opinion.date_issued)}</p>
              </div>
              {c.opinion.appeal_from && (
                <div>
                  <h3 className="uppercase tracking-widest text-xs text-muted mb-1">
                    Appeal From
                  </h3>
                  <p>{c.opinion.appeal_from}</p>
                </div>
              )}
              {c.opinion.originating_judge && (
                <div>
                  <h3 className="uppercase tracking-widest text-xs text-muted mb-1">
                    Originating Judge
                  </h3>
                  <p>{c.opinion.originating_judge}</p>
                </div>
              )}
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
