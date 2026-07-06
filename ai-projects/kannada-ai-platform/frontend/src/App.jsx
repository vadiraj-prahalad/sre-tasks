import { useState } from "react";
import { askQuestion } from "./services/api";
import "./App.css";

const suggestedQuestions = [
  { label: "🎭 ಯಕ್ಷಗಾನ", question: "ಯಕ್ಷಗಾನ ಎಂದರೇನು?" },
  { label: "🎵 ಪುರಂದರ ದಾಸರು", question: "ಪುರಂದರ ದಾಸರು ಯಾರು?" },
  { label: "📖 ಕುವೆಂಪು", question: "ಕುವೆಂಪು ಯಾರು?" },
  { label: "🕉 ಮಧ್ವಾಚಾರ್ಯರು", question: "ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?" },
];

function splitAnswerAndSources(rawAnswer) {
  if (!rawAnswer || !rawAnswer.includes("\n\nಮೂಲ:")) {
    return { answerText: rawAnswer || "", sources: [] };
  }

  const parts = rawAnswer.split("\n\nಮೂಲ:");
  const answerText = parts[0];

  const sources = parts
    .slice(1)
    .join("\nಮೂಲ:")
    .split("\nಮೂಲ:")
    .map((source) => source.trim())
    .filter(Boolean);

  return { answerText, sources };
}

function App() {
  const [question, setQuestion] = useState("");
  const [lastQuestion, setLastQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [trace, setTrace] = useState([]);
  const [confidence, setConfidence] = useState(null);
  const [showTrace, setShowTrace] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAsk(selectedQuestion = question) {
    if (!selectedQuestion.trim()) {
      setError("ದಯವಿಟ್ಟು ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setTrace([]);
    setConfidence(null);
    setShowTrace(false);
    setLastQuestion(selectedQuestion);
    setQuestion(selectedQuestion);

    try {
      const data = await askQuestion(selectedQuestion, true);
      setAnswer(data.answer);
      setTrace(data.trace || []);
      setConfidence(data.confidence || null);
    } catch {
      setError("Backend ಸಂಪರ್ಕದಲ್ಲಿ ಸಮಸ್ಯೆ ಇದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.");
    } finally {
      setLoading(false);
    }
  }

  const { answerText, sources } = splitAnswerAndSources(answer);

  return (
    <main className="app">
      <section className="shell">
        <header className="hero">
          <div className="badge">Kannada AI Beta</div>
          <h1>ಕನ್ನಡ ಜ್ಞಾನ ಸಹಾಯಕ</h1>
          <p>ಕನ್ನಡ ಸಂಸ್ಕೃತಿ, ಸಾಹಿತ್ಯ, ಇತಿಹಾಸ ಮತ್ತು ಜ್ಞಾನಕ್ಕಾಗಿ ಸರಳ AI ಸಹಾಯಕ</p>
        </header>

        <section className="ask-card">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="ಉದಾ: ಯಕ್ಷಗಾನ ಎಂದರೇನು?"
            rows="3"
          />

          <div className="ask-actions">
            <button className="primary-button" onClick={() => handleAsk()} disabled={loading}>
              {loading ? "ಉತ್ತರ ಹುಡುಕುತ್ತಿದೆ..." : "ಪ್ರಶ್ನಿಸಿ"}
            </button>
          </div>
        </section>

        <section className="suggestions">
          {suggestedQuestions.map((item) => (
            <button
              key={item.question}
              onClick={() => handleAsk(item.question)}
              disabled={loading}
            >
              {item.label}
            </button>
          ))}
        </section>

        {error && <div className="error">{error}</div>}

        {(lastQuestion || loading || answer) && (
          <section className="chat-panel">
            {lastQuestion && (
              <div className="question-card">
                <span>ನೀವು ಕೇಳಿದ್ದು</span>
                <p>{lastQuestion}</p>
              </div>
            )}

            {loading && (
              <div className="answer-card">
                <div className="answer-header">
                  <span className="bot-icon">🤖</span>
                  <div>
                    <h2>ಉತ್ತರ ಸಿದ್ಧಪಡಿಸುತ್ತಿದೆ</h2>
                    <p>ಜ್ಞಾನ ಮೂಲಗಳು ಮತ್ತು RAG pipeline ಪರಿಶೀಲಿಸುತ್ತಿದೆ...</p>
                  </div>
                </div>
              </div>
            )}

            {answer && !loading && (
              <div className="answer-card">
                <div className="answer-header">
                  <span className="bot-icon">🤖</span>
                  <div>
                    <h2>ವಿಶ್ವಾಸಾರ್ಹ ಉತ್ತರ</h2>
                    {confidence && (
                      <p className="confidence-line">
                        {confidence.score}% · {confidence.kannada_label}
                      </p>
                    )}
                  </div>
                </div>

                <p className="answer-text">{answerText}</p>

                {sources.length > 0 && (
                  <div className="sources-row">
                    <span className="section-label">ಮೂಲಗಳು</span>
                    <div className="source-list">
                      {sources.map((source) => (
                        <span className="source-chip" key={source}>
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {confidence?.reasons?.length > 0 && (
                  <div className="confidence-box">
                    {confidence.reasons.map((reason) => (
                      <span key={reason}>✓ {reason}</span>
                    ))}
                  </div>
                )}

                {trace.length > 0 && (
                  <div className="trace-section">
                    <button
                      className="trace-toggle"
                      onClick={() => setShowTrace(!showTrace)}
                    >
                      {showTrace ? "Developer Trace ಮುಚ್ಚಿ" : "Developer Trace ನೋಡಿ"}
                    </button>

                    {showTrace && (
                      <div className="trace-list">
                        {trace.map((item, index) => (
                          <div className="trace-item" key={`${item.step}-${index}`}>
                            <strong>{index + 1}. {item.step}</strong>
                            <span>{item.status}</span>
                            <p>{item.details}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </section>
        )}
      </section>
    </main>
  );
}

export default App;