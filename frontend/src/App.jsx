import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [country, setCountry] = useState("");
  const [committee, setCommittee] = useState("");
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState(null);

  const handleSubmit = async () => {
    if (!country || !committee || !topic) {
      setError("Please fill in all three fields.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setSources(null);

    try {
      const response = await axios.post("http://127.0.0.1:8000/generate", {
        country,
        committee,
        topic,
      });
      setResult(response.data.brief);
      setSources(response.data.research_sources);
    } catch (err) {
      setError("Something went wrong. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="header">
        <h1>🌐 MUN Delegate Assistant</h1>
        <p>Real-time AI-powered research for Model UN delegates</p>
      </div>

      <div className="form-card">
        <div className="form-group">
          <label>Country you are representing</label>
          <input
            type="text"
            placeholder="e.g. India"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Committee</label>
          <input
            type="text"
            placeholder="e.g. UNSC, UNHRC, WHO"
            value={committee}
            onChange={(e) => setCommittee(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Topic / Agenda</label>
          <input
            type="text"
            placeholder="e.g. Cybersecurity, Climate Change"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <button
          className="generate-btn"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Researching & Generating..." : "Generate My Brief"}
        </button>

        {error && <p className="error">{error}</p>}
      </div>

      {sources && (
        <div className="sources-card">
          <h3>📡 Live Sources Used</h3>
          <div className="sources-grid">
            <div className="source-item">
              <span>🇺🇳 UN News Articles</span>
              <strong>{sources.un_news_count}</strong>
            </div>
            <div className="source-item">
              <span>🌍 ReliefWeb Reports</span>
              <strong>{sources.reliefweb_count}</strong>
            </div>
            <div className="source-item">
              <span>📖 Wikipedia</span>
              <strong>{sources.wikipedia_found ? "✅" : "❌"}</strong>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="result-card">
          <h3>📋 Your Delegate Brief</h3>
          <pre>{result}</pre>
        </div>
      )}

      {loading && (
        <div className="loading-card">
          <div className="spinner"></div>
          <p>Scraping UN News, ReliefWeb & Wikipedia in real-time...</p>
          <p>Generating your brief with Gemini AI...</p>
        </div>
      )}
    </div>
  );
}

export default App;