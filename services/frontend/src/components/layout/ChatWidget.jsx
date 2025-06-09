import React, { useState } from "react";
import "./ChatWidget.css";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: "You", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const response = await fetch("http://localhost:8008/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userMessage.text }),
    });

    const data = await response.json();
    const botMessage = { sender: "QuantAI", text: data.answer };
    setMessages((prev) => [...prev, botMessage]);
  };

  return (
    <div className="chat-widget-container">
      {open && (
        <div className="chatbox">
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-msg ${msg.sender === "You" ? "user" : "bot"}`}>
                <strong>{msg.sender}:</strong> {msg.text}
              </div>
            ))}
          </div>
          <div className="chat-input">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask something..."
            />
            <button onClick={sendMessage}>➤</button>
          </div>
        </div>
      )}
      <button className="chat-toggle" onClick={() => setOpen(!open)}>
        🪙 
      </button>
    </div>
  );
}