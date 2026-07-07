const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function askQuestion(question, debug = false, conversationId = "default") {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      debug,
      conversation_id: conversationId,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to get answer from backend");
  }

  return response.json();
}

export async function submitFeedback(payload) {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to submit feedback");
  }

  return response.json();
}

export async function listAdminKnowledge() {
  const response = await fetch(`${API_BASE_URL}/admin/knowledge`);

  if (!response.ok) {
    throw new Error("Failed to load admin knowledge");
  }

  return response.json();
}

export async function createAdminKnowledge(payload) {
  const response = await fetch(`${API_BASE_URL}/admin/knowledge`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to create admin knowledge");
  }

  return response.json();
}

export async function getAdminDashboard() {
  const response = await fetch(`${API_BASE_URL}/admin/knowledge/dashboard`);

  if (!response.ok) {
    throw new Error("Failed to load admin dashboard");
  }

  return response.json();
}

export async function refreshAdminKnowledge() {
  const response = await fetch(`${API_BASE_URL}/admin/refresh`, {
    method: "POST",
  });

  const data = await response.json();

  if (!response.ok || data.status !== "success") {
    throw new Error(data.message || "Failed to refresh knowledge");
  }

  return data;
}