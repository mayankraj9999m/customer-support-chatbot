import React, { useState, useEffect, useRef } from 'react';
import './ChatbotWidget.css';
import { MessageCircle, X, Send } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: "Hi! I'm your customer support AI. How can I help you today?" }
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    let id = localStorage.getItem('chat_session_id');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('chat_session_id', id);
    }
    setSessionId(id);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  const sendMessage = async (userMsg) => {
    if (!userMsg.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMsg
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I'm having trouble connecting right now." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const msg = input.trim();
    setInput('');
    await sendMessage(msg);
  };

  const handleOptionClick = (optionText) => {
    sendMessage(optionText);
  };

  const renderMessageContent = (text) => {
    return text.split('\n').map((line, lineIdx) => {
      const parts = line.split(/(\[[^\]]+\])/g);
      return (
        <React.Fragment key={lineIdx}>
          {parts.map((part, i) => {
            if (part.startsWith('[') && part.endsWith(']')) {
              const optionText = part.slice(1, -1);
              return (
                <button 
                  key={i} 
                  className="chat-option-btn" 
                  onClick={() => handleOptionClick(optionText)}
                >
                  {optionText}
                </button>
              );
            }
            return <span key={i}>{part}</span>;
          })}
          <br/>
        </React.Fragment>
      );
    });
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button 
          className="chatbot-fab" 
          onClick={() => setIsOpen(true)}
          aria-label="Open Chat"
        >
          <MessageCircle size={28} />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div>
              <h3 className="body-strong" style={{ color: 'var(--on-primary)' }}>Customer Support</h3>
              <p className="caption-sm" style={{ color: 'var(--on-primary)', opacity: 0.8 }}>Online</p>
            </div>
            <button className="chatbot-close-btn" onClick={() => setIsOpen(false)}>
              <X size={20} />
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                {renderMessageContent(msg.text)}
              </div>
            ))}
            {isLoading && (
              <div className="chat-message bot-message">
                <span className="typing-indicator">...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-area" onSubmit={handleSend}>
            <input 
              type="text" 
              placeholder="Type your message..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()}>
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
