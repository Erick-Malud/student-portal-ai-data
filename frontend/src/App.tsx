import { useEffect, useRef, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import "./App.css";

// Use relative path for API calls to leverage Vite proxy, or absolute URL if set
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// --- Types ---
type StudentProfile = {
  student_id: string | number;
  name: string;
  email: string;
  gpa?: number;
  completed_courses: string[];
  enrolled_courses: string[];
  total_courses: number;
  join_date?: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  metadata?: ApiResponse; 
};

type ApiResponse = {
  response: string;
  recommended_courses?: string[]; 
  suggested_courses?: {
    course_code: string;
    course_name: string;
    department: string;
  }[];
  student_summary?: {
    student_id: string;
    name: string;
    major: string;
    enrolled_course_count: number;
    performance_level: string;
    intent?: string;
  };
  mode?: string;
  timestamp?: string;
};

type ViewProps = {
  studentId: string;
  studentProfile: StudentProfile | null;
};

// --- Components ---

function Sidebar({ activeTab, setActiveTab }: { activeTab: string, setActiveTab: (t: string) => void }) {
  return (
    <aside className="sidebar">
      <h2>🎓 Portal</h2>
      <nav>
        <div 
          className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <span>📊</span> My Dashboard
        </div>
        <div 
          className={`nav-item ${activeTab === 'advisor' ? 'active' : ''}`}
          onClick={() => setActiveTab('advisor')}
        >
          <span>🤖</span> AI Advisor
        </div>
        <div 
          className={`nav-item ${activeTab === 'predictor' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictor')}
        >
          <span>🔮</span> Success Predictor
        </div>
      </nav>
    </aside>
  );
}

function LoginView({ onLogin }: { onLogin: (id: string) => void }) {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) {
      setError("Please enter a Student ID");
      return;
    }
    onLogin(input.trim());
  };

  return (
    <div style={{ 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center", 
      height: "100vh", 
      background: "#f3f4f6" 
    }}>
      <div className="card" style={{ maxWidth: "400px", width: "100%", padding: "2rem" }}>
        <h2 style={{ textAlign: "center", marginBottom: "2rem", color: "#4f46e5" }}>🎓 Student Portal</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label style={{ display: "block", marginBottom: "0.5rem" }}>Student ID</label>
            <input 
              type="text" 
              className="form-control"
              placeholder="e.g. S002"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{ width: "100%", padding: "0.75rem", borderRadius: "0.5rem", border: "1px solid #d1d5db" }}
            />
          </div>
          {error && <p style={{ color: "red", fontSize: "0.9rem", marginTop: "0.5rem" }}>{error}</p>}
          <button 
            type="submit" 
            className="btn-primary" 
            style={{ width: "100%", marginTop: "1rem", padding: "0.75rem" }}
          >
            Login
          </button>
        </form>
        <p style={{ textAlign: "center", marginTop: "1.5rem", fontSize: "0.9rem", color: "#6b7280" }}>
          Demo IDs: S002, S003
        </p>
      </div>
    </div>
  );
}

function DashboardView({ studentId, studentProfile }: ViewProps) {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!studentId) return;
    setLoading(true);
    setStats(null); // Clear previous stats
    setError(null);
    
    // Fetch Extended Stats
    fetch(`${API_BASE_URL}/api/students/${studentId}/stats`, {
      headers: { "X-API-Key": "dev-api-key-change-in-production" }
    })
      .then(res => {
        if (!res.ok) throw new Error("API Error");
        return res.json();
      })
      .then(data => setStats(data))
      .catch(err => {
        console.error(err);
        setError("Unable to connect to backend (localhost:8000). Start the backend server.");
        setStats(null); // Ensure null on error
      })
      .finally(() => setLoading(false));
  }, [studentId]);

  if (!studentProfile) return <div className="view-container">Please enter a valid Student ID.</div>;

  if (error) {
     return (
       <div className="view-container">
          <h1>Student Dashboard</h1>
          <div className="card" style={{ borderLeft: "5px solid #ef4444", background: "#fef2f2" }}>
             <h3 style={{ color: "#b91c1c", marginTop: 0 }}>Connection Error</h3>
             <p style={{ color: "#991b1b" }}>{error}</p>
             <button onClick={() => window.location.reload()} className="btn-primary" style={{ marginTop: "1rem" }}>Retry Connection</button>
          </div>
       </div>
     );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
  const ATTENDANCE_DATA = (stats?.attendance?.summary) ? [
    { name: 'Present', value: stats.attendance.summary.present },
    { name: 'Absent', value: stats.attendance.summary.absent },
    { name: 'Late', value: stats.attendance.summary.late },
  ] : [];

  return (
    <div className="view-container">
      <h1>Student Dashboard</h1>
      {studentProfile && (
        <div className="card" style={{ marginBottom: "2rem", borderLeft: "5px solid #4f46e5" }}>
          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <h2 style={{ margin: "0 0 0.5rem 0" }}>{studentProfile.name}</h2>
              <div style={{ color: "#6b7280" }}>{studentProfile.email}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "0.9rem", color: "#6b7280" }}>Student ID</div>
              <div style={{ fontSize: "1.2rem", fontWeight: "bold" }}>{studentProfile.student_id}</div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">
            {stats?.gpa !== null && stats?.gpa !== undefined ? Number(stats.gpa).toFixed(2) : "—"}
          </div>
          <div className="stat-label">Current GPA</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">
            {stats?.total_courses !== undefined ? stats.total_courses : "—"}
          </div>
          <div className="stat-label">Total Courses</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">
            {stats?.attendance_rate !== undefined ? `${Number(stats.attendance_rate).toFixed(1)}%` : "—"}
          </div>
          <div className="stat-label">Attendance Rate</div>

          {/* Optional жижиг тайлбар */}
          {stats?.attendance?.total_classes ? (
            <div style={{ fontSize: 12, opacity: 0.75, marginTop: 6 }}>
              {stats.attendance.attended ?? 0}/{stats.attendance.total_classes} attended
            </div>
          ) : null}
        </div>
      </div>


      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
         {/* Course List */}
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Academic Record</h3>
          {loading ? <p>Loading records...</p> : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Course</th>
                  <th>Term</th>
                  <th>Status</th>
                  <th>Grade</th>
                </tr>
              </thead>
              <tbody>
                {stats?.academic_record && stats.academic_record.length > 0 ? stats.academic_record.map((c: any, i: number) => (
                  <tr key={i}>
                    <td>
                      <div style={{ fontWeight: 500 }}>{c.course_name}</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{c.course_code}</div>
                    </td>
                    <td>{c.term || "Fall 2025"}</td>
                    <td>
                      <span style={{ 
                        padding: '0.2rem 0.5rem', 
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        background: c.status === 'completed' ? '#dcfce7' : '#e0f2fe',
                        color: c.status === 'completed' ? '#166534' : '#0369a1'
                      }}>
                        {c.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      {c.grade ? <span style={{ fontWeight: "bold" }}>{c.grade}%</span> : "-"}
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan={4}>No courses found.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Attendance Chart */}
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Attendance Overview</h3>
          <div style={{ width: '100%', height: 250 }}>
            {stats && (
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={ATTENDANCE_DATA}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {ATTENDANCE_DATA.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Grade Chart */}
        <div className="card" style={{ gridColumn: "1 / -1" }}>
          <h3 style={{ marginTop: 0 }}>Grade Performance</h3>
           <div style={{ width: '100%', height: 250 }}>
            {stats && (
              <ResponsiveContainer>
                <BarChart data={stats.academic_record.filter((x:any) => x.grade)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="course_code" tick={{fontSize: 12}} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="grade" fill="#82ca9d" name="Grade %" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

    </div>
  );
}

function PredictorView({ studentId }: ViewProps) {
  const [course, setCourse] = useState("Advanced Machine Learning");
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setPrediction(null);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/predict/performance`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-API-Key": "dev-api-key-change-in-production" 
        },
        body: JSON.stringify({ student_id: studentId, course: course })
      });
      
      if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
      }
      
      const data = await res.json();
      setPrediction(data);
    } catch (err) {
      console.error(err);
      setError("Predictor service unavailable. Please ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-container">
      <h1>Success Predictor Service</h1>
      <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
        Use our regression models to forecast your performance in future courses.
      </p>

      <div className="card" style={{ maxWidth: "600px" }}>
        <div className="form-group">
          <label>Select Target Course</label>
          <select 
            className="form-select" 
            value={course} 
            onChange={(e) => setCourse(e.target.value)}
          >
            <option>Advanced Machine Learning</option>
            <option>Database Systems II</option>
            <option>Web Development Frameworks</option>
            <option>Business Analytics</option>
            <option>Cloud Computing Architecture</option>
          </select>
        </div>
        
        {error && <div style={{ color: "#b91c1c", marginBottom: "1rem", fontSize: "0.9rem" }}>{error}</div>}

        <button 
          className="btn-primary" 
          onClick={handlePredict} 
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Predict Performance"}
        </button>
      </div>

      {prediction && (
        <div className="card" style={{ borderLeft: "5px solid #744fc6", animation: "slideIn 0.3s" }}>
          <h3 style={{ marginTop: 0, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            Predictions Results
            <span className={`risk-badge risk-${prediction.risk_level}`}>
              {prediction.risk_level} RISK
            </span>
          </h3>
          
          <div style={{ display: "flex", gap: "2rem", margin: "1.5rem 0", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: "0.9rem", color: "#6b7280" }}>Expected Grade</div>
              <div style={{ fontSize: "2.5rem", fontWeight: "700", color: "#744fc6" }}>
                {prediction.predicted_grade.toFixed(1)}%
              </div>
            </div>
            <div style={{ borderLeft: "1px solid #eee", paddingLeft: "1.5rem" }}>
              <div style={{ fontSize: "0.9rem", color: "#6b7280" }}>Confidence</div>
              <div style={{ fontWeight: "600" }}>{(prediction.confidence * 100).toFixed(0)}%</div>
            </div>
          </div>

          {prediction.recommendations && (
            <div style={{ background: "#f9fafb", padding: "1rem", borderRadius: "0.5rem" }}>
              <strong style={{ fontSize: "0.9rem", display: "block", marginBottom: "0.5rem" }}>AI Recommendations:</strong>
              <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.95rem", color: "#374151" }}>
                {prediction.recommendations.map((rec: string, i: number) => (
                  <li key={i} style={{ marginBottom: "0.25rem" }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// --- Main App Component ---
function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [studentId, setStudentId] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [studentProfile, setStudentProfile] = useState<StudentProfile | null>(null);
  
  // Navigation State
  const [activeTab, setActiveTab] = useState("dashboard");

  const bottomRef = useRef<HTMLDivElement>(null);

  // Check Login State on Mount
  useEffect(() => {
    const savedId = localStorage.getItem("portal_student_id");
    if (savedId) {
      setStudentId(savedId);
      setIsLoggedIn(true);
      // Generate session ID if restoring session
      setSessionId("web-" + Math.random().toString(36).substring(7));
      // Restore welcome message if empty
      setMessages([{
        role: "assistant",
        content: "Welcome! Ask me about your courses, career path, or study plans."
      }]);
    }
  }, []);

  // Fetch Student Profile
  useEffect(() => {
    const fetchProfile = async () => {
      if (!isLoggedIn || !studentId) return;
      try {
        const res = await fetch(`${API_BASE_URL}/api/students/${studentId}`, {
          headers: { "X-API-Key": "dev-api-key-change-in-production" }
        });
        if (res.ok) {
          const data = await res.json();
          setStudentProfile(data);
        } else {
          console.error("Profile not found");
        }
      } catch (e) {
        console.error("Failed to fetch profile", e);
      }
    };
    fetchProfile();
  }, [studentId, isLoggedIn]);

  const handleLogin = (id: string) => {
    setStudentId(id);
    setIsLoggedIn(true);
    localStorage.setItem("portal_student_id", id);
    setActiveTab("dashboard");
    
    // Initialize Session
    setSessionId("web-" + Math.random().toString(36).substring(7));
    setMessages([{
      role: "assistant", 
      content: "Welcome! Ask me about your courses, career path, or study plans."
    }]);
  };

  const handleLogout = () => {
    setStudentId("");
    setIsLoggedIn(false);
    setStudentProfile(null);
    localStorage.removeItem("portal_student_id");
    setMessages([]);
    setSessionId("");
  };

  // Chat Logic
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userText = input;
    const userMessage: Message = { role: "user", content: userText };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-API-Key": "dev-api-key-change-in-production" 
        },
        body: JSON.stringify({
          message: userText,
          student_id: studentId,
          session_id: sessionId,
        }),
      });
      if (!res.ok) throw new Error(`API Error: ${res.status}`);
      const json: ApiResponse = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: json.response, metadata: json }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { role: "assistant", content: "Unable to connect to AI service. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isLoggedIn) {
    return <LoginView onLogin={handleLogin} />;
  }

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="main-content">
        {/* Header */}
        <header>
          {activeTab === 'advisor' && <h1>Student AI Advisor</h1>}
          {activeTab === 'dashboard' && <h1>My Academic Hub</h1>}
          {activeTab === 'predictor' && <h1>Grade Predictor</h1>}
          
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "1rem", fontSize: "0.9rem" }}>
            {studentProfile && (
              <div style={{ display: "flex", gap: "1rem", marginRight: "1rem", paddingRight: "1rem", borderRight: "1px solid #e5e7eb" }}>
                 <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", lineHeight: "1.2" }}>
                   <span style={{ fontWeight: "600" }}>{studentProfile.name}</span>
                   <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>Mustang University</span>
                 </div>
              </div>
            )}
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <span style={{ color: "#374151", fontWeight: "500" }}>Student ID: {studentId}</span>
              <button 
                onClick={handleLogout}
                style={{ 
                  padding: "0.4rem 0.8rem", 
                  borderRadius: "4px", 
                  border: "1px solid #ef4444", 
                  background: "transparent",
                  color: "#ef4444",
                  cursor: "pointer",
                  fontSize: "0.85rem"
                }}
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        {/* Views */}
        {activeTab === 'advisor' && (
          <>
            <div className="chat-window">
              {messages.map((m, i) => (
                <div key={i} className={`message-wrapper ${m.role}`}>
                  <div className={`avatar ${m.role === 'assistant' ? 'ai' : ''}`}>
                     {m.role === 'assistant' ? '🤖' : '👤'}
                  </div>
                  <div className="message-content">
                    <div className="message-bubble">{m.content}</div>
                    {m.role === "assistant" && m.metadata && (
                      <div className="metadata-panel">
                        {m.metadata.student_summary && (
                          <div className="metadata-grid">
                             <div className="stat-item"><span>Major</span><strong>{m.metadata.student_summary.major}</strong></div>
                          </div>
                        )}
                        {m.metadata.suggested_courses && m.metadata.suggested_courses.length > 0 && (
                          <div style={{ padding: "0 1rem 1rem 1rem" }}>
                            <span className="rec-title">Recommended Courses</span>
                            <div className="courses-grid">
                              {m.metadata.suggested_courses.map((c) => (
                                <div key={c.course_code} className="course-card">
                                  <span className="course-code">{c.course_code}</span>
                                  <span className="course-name">{c.course_name}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message-wrapper assistant">
                   <div className="avatar ai">🤖</div>
                   <div className="message-bubble"><div className="loading-dots"><div className="dot"></div><div className="dot"></div><div className="dot"></div></div></div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
            <div className="input-area">
              <div className="input-container">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message here..."
                  disabled={loading}
                />
                <button className="send-btn" onClick={sendMessage} disabled={loading || !input.trim()}>Send</button>
              </div>
            </div>
          </>
        )}

        {activeTab === 'dashboard' && <DashboardView studentId={studentId} studentProfile={studentProfile} />}
        {activeTab === 'predictor' && <PredictorView studentId={studentId} studentProfile={studentProfile} />}
      </main>
    </div>
  );
}

export default App;
