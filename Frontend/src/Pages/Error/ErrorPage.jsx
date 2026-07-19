import React, { useEffect, useState } from 'react';
import './ErrorPage.css';

const ErrorPage = ({ message, code, onRetry }) => {
  const [glitch, setGlitch] = useState(false);

  useEffect(() => {
    // Trigger glitch effect periodically
    const interval = setInterval(() => {
      setGlitch(true);
      setTimeout(() => setGlitch(false), 300);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="error-container">
      {/* Animated neural grid background */}
      <div className="neural-grid" />
      
      {/* Floating particles */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 6}s`,
              animationDuration: `${4 + Math.random() * 6}s`,
              width: `${2 + Math.random() * 4}px`,
              height: `${2 + Math.random() * 4}px`,
            }}
          />
        ))}
      </div>

      {/* Glowing orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Main card */}
      <div className={`error-card ${glitch ? 'glitch-active' : ''}`}>
        {/* Card top accent line */}
        <div className="card-accent" />

        {/* Brain/Neural icon */}
        <div className="icon-wrapper">
          <div className="brain-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Outer brain shape */}
              <path
                d="M50 15C35 15 20 25 20 40C20 48 24 55 30 59C28 63 27 67 28 71C29 76 33 80 38 82C42 83 46 82 50 80C54 82 58 83 62 82C67 80 71 76 72 71C73 67 72 63 70 59C76 55 80 48 80 40C80 25 65 15 50 15Z"
                stroke="url(#brainGradient)"
                strokeWidth="2.5"
                fill="none"
                className="brain-path"
              />
              {/* Neural nodes */}
              <circle cx="35" cy="45" r="2.5" fill="#a78bfa" className="node node-1" />
              <circle cx="50" cy="35" r="2.5" fill="#c4b5fd" className="node node-2" />
              <circle cx="65" cy="45" r="2.5" fill="#a78bfa" className="node node-3" />
              <circle cx="40" cy="60" r="2" fill="#8b5cf6" className="node node-4" />
              <circle cx="60" cy="60" r="2" fill="#8b5cf6" className="node node-5" />
              <circle cx="50" cy="52" r="3" fill="#ddd6fe" className="node node-center" />
              {/* Connection lines */}
              <line x1="35" y1="45" x2="50" y2="35" stroke="#6d28d9" strokeWidth="0.8" opacity="0.6" className="conn-line" />
              <line x1="50" y1="35" x2="65" y2="45" stroke="#6d28d9" strokeWidth="0.8" opacity="0.6" className="conn-line" />
              <line x1="35" y1="45" x2="40" y2="60" stroke="#7c3aed" strokeWidth="0.8" opacity="0.5" className="conn-line" />
              <line x1="65" y1="45" x2="60" y2="60" stroke="#7c3aed" strokeWidth="0.8" opacity="0.5" className="conn-line" />
              <line x1="40" y1="60" x2="50" y2="52" stroke="#8b5cf6" strokeWidth="0.8" opacity="0.6" className="conn-line" />
              <line x1="60" y1="60" x2="50" y2="52" stroke="#8b5cf6" strokeWidth="0.8" opacity="0.6" className="conn-line" />
              <line x1="50" y1="35" x2="50" y2="52" stroke="#a78bfa" strokeWidth="1" opacity="0.7" className="conn-line" />
              {/* Error X inside brain */}
              <g className="error-x-group">
                <line x1="42" y1="48" x2="58" y2="62" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" opacity="0.9" />
                <line x1="58" y1="48" x2="42" y2="62" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" opacity="0.9" />
              </g>
              {/* Gradient definition */}
              <defs>
                <linearGradient id="brainGradient" x1="20" y1="15" x2="80" y2="85">
                  <stop stopColor="#8b5cf6" />
                  <stop offset="0.5" stopColor="#a78bfa" />
                  <stop offset="1" stopColor="#c4b5fd" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>

        {/* Error code badge */}
        {code && (
          <div className="error-code-badge">
            <span className="code-dot" />
            ERROR {code}
          </div>
        )}

        {/* Main heading */}
        <h1 className="error-heading">
          <span className="heading-glitch" data-text="SYSTEM_MALFUNCTION">
            NEURAL_SYNC_FAILED
          </span>
        </h1>

        {/* Divider */}
        <div className="divider">
          <span className="divider-diamond" />
          <span className="divider-line" />
          <span className="divider-diamond" />
        </div>

        {/* Error message */}
        <div className="message-container">
          <div className="message-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <p className="error-message">{message || 'An unexpected error occurred in the neural proctoring system.'}</p>
        </div>

        {/* Diagnostic info */}
        <div className="diagnostic-box">
          <div className="diag-header">
            <span className="diag-dot diag-dot-red" />
            <span className="diag-dot diag-dot-yellow" />
            <span className="diag-dot diag-dot-green" />
            <span className="diag-title">diagnostic.log</span>
          </div>
          <div className="diag-body">
            <p><span className="diag-label">TIMESTAMP:</span> {new Date().toISOString()}</p>
            <p><span className="diag-label">SESSION:</span> NEUROPROCTOR_v2.4.1</p>
            <p><span className="diag-label">STATUS:</span> <span className="diag-critical">CRITICAL</span></p>
            <p><span className="diag-label">TRACE_ID:</span> {generateTraceId()}</p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="button-group">
          {onRetry && (
            <button className="btn btn-primary" onClick={onRetry}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <polyline points="1 4 1 10 7 10" />
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
              </svg>
              Retry Connection
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => window.location.reload()}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            Reload System
          </button>
        </div>

        {/* Footer text */}
        <p className="footer-text">
          NeuroProctor — Integrity Engine v2.4.1
        </p>
      </div>
    </div>
  );
};

// Helper to generate a random trace ID
const generateTraceId = () => {
  const hex = '0123456789abcdef';
  let id = '0x';
  for (let i = 0; i < 8; i++) id += hex[Math.floor(Math.random() * 16)];
  return id;
};

export default ErrorPage;