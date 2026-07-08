import { useEffect, useState } from "react";
import {
  createAdminKnowledge,
  getAdminDashboard,
  listAdminKnowledge,
  refreshAdminKnowledge,
} from "../services/api";

function AdminDashboard() {
  const [adminArticles, setAdminArticles] = useState([]);
  const [adminDashboard, setAdminDashboard] = useState(null);
  const [adminStatus, setAdminStatus] = useState("");
  const [refreshStatus, setRefreshStatus] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [adminSearch, setAdminSearch] = useState("");
  const [adminForm, setAdminForm] = useState({
    question: "",
    answer: "",
    category: "general",
  });

  const filteredAdminArticles = adminArticles.filter((article) => {
    const search = adminSearch.toLowerCase();

    return (
      article.question?.toLowerCase().includes(search) ||
      article.answer?.toLowerCase().includes(search) ||
      article.category?.toLowerCase().includes(search)
    );
  });

  useEffect(() => {
    loadAdminData();
  }, []);

  async function loadAdminData() {
    try {
      const [articlesData, dashboardData] = await Promise.all([
        listAdminKnowledge(),
        getAdminDashboard(),
      ]);

      setAdminArticles(articlesData.articles || []);
      setAdminDashboard(dashboardData || null);
      setAdminStatus("");
    } catch {
      setAdminStatus("Admin knowledge load failed.");
    }
  }

  async function handleAdminSubmit(event) {
    event.preventDefault();

    if (!adminForm.question.trim() || !adminForm.answer.trim()) {
      setAdminStatus("Question and answer are required.");
      return;
    }

    try {
      const result = await createAdminKnowledge(adminForm);

      setAdminStatus(`Article saved. Total admin articles: ${result.total_articles}`);
      setAdminForm({
        question: "",
        answer: "",
        category: "general",
      });

      await loadAdminData();
    } catch {
      setAdminStatus("Failed to save admin article.");
    }
  }

  async function handleRefreshKnowledge() {
    setRefreshing(true);
    setRefreshStatus("Refreshing knowledge...");

    try {
      const result = await refreshAdminKnowledge();
      setRefreshStatus(result.message || "Knowledge refresh completed.");
      await loadAdminData();
    } catch (error) {
      setRefreshStatus(error.message || "Knowledge refresh failed.");
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <section className="admin-card">
      <div className="admin-header">
        <h2>Knowledge Dashboard</h2>
        <p>Manage verified Kannada knowledge without editing JSON manually.</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-tile">
          <span>Total Articles</span>
          <strong>{adminDashboard?.total_articles ?? adminArticles.length}</strong>
        </div>

        <div className="dashboard-tile">
          <span>Categories</span>
          <strong>{Object.keys(adminDashboard?.categories || {}).length}</strong>
        </div>

        <div className="dashboard-tile">
          <span>Recent Articles</span>
          <strong>{adminDashboard?.recent_articles?.length ?? 0}</strong>
        </div>
      </div>

      {adminDashboard?.categories && (
        <div className="category-panel">
          <h3>Category Distribution</h3>

          {Object.entries(adminDashboard.categories).map(([category, count]) => (
            <div className="category-row" key={category}>
              <span>{category}</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
      )}

      <div className="admin-refresh-row">
        <button
          className="primary-button"
          type="button"
          onClick={handleRefreshKnowledge}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing..." : "Refresh Knowledge"}
        </button>

        {refreshStatus && <p className="admin-status">{refreshStatus}</p>}
      </div>

      <form className="admin-form" onSubmit={handleAdminSubmit}>
        <input
          value={adminForm.question}
          onChange={(event) =>
            setAdminForm({
              ...adminForm,
              question: event.target.value,
            })
          }
          placeholder="Question / ಪ್ರಶ್ನೆ"
        />

        <textarea
          value={adminForm.answer}
          onChange={(event) =>
            setAdminForm({
              ...adminForm,
              answer: event.target.value,
            })
          }
          placeholder="Verified answer / ಪರಿಶೀಲಿತ ಉತ್ತರ"
          rows="4"
        />

        <input
          value={adminForm.category}
          onChange={(event) =>
            setAdminForm({
              ...adminForm,
              category: event.target.value,
            })
          }
          placeholder="Category"
        />

        <button className="primary-button" type="submit">
          Save Knowledge
        </button>
      </form>

      {adminStatus && <p className="admin-status">{adminStatus}</p>}

      <div className="admin-list">
        <h3>Admin Articles</h3>

        <input
          className="admin-search"
          value={adminSearch}
          onChange={(event) => setAdminSearch(event.target.value)}
          placeholder="Search articles..."
        />

        {filteredAdminArticles.length === 0 && <p>No matching admin articles.</p>}

        {filteredAdminArticles.map((article, index) => (
          <div className="admin-article" key={`${article.question}-${index}`}>
            <strong>
              {index + 1}. {article.question}
            </strong>
            <p>{article.answer}</p>
            <span>{article.category}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default AdminDashboard;