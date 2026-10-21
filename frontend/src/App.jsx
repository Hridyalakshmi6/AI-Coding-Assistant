import { useState } from "react";
import "./App.css";

const examples = [
  { label: "Python KeyError", value: "KeyError: 'username'" },
  { label: "ZeroDivisionError", value: "ZeroDivisionError: division by zero" },
  { label: "Java NullPointerException", value: "NullPointerException" },
  { label: "Python SyntaxError", value: "SyntaxError: invalid syntax" },
];

/*
function previewExplanation(message) {
  const error = message.toLowerCase();

  if (error.includes("keyerror")) {
    return {
      type: "KeyError",
      description: "Python could not find the requested key in a dictionary.",
      fix: "Check that the key exists and is spelled correctly. Use dictionary.get('username') when an absent key is expected.",
    };
  }

  if (error.includes("zerodivisionerror")) {
    return {
      type: "ZeroDivisionError",
      description: "Your code is attempting to divide a number by zero.",
      fix: "Check the denominator before dividing and handle the case where it equals zero.",
    };
  }

  if (error.includes("nullpointerexception")) {
    return {
      type: "NullPointerException",
      description: "Java is trying to use an object reference that is null.",
      fix: "Check where the object is initialized and verify it is not null before accessing its methods or properties.",
    };
  }

  if (error.includes("syntaxerror")) {
    return {
      type: "SyntaxError",
      description: "The code does not follow the programming language's syntax rules.",
      fix: "Check brackets, quotes, punctuation, and keywords near the reported line.",
    };
  }

  return {
    type: "Error analysis preview",
    description: "DevFlow has received your error message.",
    fix: "Review the traceback, locate the failing line, inspect variable values, and reproduce the issue with a small test.",
  };
}*/

function App() {
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState(null);
  const [notice, setNotice] = useState("");


  async function explainError() {
    if (!errorMessage.trim()) {
      setNotice("Paste an error message first.");
      setResult(null);
      return;
    }

    setNotice("");
    setResult(null);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/explain`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            error_message: errorMessage,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not explain this error.");
      }

      setResult({
        type: data.explanation.match(/Error detected:\s*([^\n]+)/)?.[1] || "MCP analysis",
        description: data.explanation
          .match(/Explanation and fix:\s*([\s\S]*?)(?=\nNext step:|$)/)?.[1]
          || data.explanation,
        fix: data.explanation.match(/Next step:\s*([\s\S]*)/)?.[1]
          || "Review the traceback and test the change.",
      });
    } catch (error) {
      setNotice(
        error.message || "Could not connect to DevFlow. Check that both backend services are running."
      );
    }
  }

  function selectExample(value) {
    setErrorMessage(value);
    setResult(null);
    setNotice("");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#home">
          <span className="brand-mark">D</span>
          <span>DevFlow</span>
        </a>

        <div className="nav-label">WORKSPACE</div>
        <div className="nav-item active">
          <span>⌘</span> Error explainer
        </div>
        <div className="nav-item muted">
          <span>◷</span> Recent analyses
          <span className="soon">Soon</span>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Development mode</strong>
            <p>Local workspace</p>
          </div>
        </div>
      </aside>

      <main className="main-content" id="home">
        <header className="topbar">
          <span className="breadcrumb">Workspace / Error explainer</span>
          <span className="mode-badge">PREVIEW MODE</span>
        </header>

        <section className="hero">
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            YOUR AI DEBUGGING COMPANION
          </div>
          <h1>Errors happen.<br /><span>Let's solve them.</span></h1>
          <p className="hero-copy">
            Paste a programming error, understand what went wrong, and
            get a practical next step to fix it.
          </p>
        </section>

        <section className="workspace">
          <div className="section-heading">
            <div>
              <h2>Analyze an error</h2>
              <p>Start with an error message or a traceback.</p>
            </div>
            <span className="step-label">01 / INPUT</span>
          </div>

          <div className="editor-card">
            <div className="editor-top">
              <div className="window-dots"><i /><i /><i /></div>
              <span>error.log</span>
              <span className="language-label">TEXT</span>
            </div>

            <textarea
              value={errorMessage}
              onChange={(event) => {
                setErrorMessage(event.target.value);
                setNotice("");
              }}
              placeholder={"Paste your error here...\n\nExample: KeyError: 'username'"}
              aria-label="Programming error message"
              spellCheck={false}
            />

            <div className="editor-footer">
              <span>{errorMessage.length} characters</span>
              <button className="clear-button" onClick={() => {
                setErrorMessage("");
                setResult(null);
                setNotice("");
              }}>
                Clear input
              </button>
            </div>
          </div>

          {notice && <p className="notice">{notice}</p>}

          <div className="examples">
            <span>TRY AN EXAMPLE</span>
            {examples.map((example) => (
              <button
                className="example-chip"
                key={example.label}
                onClick={() => selectExample(example.value)}
              >
                {example.label}
              </button>
            ))}
          </div>

          <button className="explain-button" onClick={explainError}>
            Explain this error <span>→</span>
          </button>

          <div className="results-section">
            <div className="section-heading">
              <div>
                <h2>Understanding your error</h2>
                <p>Your explanation and suggested next step will appear here.</p>
              </div>
              <span className="step-label">02 / RESULTS</span>
            </div>

            {result ? (
              <div className="result-card">
                <div className="result-header">
                  <span className="result-icon">!</span>
                  <div>
                    <span className="result-caption">ERROR IDENTIFIED</span>
                    <h3>{result.type}</h3>
                  </div>
                </div>
                <div className="result-block">
                  <h4>What it means</h4>
                  <p>{result.description}</p>
                </div>
                <div className="result-block fix-block">
                  <h4>Suggested fix</h4>
                  <p>{result.fix}</p>
                </div>
                <p className="preview-note">
                  Live result · Generated by the DevFlow MCP server.
                </p>
              </div>
            ) : (
              <div className="empty-result">
                <div className="empty-icon">⌁</div>
                <h3>Your insights will appear here</h3>
                <p>Submit an error above to see an explanation and debugging advice.</p>
              </div>
            )}
          </div>
        </section>

        <footer className="footer">
          <span><span className="status-dot" /> DevFlow workspace</span>
          <span>Built for developers, one error at a time.</span>
        </footer>
      </main>
    </div>
  );
}

export default App;