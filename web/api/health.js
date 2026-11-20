// Fungsi Vercel: status server LyRecall (siap / sedang memuat / gagal).
module.exports = async (req, res) => {
  const base = (process.env.API_URL || "").replace(/\/$/, "");
  if (!base) return res.status(500).json({ ready: false, error: "API_URL belum diatur di Vercel." });
  try {
    const r = await fetch(`${base}/health`, {
      headers: { "ngrok-skip-browser-warning": "1" },
      signal: AbortSignal.timeout(15000),
    });
    const body = await r.json().catch(() => ({}));
    res.setHeader("Cache-Control", "no-store");
    return res.status(200).json({ ready: !!body.ready, stage: body.stage || null, error: body.error || null });
  } catch (e) {
    return res.status(502).json({ ready: false, error: "Server pencarian tidak dapat dihubungi." });
  }
};
