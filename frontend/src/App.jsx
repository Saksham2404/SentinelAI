import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  Activity,
  AlertTriangle,
  FileText,
  LayoutDashboard,
  Search,
  Settings,
  ShieldAlert,
  Clock,
  CheckCircle2,
  UploadCloud,
  FileCode,
  Zap,
  History,
  ChevronRight,
  Database,
  ArrowLeft,
  X,
  FileDown,
  Moon,
  Sun,
  Filter,
} from "lucide-react";
import TopNav from "./components/TopNav";
import ReportCard from "./components/ReportCard";
import ErrorBanner from "./components/ErrorBanner";
import "./theme.css";



// ── Helpers ──────────────────────────────────────────────────────────
function formatText(val) {
  if (val == null) return "N/A";
  return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return (
      d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) +
      " · " +
      d.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })
    );
  } catch {
    return dateStr;
  }
}

function timeAgo(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const seconds = Math.floor((now - d) / 1000);
    if (seconds < 60) return "just now";
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  } catch {
    return "";
  }
}

// ── Custom Visual Chart Components ─────────────────────────────────────
function AnomalyDistributionChart({ anomalies }) {
  if (!anomalies || anomalies.length === 0) return null;
  const maxScore = Math.max(...anomalies.map((a) => a.anomaly_score || 0.1)) || 1;

  return (
    <div className="glassmorphism p-6 border-slate-800">
      <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
        <Activity size={16} className="text-rose-400" />
        Anomaly Weight Distribution
      </h4>
      <div className="flex items-end justify-between gap-3 h-40 pt-4">
        {anomalies.map((anomaly, idx) => {
          const heightPercent = ((anomaly.anomaly_score || 0) / maxScore) * 100;
          return (
            <div key={idx} className="flex-1 flex flex-col items-center group relative">
              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 bg-slate-900 border border-slate-700 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-20 shadow-xl">
                Score: {anomaly.anomaly_score?.toFixed(5)} ({anomaly.service})
              </div>
              {/* Bar */}
              <div
                style={{ height: `${Math.max(heightPercent, 10)}%` }}
                className="w-full bg-gradient-to-t from-rose-600 to-rose-400 rounded-t-md group-hover:from-rose-500 group-hover:to-rose-300 transition-all duration-300 glow-rose"
              />
              {/* Label */}
              <span className="text-[9px] text-slate-500 mt-2 truncate w-full text-center">
                {anomaly.service || "unknown"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ServiceBreakdownChart({ anomalies }) {
  if (!anomalies || anomalies.length === 0) return null;

  const counts = {};
  anomalies.forEach((a) => {
    if (a.service) {
      counts[a.service] = (counts[a.service] || 0) + 1;
    }
  });

  const maxCount = Math.max(...Object.values(counts));

  return (
    <div className="glassmorphism p-6 border-slate-800">
      <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
        <Database size={16} className="text-blue-400" />
        Service Breakdown
      </h4>
      <div className="space-y-4">
        {Object.entries(counts).map(([service, count]) => {
          const widthPercent = (count / maxCount) * 100;
          return (
            <div key={service} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-semibold">{service}</span>
                <span className="text-blue-400 font-bold">{count} {count === 1 ? 'incident' : 'incidents'}</span>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-2 border border-slate-900">
                <div
                  style={{ width: `${widthPercent}%` }}
                  className="bg-gradient-to-r from-blue-500 to-teal-500 h-full rounded-full glow-blue transition-all duration-500"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Main App ─────────────────────────────────────────────────────────
function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [useMock, setUseMock] = useState(false);

  // Navigation
  const [activePage, setActivePage] = useState("dashboard");

  // Drag & Drop State
  const [isDragging, setIsDragging] = useState(false);

  // Toast Notifications State
  const [toasts, setToasts] = useState([]);

  // Theme Management (Light/Dark Mode)
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");

  // Settings Management
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [apiBase, setApiBase] = useState(() => localStorage.getItem("apiBaseUrl") || "http://127.0.0.1:8001");
  const [tempApiBase, setTempApiBase] = useState(apiBase);

  // Sync tempApiBase when modal is opened
  useEffect(() => {
    if (isSettingsOpen) {
      setTempApiBase(apiBase);
    }
  }, [isSettingsOpen, apiBase]);

  // Cumulative stats from DB
  const [cumulativeStats, setCumulativeStats] = useState({
    total_parsed_events: 0,
    total_anomalies: 0,
    total_runs: 0,
  });

  // Investigation history
  const [historyRuns, setHistoryRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const fileInputRef = useRef(null);

  // Apply Theme class
  useEffect(() => {
    localStorage.setItem("theme", theme);
    const root = window.document.documentElement;
    if (theme === "light") {
      root.classList.add("light");
    } else {
      root.classList.remove("light");
    }
  }, [theme]);

  // Toast Helper
  const showToast = (message, type = "success") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // Fetch cumulative stats
  const fetchStats = async () => {
    try {
      const res = await fetch(`${apiBase}/api/history/stats`);
      if (res.ok) {
        const data = await res.json();
        setCumulativeStats(data);
      }
    } catch {
      // fail silently
    }
  };

  // Fetch investigation history
  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/history/runs`);
      if (res.ok) {
        const data = await res.json();
        setHistoryRuns(data.runs || []);
      }
    } catch {
      // fail silently
    } finally {
      setHistoryLoading(false);
    }
  };

  // Fetch single run detail
  const fetchRunDetail = async (runId) => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/history/runs/${runId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedRun(data);
        showToast(`Loaded Run Details for #${runId}`);
      }
    } catch {
      showToast("Failed to fetch run details", "error");
    } finally {
      setHistoryLoading(false);
    }
  };

  // Load initial dataset stats
  useEffect(() => {
    fetchStats();
    fetchHistory();
  }, [apiBase]); // Re-fetch if API host changes

  // Update triggers on navigation
  useEffect(() => {
    if (activePage === "investigations" || activePage === "activity") {
      fetchHistory();
    }
    fetchStats();
  }, [activePage, apiBase]);


  // Log Selection handlers
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setSelectedFile(file);
    setResult(null);
    setError(null);
    showToast(`Log file selected: ${file.name}`);
  };

  const handleDroppedFile = (file) => {
    if (!file.name.endsWith(".log") && !file.name.endsWith(".txt")) {
      showToast("Only .log and .txt files are supported", "error");
      return;
    }
    setSelectedFile(file);
    setResult(null);
    setError(null);
    showToast(`Log file dropped: ${file.name}`);
  };

  // Drag & drop handlers
  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleDroppedFile(file);
    }
  };

  const handleInvestigate = async () => {
    if (!selectedFile) {
      setError("Please select a log file first.");
      showToast("No log file selected", "error");
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    showToast("Starting log analysis & anomaly detection...");
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const endpoint = useMock
        ? `${apiBase}/mock/investigate/`
        : `${apiBase}/investigate/`;
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Investigation failed.");
      }
      setResult(data);
      showToast("Investigation completed successfully!");
      fetchStats();
      fetchHistory();
    } catch (err) {
      setError(err.message);
      showToast("Investigation pipeline failed", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const pipeline = result?.pipeline_summary;

  const getImpactBadge = (impact) => {
    const normalized = String(impact || "").toLowerCase();
    if (normalized.includes("high") || normalized.includes("critical")) {
      return "bg-rose-500/10 border-rose-500/30 text-rose-400";
    }
    if (normalized.includes("medium") || normalized.includes("warning")) {
      return "bg-amber-500/10 border-amber-500/30 text-amber-400";
    }
    return "bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "investigations", label: "Investigations", icon: FileText },
    { id: "activity", label: "System Activity", icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-teal-500 selection:text-white transition-colors duration-300">
      {/* Background ambient glows */}
      <div className="fixed top-0 left-1/4 h-[500px] w-[500px] rounded-full bg-teal-500/10 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-0 right-1/4 h-[500px] w-[500px] rounded-full bg-blue-500/10 blur-[120px] pointer-events-none" />

      <TopNav useMock={useMock} setUseMock={setUseMock} theme={theme} setTheme={setTheme} onSettingsClick={() => setIsSettingsOpen(true)} />

      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="sticky top-0 h-screen w-64 border-r border-slate-900 bg-slate-950/80 backdrop-blur-xl p-6 flex flex-col justify-between z-10">
          <div>
            <div className="mb-10 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-500 to-blue-600 shadow-[0_0_20px_rgba(20,184,166,0.3)]">
                <ShieldAlert size={22} className="text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  SentinelAI
                </h1>
                <p className="text-xs text-teal-500/80 font-medium tracking-wider uppercase">
                  Incident Intelligence
                </p>
              </div>
            </div>

            <nav className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activePage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActivePage(item.id);
                      setSelectedRun(null);
                    }}
                    className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? "bg-gradient-to-r from-teal-600/20 to-blue-600/10 border border-teal-500/20 text-teal-300 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]"
                        : "text-slate-400 border border-transparent hover:bg-slate-900/50 hover:text-white"
                    }`}
                  >
                    <Icon size={18} className={isActive ? "text-teal-400" : ""} />
                    {item.label}
                    {item.id === "investigations" && historyRuns.length > 0 && (
                      <span className="ml-auto rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-bold text-slate-300">
                        {historyRuns.length}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="border-t border-slate-900 pt-6">
            <button 
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center gap-3 px-4 py-2 text-sm font-medium text-slate-400 transition hover:text-white"
            >
              <Settings size={18} />
              Settings
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 bg-slate-950/40 p-8 overflow-y-auto">
          {activePage === "dashboard" && (
            <DashboardPage
              cumulativeStats={cumulativeStats}
              result={result}
              pipeline={pipeline}
              isLoading={isLoading}
              error={error}
              setError={setError}
              selectedFile={selectedFile}
              fileInputRef={fileInputRef}
              handleFileChange={handleFileChange}
              handleInvestigate={handleInvestigate}
              getImpactBadge={getImpactBadge}
              isDragging={isDragging}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            />
          )}
          {activePage === "investigations" && (
            <InvestigationsPage
              historyRuns={historyRuns}
              historyLoading={historyLoading}
              selectedRun={selectedRun}
              setSelectedRun={setSelectedRun}
              fetchRunDetail={fetchRunDetail}
            />
          )}
          {activePage === "activity" && (
            <SystemActivityPage historyRuns={historyRuns} historyLoading={historyLoading} />
          )}
        </main>
      </div>

      {/* Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glassmorphism w-full max-w-md p-6 border-slate-800 shadow-2xl relative animate-fade-in text-left">
            <button
              onClick={() => setIsSettingsOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white transition p-1 hover:bg-slate-900 rounded-lg"
            >
              <X size={18} />
            </button>

            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Settings size={20} className="text-teal-400" />
              System Settings
            </h3>

            <div className="space-y-4">
              {/* API Base URL Setting */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Backend API Endpoint</label>
                <input
                  type="text"
                  value={tempApiBase}
                  onChange={(e) => setTempApiBase(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl text-sm px-3 py-2 text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              {/* Mode Settings */}
              <div className="flex justify-between items-center py-2 border-t border-b border-slate-900">
                <div>
                  <p className="text-sm font-semibold text-white">Mock Mode Investigation</p>
                  <p className="text-[11px] text-slate-400">Simulate responses to preserve API quotas</p>
                </div>
                <input
                  type="checkbox"
                  checked={useMock}
                  onChange={(e) => setUseMock(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-800 bg-slate-950 text-teal-600 focus:ring-teal-500"
                />
              </div>

              {/* System Metadata Readonly */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">System Information</p>
                <div className="rounded-xl bg-slate-950 p-3 space-y-1 text-xs text-slate-400 font-mono">
                  <p>Database: <span className="text-slate-200">sentinelai_db (PostgreSQL)</span></p>
                  <p>Model Backend: <span className="text-slate-200">Isolation Forest (joblib)</span></p>
                  <p>RAG Vectors: <span className="text-slate-200">ChromaDB collection active</span></p>
                  <p>Default LLM: <span className="text-teal-400">gemini-3.5-flash</span></p>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="btn btn-outline border-slate-800 text-slate-400 hover:text-white px-4 py-2 text-xs"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setApiBase(tempApiBase);
                  localStorage.setItem("apiBaseUrl", tempApiBase);
                  setIsSettingsOpen(false);
                  showToast("Settings saved successfully!");
                }}
                className="btn bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 text-white font-bold px-4 py-2 text-xs rounded-lg"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Manager */}
      <div className="fixed bottom-5 right-5 z-50 space-y-2 pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`glassmorphism px-4 py-3 rounded-xl border flex items-center gap-2.5 text-xs font-semibold shadow-2xl pointer-events-auto animate-fade-in ${
              t.type === "error"
                ? "border-rose-500/30 bg-rose-950/20 text-rose-300"
                : "border-teal-500/30 bg-teal-950/20 text-teal-300"
            }`}
          >
            {t.type === "error" ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
            <span>{t.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((item) => item.id !== t.id))}
              className="ml-2 hover:text-white"
            >
              <X size={12} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// DASHBOARD PAGE
// ═══════════════════════════════════════════════════════════════════════
function DashboardPage({
  cumulativeStats,
  result,
  pipeline,
  isLoading,
  error,
  setError,
  selectedFile,
  fileInputRef,
  handleFileChange,
  handleInvestigate,
  getImpactBadge,
  isDragging,
  onDragOver,
  onDragLeave,
  onDrop,
}) {
  return (
    <>
      {/* Header */}
      <header className="flex items-center justify-between mb-8 pb-6 border-b border-slate-900">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Security Command Center</h2>
          <p className="mt-1 text-sm text-slate-400">
            Upload raw system logs, detect real-time anomalies, and perform AI-driven root cause investigations.
          </p>
        </div>
        <div className="flex items-center gap-3 rounded-full border border-teal-500/20 bg-teal-950/20 px-4 py-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500" />
          </span>
          <span className="text-xs font-semibold tracking-wide text-teal-400 uppercase">System Active</span>
        </div>
      </header>

      {/* Cumulative Stats (from DB) */}
      <div className="mb-8 grid gap-6 md:grid-cols-3">
        <StatCard
          title="Total Parsed Events"
          value={Number(cumulativeStats.total_parsed_events).toLocaleString()}
          icon={<FileCode size={20} />}
          gradient="from-blue-500/10 to-teal-500/5 border-blue-500/20 text-blue-400"
        />
        <StatCard
          title="Total Anomalies Found"
          value={cumulativeStats.total_anomalies}
          icon={<AlertTriangle size={20} />}
          gradient={
            cumulativeStats.total_anomalies > 0
              ? "from-rose-500/10 to-amber-500/5 border-rose-500/30 text-rose-400 glow-rose"
              : "from-slate-900 to-slate-950 border-slate-900 text-slate-400"
          }
        />
        <StatCard
          title="Total Investigations"
          value={cumulativeStats.total_runs}
          icon={<Search size={20} />}
          gradient="from-purple-500/10 to-indigo-500/5 border-purple-500/20 text-purple-400"
        />
      </div>

      {/* Drag and Drop Action Card */}
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={`glassmorphism p-8 mb-8 text-center relative overflow-hidden transition-all duration-300 border shadow-xl ${
          isDragging
            ? "border-teal-400 bg-teal-950/10 scale-[1.01] glow-teal"
            : "border-slate-800 hover:border-slate-700"
        }`}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-teal-500/5 to-transparent pointer-events-none" />
        <UploadCloud
          size={48}
          className={`mx-auto mb-4 transition-transform duration-200 ${
            isDragging ? "text-teal-400 scale-110" : "text-teal-400"
          }`}
        />
        <h3 className="text-xl font-bold text-white mb-2">Ingest & Investigate System Logs</h3>
        <p className="text-sm text-slate-400 max-w-lg mx-auto mb-6">
          {isDragging
            ? "Drop the log file here to load it!"
            : "Drag & drop log files here, or click standard upload to select file manually."}
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".log,.txt"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="flex flex-col items-center justify-center gap-4">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn btn-outline border-slate-700 text-slate-300 hover:bg-slate-900/60 hover:text-white px-6 py-2.5 rounded-xl font-semibold flex items-center gap-2"
          >
            Choose Log File
          </button>
          {selectedFile && (
            <div className="mt-4 p-4 rounded-xl border border-teal-500/20 bg-teal-950/10 max-w-md w-full animate-fade-in">
              <p className="text-sm font-medium text-slate-300 break-all mb-3 flex items-center justify-center gap-2">
                <FileCode size={16} className="text-teal-400" />
                Selected: {selectedFile.name}
              </p>
              <button
                onClick={handleInvestigate}
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 text-white font-bold py-3 px-6 rounded-xl shadow-lg shadow-teal-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Activity size={18} className="animate-spin" />
                    Running Detection Pipeline...
                  </>
                ) : (
                  <>
                    <Zap size={18} />
                    Run AI Investigation
                  </>
                )}
              </button>
            </div>
          )}
        </div>
        {error && (
          <div className="mt-6 max-w-xl mx-auto">
            <ErrorBanner message={error} onClose={() => setError(null)} />
          </div>
        )}
        <p className="mt-4 text-xs text-slate-500">Supported formats: .log, .txt</p>
      </div>

      {/* Running pipeline details loader */}
      {isLoading && (
        <div className="glassmorphism border border-teal-500/20 bg-teal-500/5 p-6 mb-8 animate-pulse">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-500/10 text-teal-400">
              <Activity size={24} className="animate-pulse" />
            </div>
            <div>
              <h3 className="font-bold text-white text-lg">AI Pipeline executing...</h3>
              <p className="text-sm text-slate-400 mt-1">
                Ingesting log blocks ➔ Feature modeling ➔ Vector similarity search ➔ LLM Root Cause generation.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Results Panel */}
      {result && (
        <div className="space-y-8 animate-fade-in">
          {/* Pipeline summary card */}
          <div className="glassmorphism p-6 border-slate-800">
            <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center pb-4 border-b border-slate-900">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">Investigation Success</h3>
                  <p className="text-xs text-slate-400">Analysis results for {result.filename}</p>
                </div>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-2 text-xs font-mono text-slate-400">
                RUN_ID: <span className="text-teal-400 font-semibold">{result.analysis_run_id}</span>
              </div>
            </div>
            <div className="mt-6 grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
              <ResultItem label="Total Lines" value={pipeline?.total_lines ?? 0} />
              <ResultItem label="Parsed Events" value={pipeline?.parsed_events ?? 0} />
              <ResultItem label="Skipped Lines" value={pipeline?.skipped_lines ?? 0} />
              <ResultItem label="Feature Windows" value={pipeline?.feature_windows ?? 0} />
              <ResultItem label="Anomalies Found" value={pipeline?.anomalies_detected ?? 0} />
              <ResultItem
                label="Execution Time"
                value={
                  pipeline?.total_pipeline_time_seconds != null
                    ? `${pipeline.total_pipeline_time_seconds}s`
                    : "N/A"
                }
              />
            </div>
          </div>

          {/* Anomaly Dashboard Charts */}
          {result.analysis?.anomalies?.length > 0 && (
            <div className="grid gap-6 md:grid-cols-2">
              <AnomalyDistributionChart anomalies={result.analysis.anomalies} />
              <ServiceBreakdownChart anomalies={result.analysis.anomalies} />
            </div>
          )}

          {/* RAG Knowledge Base retrieve findings */}
          {result.analysis?.summary && (
            <div className="glassmorphism p-6 border-slate-800">
              <h3 className="flex items-center gap-2 text-lg font-bold text-white mb-4">
                <Search size={20} className="text-blue-400" />
                Knowledge Base Retrieval & Findings
              </h3>
              <div className="grid gap-4 md:grid-cols-3 mb-6">
                <ResultItem label="Anomalies Investigated" value={result.analysis.summary.anomalies_detected ?? 0} />
                <ResultItem label="RAG Evidence Chunks" value={result.analysis.summary.total_evidence_chunks ?? 0} />
                <ResultItem label="Impacted Host Services" value={result.analysis.summary.affected_services?.length ?? 0} />
              </div>
              {result.analysis.summary.affected_services?.length > 0 && (
                <div className="border-t border-slate-900 pt-4">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Affected Services</p>
                  <div className="flex flex-wrap gap-2">
                    {result.analysis.summary.affected_services.map((s) => (
                      <span
                        key={s}
                        className="rounded-full border border-red-500/20 bg-red-500/5 px-3 py-1 text-xs font-semibold text-red-400 glow-red"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Assessment */}
          {result.evaluation && (
            <div className="glassmorphism p-6 border-slate-800">
              <h3 className="flex items-center gap-2 text-lg font-bold text-white mb-4">
                <AlertTriangle size={20} className="text-amber-400" /> Incident Assessment
              </h3>
              <div className="grid gap-4 md:grid-cols-3 mb-6">
                <ResultItem
                  label="Impact Score"
                  value={
                    <span className={`px-2.5 py-0.5 rounded-full border text-sm font-bold ${getImpactBadge(result.evaluation.impact)}`}>
                      {formatText(result.evaluation.impact)}
                    </span>
                  }
                />
                <ResultItem
                  label="Severity"
                  value={
                    <span className={`px-2.5 py-0.5 rounded-full border text-sm font-bold ${getImpactBadge(result.evaluation.service_impact)}`}>
                      {formatText(result.evaluation.service_impact)}
                    </span>
                  }
                />
                <ResultItem label="Pattern Reoccurrence" value={formatText(result.evaluation.historical_pattern)} />
              </div>
            </div>
          )}

          {/* AI Report Card */}
          {result.investigation_report && (
            <div className="glow-shadow">
              <ReportCard report={result.investigation_report} />
            </div>
          )}

          {/* Anomaly Details */}
          {result.analysis?.anomalies?.length > 0 && (
            <div className="glassmorphism p-6 border-slate-800">
              <h3 className="flex items-center gap-2 text-lg font-bold text-white mb-4">
                <Activity size={20} className="text-rose-400" /> Investigated Anomalies
              </h3>
              <div className="space-y-4">
                {result.analysis.anomalies.map((anomaly, index) => (
                  <div
                    key={`${anomaly.service}-${index}`}
                    className="rounded-xl border border-slate-800/80 bg-slate-950/40 hover:bg-slate-950/80 transition-all p-5 flex flex-col justify-between gap-4 md:flex-row border-l-4 border-l-rose-500"
                  >
                    <div>
                      <div className="flex items-center gap-3">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-rose-500/10 text-xs font-bold text-rose-400 border border-rose-500/20">
                          {index + 1}
                        </span>
                        <h4 className="font-bold text-white">{anomaly.service}</h4>
                      </div>
                      <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-400">
                        <span className="flex items-center gap-1.5">
                          <Clock size={14} className="text-slate-500" />
                          {formatDate(anomaly.window_start)} ➔ {formatDate(anomaly.window_end)}
                        </span>
                        <span>
                          Events: <span className="text-slate-200 font-semibold">{anomaly.total_events}</span>
                        </span>
                      </div>
                    </div>
                    <div className="rounded-xl border border-slate-900 bg-slate-950 px-4 py-3 flex flex-col justify-center items-end min-w-[120px]">
                      <p className="text-[10px] uppercase font-semibold tracking-wider text-slate-500">Anomaly Weight</p>
                      <p className="mt-1 font-mono font-bold text-rose-400 text-lg">{anomaly.anomaly_score?.toFixed(5)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// INVESTIGATIONS PAGE
// ═══════════════════════════════════════════════════════════════════════
function InvestigationsPage({ historyRuns, historyLoading, selectedRun, setSelectedRun, fetchRunDetail }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");

  const filteredRuns = historyRuns.filter((run) => {
    const matchesSearch = run.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filterType === "all"
        ? true
        : filterType === "anomalies"
        ? run.anomalies_detected > 0
        : run.anomalies_detected === 0;
    return matchesSearch && matchesFilter;
  });

  if (selectedRun) {
    return (
      <div className="animate-fade-in">
        <button
          onClick={() => setSelectedRun(null)}
          className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition mb-6"
        >
          <ArrowLeft size={16} />
          Back to Investigations
        </button>

        <header className="mb-8 pb-6 border-b border-slate-900">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
              <Database size={20} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">
                Run #{selectedRun.id} — {selectedRun.filename}
              </h2>
              <p className="text-xs text-slate-400 mt-1">{formatDate(selectedRun.created_at)}</p>
            </div>
          </div>
        </header>

        {/* Run Stats */}
        <div className="grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-6 mb-8">
          <ResultItem label="Total Lines" value={selectedRun.total_lines} />
          <ResultItem label="Parsed Events" value={selectedRun.parsed_events} />
          <ResultItem label="Skipped Lines" value={selectedRun.skipped_lines} />
          <ResultItem label="Feature Windows" value={selectedRun.feature_windows} />
          <ResultItem label="Anomalies" value={selectedRun.anomalies_detected} />
          <ResultItem label="Timestamp" value={timeAgo(selectedRun.created_at)} />
        </div>

        {/* Anomaly Results List */}
        {selectedRun.anomaly_results?.length > 0 && (
          <div className="glassmorphism p-6 border-slate-800">
            <h3 className="flex items-center gap-2 text-lg font-bold text-white mb-4">
              <Activity size={20} className="text-rose-400" /> Anomaly Results (
              {selectedRun.anomaly_results.filter((r) => r.is_anomaly).length} anomalies out of{" "}
              {selectedRun.anomaly_results.length} windows)
            </h3>
            <div className="space-y-3">
              {selectedRun.anomaly_results
                .filter((r) => r.is_anomaly)
                .map((ar, i) => (
                  <div
                    key={ar.id || i}
                    className="rounded-xl border border-slate-800/80 bg-slate-950/40 p-4 flex flex-col md:flex-row justify-between gap-4 border-l-4 border-l-rose-500"
                  >
                    <div>
                      <p className="font-semibold text-white">{ar.service || "Unknown Service"}</p>
                      <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                        <Clock size={12} /> {formatDate(ar.window_start)} ➔ {formatDate(ar.window_end)}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Events: <span className="text-white font-semibold">{ar.total_events}</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] uppercase font-semibold tracking-wider text-slate-500">Score</p>
                      <p className="font-mono font-bold text-rose-400">{ar.anomaly_score?.toFixed(5)}</p>
                    </div>
                  </div>
                ))}
              {selectedRun.anomaly_results.filter((r) => r.is_anomaly).length === 0 && (
                <p className="text-sm text-slate-400 text-center py-8">No anomalies were detected in this run.</p>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8 pb-6 border-b border-slate-900">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Investigation History</h2>
          <p className="mt-1 text-sm text-slate-400">
            View past logs and anomalies. Click any run to review details.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
          <Database size={14} />
          <span>PostgreSQL · sentinelai_db</span>
        </div>
      </header>

      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
          <input
            type="text"
            placeholder="Search by filename..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-800 bg-slate-950/60 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-teal-500 transition"
          />
        </div>
        
        <div className="flex items-center gap-2 min-w-[200px]">
          <Filter size={15} className="text-slate-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-xl text-xs py-2 px-3 text-slate-200 focus:outline-none focus:border-teal-500"
          >
            <option value="all">All Runs</option>
            <option value="anomalies">Anomalies Detected</option>
            <option value="clean">Clean Runs</option>
          </select>
        </div>
      </div>

      {historyLoading && (
        <div className="text-center py-16">
          <Activity size={32} className="mx-auto text-teal-400 animate-spin mb-4" />
          <p className="text-slate-400">Loading history...</p>
        </div>
      )}

      {!historyLoading && filteredRuns.length === 0 && (
        <div className="glassmorphism p-12 text-center border-slate-800">
          <History size={48} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-white">No matching runs</h3>
          <p className="text-sm text-slate-400 mt-2">Adjust your query or search query to find past analysis records.</p>
        </div>
      )}

      {!historyLoading && filteredRuns.length > 0 && (
        <div className="space-y-3">
          {filteredRuns.map((run) => (
            <button
              key={run.id}
              onClick={() => fetchRunDetail(run.id)}
              className="w-full text-left glassmorphism p-5 border-slate-800 hover:border-teal-500/30 transition-all duration-200 flex items-center justify-between group"
            >
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800 text-slate-300 font-mono font-bold text-sm border border-slate-700 group-hover:border-teal-500/30 group-hover:bg-teal-500/10 group-hover:text-teal-400 transition-all">
                  #{run.id}
                </div>
                <div>
                  <p className="font-semibold text-white group-hover:text-teal-300 transition">{run.filename}</p>
                  <p className="text-xs text-slate-400 mt-1 flex items-center gap-3">
                    <span>{formatDate(run.created_at)}</span>
                    <span>·</span>
                    <span>{run.parsed_events.toLocaleString()} events</span>
                    <span>·</span>
                    <span className={run.anomalies_detected > 0 ? "text-rose-400 font-semibold" : "text-emerald-400"}>
                      {run.anomalies_detected} anomalies
                    </span>
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-500">{timeAgo(run.created_at)}</span>
                <ChevronRight size={18} className="text-slate-600 group-hover:text-teal-400 transition" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// SYSTEM ACTIVITY PAGE
// ═══════════════════════════════════════════════════════════════════════
function SystemActivityPage({ historyRuns, historyLoading }) {
  const timeline = historyRuns.map((run) => ({
    id: run.id,
    type: run.anomalies_detected > 0 ? "anomaly" : "clean",
    title: `Investigation #${run.id}`,
    description: `${run.filename} — ${run.parsed_events} events parsed, ${run.anomalies_detected} anomalies detected`,
    timestamp: run.created_at,
  }));

  return (
    <div className="animate-fade-in">
      <header className="flex items-center justify-between mb-8 pb-6 border-b border-slate-900">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">System Activity</h2>
          <p className="mt-1 text-sm text-slate-400">
            Real-time feed of all pipeline executions and anomaly detection events.
          </p>
        </div>
      </header>

      {historyLoading && (
        <div className="text-center py-16">
          <Activity size={32} className="mx-auto text-teal-400 animate-spin mb-4" />
          <p className="text-slate-400">Loading activity...</p>
        </div>
      )}

      {!historyLoading && timeline.length === 0 && (
        <div className="glassmorphism p-12 text-center border-slate-800">
          <Activity size={48} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-white">No activity recorded</h3>
          <p className="text-sm text-slate-400 mt-2">System activity will appear here after your first investigation.</p>
        </div>
      )}

      {!historyLoading && timeline.length > 0 && (
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-px bg-slate-800" />
          <div className="space-y-6">
            {timeline.map((event) => (
              <div key={event.id} className="relative flex gap-6 pl-2">
                <div
                  className={`relative z-10 mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border ${
                    event.type === "anomaly"
                      ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                      : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                  }`}
                >
                  {event.type === "anomaly" ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
                </div>

                <div className="glassmorphism p-5 border-slate-800 flex-1 hover:border-slate-700 transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{event.title}</h4>
                    <span className="text-xs text-slate-500">{timeAgo(event.timestamp)}</span>
                  </div>
                  <p className="text-sm text-slate-400">{event.description}</p>
                  <p className="text-xs text-slate-500 mt-2">{formatDate(event.timestamp)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════
// SHARED COMPONENTS
// ═══════════════════════════════════════════════════════════════════════
function StatCard({ title, value, icon, gradient }) {
  return (
    <div
      className={`rounded-2xl border bg-gradient-to-tr p-6 shadow-xl transition-all duration-300 hover:-translate-y-1 ${gradient}`}
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className="opacity-80">{icon}</div>
      </div>
      <p className="text-3xl font-extrabold tracking-tight text-white">{value}</p>
    </div>
  );
}

function ResultItem({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-900/60 bg-slate-950/60 p-4">
      <p className="text-[10px] uppercase font-semibold tracking-wider text-slate-500 mb-1">{label}</p>
      <div className="break-words text-sm font-bold text-slate-200">{value}</div>
    </div>
  );
}

export default App;