import React from "react";
import { AlertTriangle } from "lucide-react";

/**
 * ErrorBanner – displays an error message in a prominent, styled banner.
 *
 * Props:
 *   - message: string – the error text to show.
 *   - onClose (optional): () => void – callback invoked when the close button is clicked.
 *
 * The component uses the dark‑theme colour palette defined in `theme.css` and
 * applies a subtle glass‑morphism background. It also includes an icon for visual
 * emphasis and a dismiss button.
 */
function ErrorBanner({ message, onClose }) {
  return (
    <div className="error-banner glassmorphism mb-4 flex items-center rounded-lg border border-red-600/30 bg-red-900/30 p-4 text-red-100">
      <AlertTriangle className="mr-2 flex-shrink-0" size={20} />
      <span className="flex-1 break-words text-sm">{message}</span>
      {onClose && (
        <button
          type="button"
          className="ml-3 rounded-full p-1 hover:bg-red-800/50"
          onClick={onClose}
          aria-label="Dismiss error"
        >
          ✕
        </button>
      )}
    </div>
  );
}

export default ErrorBanner;
