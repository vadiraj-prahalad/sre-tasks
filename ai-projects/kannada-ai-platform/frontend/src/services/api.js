const API_BASE_URL = "http://127.0.0.1:8000";

export async function askQuestion(question, debug = false) {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      debug,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to get answer from backend");
  }

  return response.json();
}