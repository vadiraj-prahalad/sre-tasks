import { useState } from "react";
import { askQuestion } from "./services/api";
import "./App.css";

function splitAnswerAndSources(rawAnswer) {
  if (!rawAnswer.includes("\n\nಮೂಲ:")) {
    return {
      answerText: rawAnswer,
      sources: [],
    };
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAsk() {
    if (!question.trim()) {
      setError("ದಯವಿಟ್ಟು ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setLastQuestion(question);

    try {
      const data = await askQuestion(question);
      setAnswer(data.answer);
    } catch (err) {
      setError("Backend ಸಂಪರ್ಕದಲ್ಲಿ ಸಮಸ್ಯೆ ಇದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.");
    } finally {
      setLoading(false);
    }
  }

  const { answerText, sources } = splitAnswerAndSources(answer);

  return (
    <main className="app">
      <section className="hero">
        <div className="title-block">
          <span className="badge">Kannada AI</span>
          <h1>ಕನ್ನಡ ಜ್ಞಾನ ಸಹಾಯಕ</h1>
          <p>ಕನ್ನಡ, ಸಂಸ್ಕೃತಿ, ಇತಿಹಾಸ ಮತ್ತು ಜ್ಞಾನಕ್ಕಾಗಿ ವಿಶ್ವಾಸಾರ್ಹ ಸಹಾಯಕ</p>
        </div>

        <div className="search-card">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="ಉದಾ: ಪುರಂದರ ದಾಸರು ಯಾರು?"
            rows="3"
          />

          <button onClick={handleAsk} disabled={loading}>
            {loading ? "ಉತ್ತರ ಸಿದ್ಧಪಡಿಸುತ್ತಿದೆ..." : "ಪ್ರಶ್ನಿಸಿ"}
          </button>
        </div>

        <div className="suggestions">
          <button onClick={() => setQuestion("ಪುರಂದರ ದಾಸರು ಯಾರು?")}>
            ಪುರಂದರ ದಾಸರು
          </button>
          <button onClick={() => setQuestion("ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?")}>
            ವಿಷ್ಣುವರ್ಧನ್
          </button>
          <button onClick={() => setQuestion("ಕುವೆಂಪು ಕನ್ನಡ ಸಾಹಿತ್ಯ")}>
            ಕುವೆಂಪು
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {(lastQuestion || loading || answer) && (
          <section className="chat-panel">
            {lastQuestion && (
              <div className="message user-message">
                <div className="avatar">🙋</div>
                <div>
                  <p className="label">ನೀವು ಕೇಳಿದ್ದು</p>
                  <p>{lastQuestion}</p>
                </div>
              </div>
            )}

            {loading && (
              <div className="message ai-message">
                <div className="avatar">🤖</div>
                <div>
                  <p className="label">AI ಉತ್ತರ</p>
                  <p className="loading-text">ವಿಶ್ವಾಸಾರ್ಹ ಮೂಲಗಳಿಂದ ಹುಡುಕುತ್ತಿದೆ...</p>
                </div>
              </div>
            )}

            {answer && !loading && (
              <div className="message ai-message">
                <div className="avatar">🤖</div>
                <div className="answer-content">
                  <p className="label">ವಿಶ್ವಾಸಾರ್ಹ ಉತ್ತರ</p>
                  <p>{answerText}</p>

                  {sources.length > 0 && (
                    <div className="sources-card">
                      <h3>📚 ಮೂಲಗಳು</h3>
                      {sources.map((source) => (
                        <div className="source-pill" key={source}>
                          📄 {source}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </section>
        )}
      </section>
    </main>
  );
}

export default App;