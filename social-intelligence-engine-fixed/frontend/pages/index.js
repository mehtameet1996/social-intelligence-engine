import { useState } from "react";

export default function Home() {
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const [company, setCompany] = useState("openai.com");
  const [subs, setSubs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const discover = async () => {
    setLoading(true);
    setErr("");
    setSubs([]);

    try {
      const res = await fetch(`${API}/api/v1/discovery/subreddits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_domain: company }),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt);
      }

      const data = await res.json();
      setSubs(data);
    } catch (e) {
      setErr(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, fontFamily: "Arial" }}>
      <h2>Social Intelligence Engine</h2>
      <h3>Community Discovery (Reddit)</h3>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <input
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          placeholder="openai.com"
          style={{ padding: 10, width: 260 }}
        />
        <button onClick={discover} disabled={loading} style={{ padding: "10px 16px" }}>
          {loading ? "Discovering..." : "Discover"}
        </button>
      </div>

      {err && (
        <div style={{ background: "#ffe5e5", padding: 12, borderRadius: 8, marginBottom: 12 }}>
          <b>Error:</b> {err}
        </div>
      )}

      {subs.length === 0 && !loading && !err && (
        <div style={{ color: "#666" }}>No data yet. Enter a company domain and click Discover.</div>
      )}

      <div style={{ display: "grid", gap: 12 }}>
        {subs.map((s, idx) => (
          <div
            key={s.name}
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: 14,
              background: "white",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  r/{s.name} — {s.subscribers} subs — score {(s.business_value_score * 100).toFixed(1)}%
                </div>
                <div style={{ marginTop: 6, color: "#555" }}>{s.description}</div>
              </div>

              <div style={{ textAlign: "right", minWidth: 160 }}>
                <div><b>Relevance:</b> {(s.relevance_score * 100).toFixed(0)}%</div>
                <div><b>Engagement:</b> {(s.engagement_score * 100).toFixed(0)}%</div>
                <div><b>Mentions:</b> {s.mention_count ?? 0}</div>
                <div style={{ color: "#888" }}>Rank #{idx + 1}</div>
              </div>
            </div>

            {s.sample_posts && s.sample_posts.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <b>Top posts (demo):</b>
                <ul style={{ marginTop: 6 }}>
                  {s.sample_posts.map((p) => (
                    <li key={p.id} style={{ marginBottom: 6 }}>
                      <a href={p.permalink} target="_blank" rel="noreferrer">
                        {p.title}
                      </a>{" "}
                      <span style={{ color: "#777" }}>
                        ({p.num_comments} comments, {p.score} score)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
