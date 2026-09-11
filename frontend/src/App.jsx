import { useState, useEffect } from "react";
import "./App.css";

// 배포할 때는 VITE_API_URL 에 렌더 주소를 쓴다.
// 값이 없으면 로컬 서버를 쓴다.
const API = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  const loadSessions = async () => {
    const res = await fetch(`${API}/sessions`);
    const data = await res.json();
    setSessions(data.sessions);
    return data.sessions;
  };

  const loadMsgs = async (id) => {
    if (!id) {
      setMsgs([]);
      return;
    }
    const res = await fetch(`${API}/sessions/${id}/messages`);
    const data = await res.json();
    setMsgs(data.messages);
  };

  useEffect(() => {
    loadSessions().then(list => {
      if (list.length > 0) {
        setSessionId(list[0].id);
        loadMsgs(list[0].id);
      }
    });
  }, []);

  const openSession = (id) => {
    setSessionId(id);
    setEditId(null);
    loadMsgs(id);
  };

  const newSession = async () => {
    const res = await fetch(`${API}/sessions`, { method: "POST" });
    const data = await res.json();
    await loadSessions();
    setSessionId(data.id);
    setMsgs([]);
  };

  const startRename = (s) => {
    setEditId(s.id);
    setEditTitle(s.title);
  };

  const saveTitle = async (id) => {
    await fetch(`${API}/sessions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: editTitle })
    });
    setEditId(null);
    await loadSessions();
  };

  const removeSession = async (id) => {
    await fetch(`${API}/sessions/${id}`, { method: "DELETE" });
    const list = await loadSessions();
    const next = list.length > 0 ? list[0].id : null;
    setSessionId(next);
    loadMsgs(next);
  };

  const send = async () => {
    if (!input.trim() || !sessionId) return;
    const text = input;
    setInput("");
    setLoading(true);
    await fetch(`${API}/sessions/${sessionId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    await loadMsgs(sessionId);
    await loadSessions();
    setLoading(false);
  };

  const onKey = (e) => {
    if (e.key === "Enter") send();
  };

  return (
    <div className="app">
      <aside className="side">
        <button className="new" onClick={newSession}>+ 새 대화</button>
        <ul className="session-list">
          {sessions.map(s => (
            <li key={s.id} className={s.id === sessionId ? "session on" : "session"}>
              {editId === s.id ? (
                <span className="rename">
                  <input value={editTitle} onChange={e => setEditTitle(e.target.value)} />
                  <button onClick={() => saveTitle(s.id)}>저장</button>
                </span>
              ) : (
                <>
                  <button className="session-title" onClick={() => openSession(s.id)}>{s.title}</button>
                  <span className="session-tools">
                    <button onClick={() => startRename(s)}>이름</button>
                    <button onClick={() => removeSession(s.id)}>삭제</button>
                  </span>
                </>
              )}
            </li>
          ))}
        </ul>
      </aside>

      <main className="chat">
        <div className="box">
          {msgs.map(m => (
            <div key={m.id} className={m.role}>
              <p>{m.text}</p>
            </div>
          ))}
          {loading && <p className="loading">생각 중...</p>}
        </div>
        <div className="input-row">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder="메시지를 입력하세요"
          />
          <button onClick={send}>전송</button>
        </div>
      </main>
    </div>
  );
}
