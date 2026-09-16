import fs from "node:fs";
import path from "node:path";

export type OpinionSection = {
  author: string;
  kind: "majority" | "concurrence" | "dissent" | "concurrence/dissent";
  text: string;
};

export type Opinion = {
  opinion_number: string;
  published: boolean;
  author: string | null;
  decision: string | null;
  case_type: string | null;
  appeal_from: string | null;
  originating_judge: string | null;
  pdf_url: string | null;
  date_issued: string | null;
  pdf_file: string | null;
  sections: OpinionSection[] | null;
};

export type Case = {
  docket_number: string;
  case_name: string;
  argument_date: string;
  panel: string[];
  counsel: string[];
  audio_url: string;
  audio_file: string | null;
  opinion: Opinion | null;
  facts_of_the_case: string | null;
  question_presented: string | null;
  conclusion_summary: string | null;
};

// Reads data/cases.json (produced by scraper/build_dataset.py). Falls back
// to the small sample dataset when the real one hasn't been generated yet,
// so `npm run dev` works out of the box.
export function getAllCases(): Case[] {
  const dataDir = path.join(process.cwd(), "..", "data");
  const realPath = path.join(dataDir, "cases.json");
  const samplePath = path.join(dataDir, "cases.sample.json");

  const file = fs.existsSync(realPath) ? realPath : samplePath;
  const raw = fs.readFileSync(file, "utf-8");
  const cases = JSON.parse(raw) as Case[];

  return [...cases].sort((a, b) => (a.argument_date < b.argument_date ? 1 : -1));
}

export function getCase(docketNumber: string): Case | undefined {
  return getAllCases().find((c) => c.docket_number === docketNumber);
}

export function isUsingSampleData(): boolean {
  const dataDir = path.join(process.cwd(), "..", "data");
  return !fs.existsSync(path.join(dataDir, "cases.json"));
}
