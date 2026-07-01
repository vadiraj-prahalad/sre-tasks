import { useState } from "react";
import { askQuestion } from "./services/api";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
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

    try {
      const data = await askQuestion(question);
      setAnswer(data.answer);
    } catch (err) {
      setError("Backend ಸಂಪರ್ಕದಲ್ಲಿ ಸಮಸ್ಯೆ ಇದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <h1>ಕನ್ನಡ ಜ್ಞಾನ ಸಹಾಯಕ</h1>
        <p>ಕನ್ನಡ, ಸಂಸ್ಕೃತಿ, ಇತಿಹಾಸ ಮತ್ತು ಜ್ಞಾನಕ್ಕಾಗಿ ವಿಶ್ವಾಸಾರ್ಹ ಸಹಾಯಕ</p>

        <div className="search-card">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="ಉದಾ: ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?"
            rows="3"
          />

          <button onClick={handleAsk} disabled={loading}>
            {loading ? "ಹುಡುಕುತ್ತಿದೆ..." : "ಪ್ರಶ್ನಿಸಿ"}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {answer && (
          <div className="answer-card">
            <h2>ವಿಶ್ವಾಸಾರ್ಹ ಉತ್ತರ</h2>
            <p>{answer}</p>
          </div>
        )}

        <div className="suggestions">
          <button onClick={() => setQuestion("ಅಣ್ಣಾವ್ರು")}>ಅಣ್ಣಾವ್ರು</button>
          <button onClick={() => setQuestion("madhwa")}>madhwa</button>
          <button onClick={() => setQuestion("ಬೆಂಗಳೂರು ಬಗ್ಗೆ ಹೇಳಿ")}>
            ಬೆಂಗಳೂರು
          </button>
        </div>
      </section>
    </main>
  );
}

export default App;
