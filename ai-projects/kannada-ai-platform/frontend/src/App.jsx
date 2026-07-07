import { useState } from "react";
import { askQuestion, submitFeedback } from "./services/api";
import "./App.css";

const suggestedQuestions = [
  { label: "🎭 ಯಕ್ಷಗಾನ", question: "ಯಕ್ಷಗಾನ ಎಂದರೇನು?" },
  { label: "🎵 ಪುರಂದರ ದಾಸರು", question: "ಪುರಂದರ ದಾಸರು ಯಾರು?" },
  { label: "📖 ಕುವೆಂಪು", question: "ಕುವೆಂಪು ಯಾರು?" },
  { label: "📝 ಕನ್ನಡ ವ್ಯಾಕರಣ", question: "ಕನ್ನಡ ವ್ಯಾಕರಣ ಎಂದರೇನು?" },
];

function getConversationId() {
  const existingId = localStorage.getItem("kannada_ai_conversation_id");

  if (existingId) {
    return existingId;
  }

  const newId = crypto.randomUUID();
  localStorage.setItem("kannada_ai_conversation_id", newId);
  return newId;
}

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

function getTrustBadge(confidence) {
  if (!confidence) {
    return {
      icon: "⚪",
      title: "Unknown",
      subtitle: "No confidence data available",
      className: "trust-neutral",
      scoreText: "ವಿಶ್ವಾಸಾರ್ಹತೆ ಲಭ್ಯವಿಲ್ಲ",
    };
  }

  if (confidence.score >= 90) {
    return {
      icon: "🟢",
      title: "Trusted Answer",
      subtitle: "Verified knowledge source",
      className: "trust-high",
      scoreText: `${confidence.score}% · ${confidence.kannada_label}`,
    };
  }

  if (confidence.score >= 50) {
    return {
      icon: "🟡",
      title: "AI Generated",
      subtitle: "Needs human verification",
      className: "trust-medium",
      scoreText: `${confidence.score}% · ${confidence.kannada_label}`,
    };
  }

  return {
    icon: "🟠",
    title: "Limited Information",
    subtitle: "Low confidence answer",
    className: "trust-low",
    scoreText: `${confidence.score}% · ${confidence.kannada_label}`,
  };
}

function App() {
  const [conversationId] = useState(getConversationId);
  const [question, setQuestion] = useState("");
  const [lastQuestion, setLastQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [trace, setTrace] = useState([]);
  const [confidence, setConfidence] = useState(null);
  const [relatedTopics, setRelatedTopics] = useState([]);
  const [showTrace, setShowTrace] = useState(false);
  const [developerMode, setDeveloperMode] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [memoryInfo, setMemoryInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { answerText, sources } = splitAnswerAndSources(answer);
  const trustBadge = getTrustBadge(confidence);
  const isTrustedAnswer = confidence?.score >= 90;

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
    setRelatedTopics([]);
    setShowTrace(false);
    setFeedbackStatus("");
    setMemoryInfo(null);
    setLastQuestion(selectedQuestion);
    setQuestion(selectedQuestion);

    try {
      const data = await askQuestion(selectedQuestion, true, conversationId);
      setAnswer(data.answer);
      setTrace(data.trace || []);
      setConfidence(data.confidence || null);
      setRelatedTopics(data.related_topics || []);
      setMemoryInfo(data.memory || null);
    } catch {
      setError("Backend ಸಂಪರ್ಕದಲ್ಲಿ ಸಮಸ್ಯೆ ಇದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.");
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(rating) {
    try {
      await submitFeedback({
        question: lastQuestion,
        answer: answerText,
        rating,
        confidence_score: confidence?.score ?? null,
        source: sources[0] || null,
      });

      setFeedbackStatus(
        rating === "positive"
          ? "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಪ್ರತಿಕ್ರಿಯೆ ಉಳಿಸಲಾಗಿದೆ."
          : "ಧನ್ಯವಾದಗಳು. ಈ ಉತ್ತರವನ್ನು ಸುಧಾರಣೆಗೆ ಗುರುತಿಸಲಾಗಿದೆ."
      );
    } catch {
      setFeedbackStatus("ಪ್ರತಿಕ್ರಿಯೆ ಉಳಿಸಲು ಸಮಸ್ಯೆ ಆಯಿತು.");
    }
  }

  return (
    <main className="app">
      <section className="shell">
        <header className="hero">
          <div className="top-row">
            <div className="badge">Kannada AI Beta</div>

            <label className="dev-toggle">
              <input
                type="checkbox"
                checked={developerMode}
                onChange={(event) => setDeveloperMode(event.target.checked)}
              />
              Developer Mode
            </label>
          </div>

          <h1>ಕನ್ನಡ ಜ್ಞಾನ ಸಹಾಯಕ</h1>
          <p>ಕನ್ನಡ ಸಂಸ್ಕೃತಿ, ಸಾಹಿತ್ಯ, ಇತಿಹಾಸ ಮತ್ತು ಜ್ಞಾನಕ್ಕಾಗಿ ಸರಳ AI ಸಹಾಯಕ</p>
        </header>

        <section className="ask-card">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="ಉದಾ: ಕನ್ನಡ ವ್ಯಾಕರಣ ಎಂದರೇನು?"
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
                  <h2>ಉತ್ತರ ಸಿದ್ಧಪಡಿಸುತ್ತಿದೆ</h2>
                  <p>ಜ್ಞಾನ ಮೂಲಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತಿದೆ...</p>
                </div>
              </div>
            )}

            {answer && !loading && (
              <div className="answer-card">
                <div className="answer-header">
                  <h2>ಉತ್ತರ</h2>
                </div>

                {developerMode && memoryInfo?.used && (
                  <div className="memory-card">
                    <strong>Conversation Memory</strong>
                    <span>Memory used: YES</span>
                    <span>Entity: {memoryInfo.entity}</span>
                  </div>
                )}

                <p className="answer-text">{answerText}</p>

                <div className={`trust-card ${trustBadge.className}`}>
                  <div className="trust-icon">{trustBadge.icon}</div>
                  <h3>{trustBadge.title}</h3>
                  <p>{trustBadge.subtitle}</p>
                  <span className="trust-score">{trustBadge.scoreText}</span>
                </div>

                {sources.length > 0 && (
                  <div className="sources-row">
                    <span className="section-label">📚 ಮೂಲಗಳು</span>
                    <div className="source-list">
                      {sources.map((source) => (
                        <span className="source-chip" key={source}>
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {relatedTopics.length > 0 && (
                  <div className="related-card">
                    <span className="section-label">🔍 ಇನ್ನಷ್ಟು ಅನ್ವೇಷಿಸಿ</span>
                    <div className="related-list">
                      {relatedTopics.map((topic) => (
                        <button
                          key={topic}
                          onClick={() => handleAsk(topic)}
                          disabled={loading}
                        >
                          {topic}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {confidence?.reasons?.length > 0 && (
                  <div className="insight-card">
                    <span className="section-label">
                      {isTrustedAnswer
                        ? "💡 ಈ ಉತ್ತರವನ್ನು ಏಕೆ ನಂಬಬಹುದು?"
                        : "⚠️ AI ಉತ್ತರ — ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ"}
                    </span>

                    <div className="insight-list">
                      {isTrustedAnswer ? (
                        confidence.reasons.map((reason) => (
                          <div key={reason}>✓ {reason}</div>
                        ))
                      ) : (
                        <>
                          <div>✓ ಪರಿಶೀಲಿತ ಮೂಲ ಸಿಗಲಿಲ್ಲ</div>
                          <div>✓ ಸಾಮಾನ್ಯ AI ಉತ್ತರ ಬಳಸಲಾಗಿದೆ</div>
                          <div>✓ ತಪ್ಪುಗಳಿರಬಹುದು, ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ</div>
                        </>
                      )}
                    </div>
                  </div>
                )}

                <div className="feedback-card">
                  <span>ಈ ಉತ್ತರ ಉಪಯುಕ್ತವಾಗಿತ್ತೇ?</span>
                  <div>
                    <button type="button" onClick={() => handleFeedback("positive")}>
                      👍 ಹೌದು
                    </button>
                    <button type="button" onClick={() => handleFeedback("negative")}>
                      👎 ಸುಧಾರಣೆ ಬೇಕು
                    </button>
                  </div>
                  {feedbackStatus && <p className="feedback-status">{feedbackStatus}</p>}
                </div>

                {developerMode && trace.length > 0 && (
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