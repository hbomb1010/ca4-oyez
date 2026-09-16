export default function About() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10 space-y-4 leading-relaxed">
      <h1 className="font-display text-3xl mb-4">About this project</h1>
      <p>
        This is an independent, non-commercial project that presents oral
        arguments and opinions from the U.S. Court of Appeals for the Fourth
        Circuit in a case-page format, starting with cases argued in 2026.
      </p>
      <p>
        It is not affiliated with the federal judiciary, the Fourth Circuit,
        Oyez.org, or Cornell&apos;s Legal Information Institute. All primary
        source material (audio, opinions) is pulled from the Fourth
        Circuit&apos;s official public site,{" "}
        <a
          href="https://www.ca4.uscourts.gov"
          className="underline"
          target="_blank"
          rel="noreferrer"
        >
          ca4.uscourts.gov
        </a>
        .
      </p>
      <p>
        Case summaries (&quot;Facts of the Case,&quot; &quot;Question,&quot;
        etc.), where present, are written by the site&apos;s maintainer and
        are not official court text.
      </p>
    </div>
  );
}
