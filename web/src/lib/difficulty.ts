/** Pure helpers shared by the server (generation) and the browser (live availability hints). */

/** Python's round() rounds halves to even; match it so counts equal the Streamlit app's. */
function roundHalfEven(x: number) {
  const f = Math.floor(x);
  const diff = x - f;
  if (diff < 0.5) return f;
  if (diff > 0.5) return f + 1;
  return f % 2 === 0 ? f : f + 1;
}

export function splitCounts(total: number, easyPct: number, mediumPct: number) {
  const easy = roundHalfEven((total * easyPct) / 100);
  const medium = roundHalfEven((total * mediumPct) / 100);
  return { easy, medium, hard: total - easy - medium };
}
