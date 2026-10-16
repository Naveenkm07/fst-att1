import React, { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../api";

export default function ChatPanel({ profile, lang, t }) {
  const [messages, setMessages] = useState([
    {
      id: "initial-greeting",
      sender: "bot",
      text: t.chatInitialGreeting,
      sources: ["https://www.myscheme.gov.in"],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    const query = input.trim();
    if (!query || loading) return;

    setError(null);
    const userMsgId = `user-${Date.now()}`;
    const newMessages = [
      ...messages,
      { id: userMsgId, sender: "user", text: query },
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const response = await sendChatMessage(query, profile);
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: response.answer,
        sources: response.sources || [],
        language: response.language,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      setError(
        err.message ||
          "Could not reach the assistant. Please check your backend connection."
      );
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: "bot",
          text:
            lang === "kn"
              ? "ಕ್ಷಮಿಸಿ, ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ಸರ್ವರ್ ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ."
              : "I apologize, but I could not retrieve an answer at this time. Please ensure the backend is running.",
          sources: ["https://www.myscheme.gov.in"],
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="chat-panel" aria-labelledby="chat-heading">
      <div className="chat-header">
        <div className="chat-header-text">
          <h3 id="chat-heading" className="chat-title">
            <span aria-hidden="true">💬</span> {t.chatTitle}
          </h3>
          <p className="chat-subtitle">{t.chatSubtitle}</p>
        </div>
        <div className="chat-notice-pill">
          <span aria-hidden="true">🔒</span>
          <span>{t.chatGroundedNotice}</span>
        </div>
      </div>

      <div className="chat-messages-container" tabIndex={0} aria-live="polite">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-bubble-row ${
              msg.sender === "user" ? "bubble-row-user" : "bubble-row-bot"
            }`}
          >
            <div
              className={`chat-bubble ${
                msg.sender === "user" ? "bubble-user" : "bubble-bot"
              } ${msg.isError ? "bubble-error" : ""}`}
            >
              <div className="bubble-sender-label">
                {msg.sender === "user" ? "Citizen" : "Scheme Bot"}
              </div>
              <p className="bubble-text">{msg.text}</p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="bubble-sources">
                  <span className="sources-label">{t.chatSources}:</span>
                  <div className="sources-list">
                    {msg.sources.map((src, idx) => (
                      <a
                        key={idx}
                        href={src}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-tag"
                      >
                        {new URL(src).hostname} ↗
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-bubble-row bubble-row-bot">
            <div className="chat-bubble bubble-bot bubble-loading">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-text">{t.chatSending}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-inline-error" role="alert">
          <span>⚠️ {error}</span>
        </div>
      )}

      <form onSubmit={handleSend} className="chat-input-bar">
        <label htmlFor="chat-input-field" className="sr-only">
          {t.chatPlaceholder}
        </label>
        <input
          id="chat-input-field"
          type="text"
          className="chat-input"
          placeholder={t.chatPlaceholder}
          value={input}
          maxLength={500}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          autoComplete="off"
        />
        <button
          type="submit"
          className="btn btn-primary btn-send"
          disabled={loading || !input.trim()}
          id="btn-chat-send"
        >
          {t.chatSend}
        </button>
      </form>
    </section>
  );
}
