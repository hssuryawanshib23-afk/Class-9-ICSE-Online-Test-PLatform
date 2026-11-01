import "server-only";
import { readFile } from "node:fs/promises";
import path from "node:path";
import fontkit from "@pdf-lib/fontkit";
import { PDFDocument, rgb, type PDFFont, type PDFPage } from "pdf-lib";
import { breakdownOf, gradeFor, insightsOf, type ReviewItem } from "@/lib/results";

const A4: [number, number] = [595.28, 841.89];
const M = 40;
const BRAND = rgb(0.357, 0.239, 0.961);
const INK = rgb(0.08, 0.07, 0.17);
const MUTED = rgb(0.42, 0.42, 0.52);
const GOOD = rgb(0.086, 0.639, 0.29);
const BAD = rgb(0.863, 0.149, 0.149);

async function font(name: string) {
  // Bundled with the app (see outputFileTracingIncludes in next.config.ts).
  return readFile(path.join(process.cwd(), "assets", "fonts", name));
}

export type ReportInput = {
  title: string;
  student: string;
  score: number;
  total: number;
  seconds: number | null;
  items: ReviewItem[];
  date: Date;
};

export async function buildReport(input: ReportInput): Promise<Uint8Array> {
  const pdf = await PDFDocument.create();
  pdf.registerFontkit(fontkit);
  const regular = await pdf.embedFont(await font("DejaVuSans.ttf"), { subset: true });
  const bold = await pdf.embedFont(await font("DejaVuSans-Bold.ttf"), { subset: true });

  let page: PDFPage = pdf.addPage(A4);
  let y = A4[1] - M;

  const ensure = (h: number) => {
    if (y - h < M) {
      page = pdf.addPage(A4);
      y = A4[1] - M;
    }
  };

  // Breaks on words; long unbroken strings are split by characters so nothing runs off the page.
  const wrap = (text: string, f: PDFFont, size: number, width: number) => {
    const lines: string[] = [];
    for (const para of text.replace(/\r/g, "").split("\n")) {
      let line = "";
      for (const word of para.split(/\s+/)) {
        let w = word;
        while (f.widthOfTextAtSize(w, size) > width) {
          let cut = w.length - 1;
          while (cut > 1 && f.widthOfTextAtSize(w.slice(0, cut), size) > width) cut--;
          if (line) { lines.push(line); line = ""; }
          lines.push(w.slice(0, cut));
          w = w.slice(cut);
        }
        const next = line ? `${line} ${w}` : w;
        if (f.widthOfTextAtSize(next, size) <= width) line = next;
        else { lines.push(line); line = w; }
      }
      lines.push(line);
    }
    return lines;
  };

  const text = (t: string, opts: { f?: PDFFont; size?: number; color?: ReturnType<typeof rgb>; x?: number; gap?: number } = {}) => {
    const f = opts.f ?? regular;
    const size = opts.size ?? 10.5;
    const x = opts.x ?? M;
    for (const line of wrap(t, f, size, A4[0] - M - x)) {
      ensure(size * 1.5);
      y -= size * 1.35;
      page.drawText(line, { x, y, size, font: f, color: opts.color ?? INK });
    }
    y -= opts.gap ?? 0;
  };

  const heading = (t: string) => {
    ensure(40);
    y -= 12;
    text(t, { f: bold, size: 14, color: BRAND, gap: 4 });
  };

  const table = (rows: string[][], widths: number[]) => {
    rows.forEach((row, ri) => {
      ensure(24);
      const h = 22;
      if (ri === 0) page.drawRectangle({ x: M, y: y - h, width: widths.reduce((a, b) => a + b, 0), height: h, color: BRAND });
      else if (ri % 2 === 0) page.drawRectangle({ x: M, y: y - h, width: widths.reduce((a, b) => a + b, 0), height: h, color: rgb(0.96, 0.95, 1) });
      let x = M;
      row.forEach((cell, ci) => {
        page.drawText(cell, { x: x + 8, y: y - 15, size: 10.5, font: ri === 0 ? bold : regular, color: ri === 0 ? rgb(1, 1, 1) : INK });
        x += widths[ci];
      });
      y -= h;
    });
    y -= 8;
  };

  const pct = input.total ? Math.round((input.score / input.total) * 1000) / 10 : 0;
  const b = breakdownOf(input.items);
  const { strengths, focus } = insightsOf(b);

  // Title block
  page.drawRectangle({ x: 0, y: A4[1] - 92, width: A4[0], height: 92, color: BRAND });
  page.drawText("Test Analytics & Results", { x: M, y: A4[1] - 48, size: 22, font: bold, color: rgb(1, 1, 1) });
  page.drawText(`${input.title}  ·  ${input.student}  ·  ${input.date.toISOString().slice(0, 10)}`, {
    x: M, y: A4[1] - 72, size: 10, font: regular, color: rgb(0.9, 0.88, 1),
  });
  y = A4[1] - 92 - 8;

  heading("Performance Overview");
  const time = input.seconds === null ? "N/A" : `${Math.floor(input.seconds / 60)}m ${input.seconds % 60}s`;
  table(
    [
      ["Metric", "Value"],
      ["Score", `${input.score}/${input.total}`],
      ["Percentage", `${pct}%`],
      ["Grade", gradeFor(pct)],
      ["Time taken", time],
    ],
    [240, 240],
  );

  heading("Difficulty-wise Analysis");
  const rows = [["Difficulty", "Correct", "Total", "Accuracy"]];
  for (const d of ["easy", "medium", "hard"] as const) {
    if (b[d].total) rows.push([d[0].toUpperCase() + d.slice(1), String(b[d].correct), String(b[d].total), `${Math.round((b[d].correct / b[d].total) * 1000) / 10}%`]);
  }
  table(rows, [150, 110, 110, 110]);

  heading("Insights & Recommendations");
  if (!strengths.length && !focus.length) text("Keep practising across all difficulty levels to build a clearer picture.", { gap: 4 });
  for (const s of strengths) text(`+  ${s}`, { color: GOOD, gap: 2 });
  for (const f of focus) text(`!  ${f}`, { color: BAD, gap: 2 });

  page = pdf.addPage(A4);
  y = A4[1] - M;
  heading("Question-by-Question Review");
  for (const it of input.items) {
    ensure(60);
    y -= 6;
    text(`Q${it.n}. ${it.text}   ${it.ok ? "[Correct]" : it.answered ? "[Incorrect]" : "[Not answered]"}`, {
      f: bold, size: 10.5, color: it.ok ? GOOD : BAD, gap: 2,
    });
    for (const o of it.options) {
      const tag = `${o.picked ? "  ← your answer" : ""}${o.correct ? "  ✓ correct" : ""}`;
      text(`${o.letter}. ${o.text}${tag}`, { x: M + 14, size: 10, color: o.correct ? GOOD : o.picked ? BAD : INK });
    }
    y -= 4;
  }

  const pages = pdf.getPages();
  pages.forEach((p, i) =>
    p.drawText(`Page ${i + 1} of ${pages.length}`, { x: A4[0] - M - 60, y: 18, size: 8, font: regular, color: MUTED }),
  );
  return pdf.save();
}
