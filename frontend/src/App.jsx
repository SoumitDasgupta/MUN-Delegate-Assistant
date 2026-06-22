import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

const UN_COMMITTEES = [
  "UNSC - Security Council",
  "UNGA - General Assembly",
  "UNHRC - Human Rights Council",
  "WHO - World Health Organization",
  "UNEP - Environment Programme",
  "UNESCO - Education & Culture",
  "UNICEF - Children's Fund",
  "IMF - International Monetary Fund",
  "ICJ - International Court of Justice",
  "Other"
];

const INDIAN_COMMITTEES = [
  "Lok Sabha",
  "Rajya Sabha",
  "Maharashtra Vidhan Sabha",
  "Delhi Legislative Assembly",
  "West Bengal Legislative Assembly",
  "Tamil Nadu Legislative Assembly",
  "CBI - Central Bureau of Investigation",
  "ED - Enforcement Directorate",
  "NITI Aayog",
  "Cabinet Committee on Security",
  "Other"
];

function App() {
  const [munType, setMunType] = useState(null);
  const [committee, setCommittee] = useState("");
  const [topic, setTopic] = useState("");
  const [country, setCountry] = useState("");
  const [politician, setPolitician] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysing, setAnalysing] = useState(false);
  const [result, setResult] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [sources, setSources] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("brief");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleReset = () => {
    setMunType(null);
    setCommittee("");
    setTopic("");
    setCountry("");
    setPolitician("");
    setResult(null);
    setAnalysis(null);
    setSources(null);
    setError(null);
    setActiveTab("brief");
    setChatMessages([]);
    setChatInput("");
  };

  const handleSubmit = async () => {
    if (!committee || !topic) { setError("Please fill in all fields."); return; }
    if (munType === "un" && !country) { setError("Please enter the country."); return; }
    if (munType === "indian" && !politician) { setError("Please enter the politician."); return; }

    setLoading(true);
    setError(null);
    setResult(null);
    setAnalysis(null);
    setSources(null);
    setChatMessages([]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/generate", {
        mun_type: munType, committee, topic,
        country: munType === "un" ? country : null,
        politician: munType === "indian" ? politician : null,
      });
      setResult(response.data.brief);
      setSources(response.data.research_sources);
      setActiveTab("brief");
    } catch (err) {
      setError("Something went wrong. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyse = async () => {
    setAnalysing(true);
    setError(null);
    try {
      const response = await axios.post("http://127.0.0.1:8000/analyse", {
        mun_type: munType, committee, topic,
        country: munType === "un" ? country : null,
        politician: munType === "indian" ? politician : null,
      });
      setAnalysis(response.data.analysis);
      setActiveTab("analysis");

      // Seed the chat with the analysis as context
      setChatMessages([
        {
          role: "assistant",
          content: "I've completed the agenda analysis above. Ask me anything — I can go deeper on any problem, help refine your arguments, suggest counterpoints, or help you prepare for tough questions in the chamber."
        }
      ]);
    } catch (err) {
      setError("Analysis failed. Make sure the backend is running.");
    } finally {
      setAnalysing(false);
    }
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: "user", content: chatInput };
    const updatedMessages = [...chatMessages, userMessage];
    setChatMessages(updatedMessages);
    setChatInput("");
    setChatLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/chat", {
        mun_type: munType, committee, topic,
        country: munType === "un" ? country : null,
        politician: munType === "indian" ? politician : null,
        messages: updatedMessages
      });

      setChatMessages([...updatedMessages, {
        role: "assistant",
        content: response.data.reply
      }]);
    } catch (err) {
      setChatMessages([...updatedMessages, {
        role: "assistant",
        content: "Something went wrong. Please try again."
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleChat();
    }
  };

  return (
    <div className="app">
      <div className="header">
        <h1>🌐 MUN Delegate Assistant</h1>
        <p>AI-powered preparation for UN and Indian parliamentary committees</p>
      </div>

      {/* STEP 1 */}
      {!munType && (
        <div className="type-selector">
          <h2>What kind of committee are you preparing for?</h2>
          <div className="type-cards">
            <div className="type-card" onClick={() => setMunType("un")}>
              <div className="type-icon">🇺🇳</div>
              <h3>UN Committee</h3>
              <p>UNSC, UNHRC, WHO, UNGA and other international bodies</p>
            </div>
            <div className="type-card" onClick={() => setMunType("indian")}>
              <div className="type-icon">🇮🇳</div>
              <h3>Indian Committee</h3>
              <p>Lok Sabha, Rajya Sabha, State Legislatures, CBI, ED and more</p>
            </div>
          </div>
        </div>
      )}

      {/* STEP 2 */}
      {munType && !result && (
        <div className="form-card">
          <div className="form-header">
            <button className="back-btn" onClick={handleReset}>← Back</button>
            <h2>{munType === "un" ? "🇺🇳 UN Committee" : "🇮🇳 Indian Committee"}</h2>
          </div>

          <div className="form-group">
            <label>Committee</label>
            <select value={committee} onChange={(e) => setCommittee(e.target.value)}>
              <option value="">Select a committee...</option>
              {(munType === "un" ? UN_COMMITTEES : INDIAN_COMMITTEES).map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {munType === "un" && (
            <div className="form-group">
              <label>Country you are representing</label>
              <input
                type="text"
                placeholder="e.g. India, USA, France"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              />
            </div>
          )}

          {munType === "indian" && (
            <div className="form-group">
              <label>Politician you are representing</label>
              <input
                type="text"
                placeholder="e.g. Narendra Modi, Rahul Gandhi, Mamata Banerjee"
                value={politician}
                onChange={(e) => setPolitician(e.target.value)}
              />
            </div>
          )}

          <div className="form-group">
            <label>Agenda / Topic</label>
            <input
              type="text"
              placeholder={
                munType === "un"
                  ? "e.g. Cybersecurity, Climate Change, Nuclear Proliferation"
                  : "e.g. CAA, Article 370, GST, Uniform Civil Code"
              }
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          <button className="generate-btn" onClick={handleSubmit} disabled={loading}>
            {loading ? "Researching & Generating..." : "Generate My Brief"}
          </button>

          {error && <p className="error">{error}</p>}

          {loading && (
            <div className="loading-info">
              <div className="spinner"></div>
              <p>Scraping live news, Wikipedia, World Bank data...</p>
              <p>Generating your complete delegate brief with AI...</p>
            </div>
          )}
        </div>
      )}

      {/* RESULTS */}
      {result && (
        <div className="result-section">
          <div className="result-header">
            <h2>📋 {munType === "un" ? country : politician} — {topic}</h2>
            <button className="back-btn" onClick={handleReset}>Start Over</button>
          </div>

          {sources && (
            <div className="sources-card">
              <h3>📡 Live Sources Used</h3>
              <div className="sources-grid">
                <div className="source-item">
                  <span>📰 News Articles</span>
                  <strong>{sources.news_count}</strong>
                </div>
                <div className="source-item">
                  <span>🌍 ReliefWeb</span>
                  <strong>{sources.reliefweb_count}</strong>
                </div>
                <div className="source-item">
                  <span>📖 Wikipedia</span>
                  <strong>{sources.wikipedia_found ? "✅" : "❌"}</strong>
                </div>
                <div className="source-item">
                  <span>🏦 World Bank</span>
                  <strong>{sources.world_bank_found ? "✅" : "❌"}</strong>
                </div>
                <div className="source-item">
                  <span>⚖️ Indian Laws</span>
                  <strong>{sources.indian_laws_found}</strong>
                </div>
              </div>
            </div>
          )}

          {/* TABS */}
          <div className="tabs">
            <button
              className={`tab-btn ${activeTab === "brief" ? "active" : ""}`}
              onClick={() => setActiveTab("brief")}
            >
              📋 Delegate Brief
            </button>
            <button
              className={`tab-btn ${activeTab === "analysis" ? "active" : ""}`}
              onClick={() => {
                if (!analysis) handleAnalyse();
                else setActiveTab("analysis");
              }}
              disabled={analysing}
            >
              {analysing ? "⏳ Analysing..." : "🔍 Agenda Analysis"}
            </button>
            {analysis && (
              <button
                className={`tab-btn ${activeTab === "chat" ? "active" : ""}`}
                onClick={() => setActiveTab("chat")}
              >
                💬 Research Chat
              </button>
            )}
          </div>

          {/* BRIEF TAB */}
          {activeTab === "brief" && (
            <div className="result-card">
              <pre>{result}</pre>
            </div>
          )}

          {/* ANALYSIS TAB */}
          {activeTab === "analysis" && analysis && (
            <div className="result-card">
              <pre>{analysis}</pre>
              <button
                className="chat-prompt-btn"
                onClick={() => setActiveTab("chat")}
              >
                💬 Discuss this analysis →
              </button>
            </div>
          )}

          {analysing && (
            <div className="loading-info">
              <div className="spinner"></div>
              <p>Analysing agenda problems with real precedents...</p>
            </div>
          )}

          {/* CHAT TAB */}
          {activeTab === "chat" && (
            <div className="chat-section">
              <div className="chat-messages">
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`chat-bubble ${msg.role}`}>
                    <div className="chat-label">
                      {msg.role === "user" ? "You" : "🌐 MUN Assistant"}
                    </div>
                    <div className="chat-text">{msg.content}</div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="chat-bubble assistant">
                    <div className="chat-label">🌐 MUN Assistant</div>
                    <div className="chat-text typing">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              <div className="chat-input-row">
                <textarea
                  className="chat-input"
                  placeholder="Ask anything — refine an argument, get a precedent, challenge a point, improve your speech..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  rows={2}
                />
                <button
                  className="chat-send-btn"
                  onClick={handleChat}
                  disabled={chatLoading || !chatInput.trim()}
                >
                  ➤
                </button>
              </div>
              <p className="chat-hint">Press Enter to send · Shift+Enter for new line</p>
            </div>
          )}

          {error && <p className="error">{error}</p>}
        </div>
      )}
    </div>
  );
}

export default App;