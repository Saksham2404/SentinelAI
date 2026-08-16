import React from "react";

import { Settings, Sun, Moon } from "lucide-react";

function TopNav({ useMock, setUseMock, theme, setTheme, onSettingsClick }) {
  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header className="flex items-center justify-between bg-slate-900 px-6 py-3 border-b border-slate-800">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-white">SentinelAI</h1>
        <span className="text-sm text-slate-400">Incident Intelligence</span>
      </div>
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={useMock}
            onChange={(e) => setUseMock(e.target.checked)}
            className="h-4 w-4 rounded border-gray-600 bg-gray-700 text-blue-600 focus:ring-blue-500"
          />
          Mock Mode
        </label>

        <button
          onClick={toggleTheme}
          className="flex items-center justify-center p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <button
          onClick={onSettingsClick}
          className="flex items-center gap-1 text-slate-400 hover:text-white"
        >
          <Settings size={18} />
          Settings
        </button>
      </div>
    </header>

  );
}

export default TopNav;

