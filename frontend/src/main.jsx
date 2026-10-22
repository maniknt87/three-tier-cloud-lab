import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = import.meta.env.VITE_API_BASE_URL || "/api";

function Login({ onLogin }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Login failed");
      localStorage.setItem("token", data.access_token);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page center">
      <form className="card login-card" onSubmit={submit}>
        <div className="brand">CLOUD LAB</div>
        <h1>Admin Portal</h1>
        <p className="muted">Three-tier cloud application</p>

        <label>Username</label>
        <input value={username} onChange={e => setUsername(e.target.value)} />

        <label>Password</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} />

        {error && <div className="error">{error}</div>}

        <button disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>

        <p className="hint">Lab user: admin / ChangeMe123!</p>
      </form>
    </div>
  );
}

function Dashboard({ user, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };

    Promise.all([
      fetch(`${API}/profile`, { headers }),
      fetch(`${API}/stats`, { headers }),
    ])
      .then(async ([profileRes, statsRes]) => {
        const p = await profileRes.json();
        const s = await statsRes.json();
        if (!profileRes.ok || !statsRes.ok) throw new Error("Session expired");
        setProfile(p);
        setStats(s);
      })
      .catch(err => setError(err.message));
  }, []);

  function logout() {
    localStorage.removeItem("token");
    onLogout();
  }

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">CLOUD LAB</div>
        <button className="secondary" onClick={logout}>Logout</button>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <p className="eyebrow">AUTHENTICATED</p>
            <h1>Welcome, {user.display_name}</h1>
            <p className="muted">This page is backed by a FastAPI API and MySQL database.</p>
          </div>
        </section>

        {error && <div className="error">{error}</div>}

        <section className="grid">
          <div className="card">
            <h3>User</h3>
            <p><strong>{profile?.display_name || user.display_name}</strong></p>
            <p className="muted">{profile?.username || user.username}</p>
            <span className="badge">{profile?.role || user.role}</span>
          </div>

          <div className="card">
            <h3>Database</h3>
            <p className="big">{stats?.total_users ?? "—"}</p>
            <p className="muted">registered users</p>
          </div>

          <div className="card">
            <h3>API</h3>
            <p className="big">{stats?.successful_logins ?? "—"}</p>
            <p className="muted">successful logins</p>
          </div>

          <div className="card">
            <h3>Architecture</h3>
            <p>React UI → FastAPI → MySQL</p>
            <p className="muted">Designed for private backend/database deployment.</p>
          </div>
        </section>
      </main>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);

  function logout() {
    setUser(null);
  }

  return user ? (
    <Dashboard user={user} onLogout={logout} />
  ) : (
    <Login onLogin={setUser} />
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode><App /></React.StrictMode>
);
