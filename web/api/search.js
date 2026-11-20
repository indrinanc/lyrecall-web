// Fungsi Vercel: meneruskan pencarian ke server LyRecall (alamatnya di variabel lingkungan API_URL).
module.exports = async (req, res) => {
  const base = (process.env.API_URL || "").replace(/\/$/, "");
  if (!base) return res.status(500).json({ error: "API_URL belum diatur di Vercel." });

  const q = String((req.query && req.query.q) || "").trim().slice(0, 500);
  if (q.length < 2) return res.status(400).json({ error: "Kueri terlalu pendek." });
  const mode = req.query.mode === "lexical" ? "lexical" : "hybrid";

  try {
    const r = await fetch(`${base}/search?` + new URLSearchParams({ q, top: "10", mode }), {
      headers: { "ngrok-skip-browser-warning": "1" },
      signal: AbortSignal.timeout(55000),
    });
    const body = await r.json().catch(() => ({}));
    if (!r.ok) {
      return res.status(r.status === 503 ? 503 : 502).json({ error: body.detail || "Server pencarian mengembalikan error." });
    }
    res.setHeader("Cache-Control", "no-store");
    return res.status(200).json(body);
  } catch (e) {
    return res.status(502).json({ error: "Server pencarian tidak dapat dihubungi." });
  }
};
