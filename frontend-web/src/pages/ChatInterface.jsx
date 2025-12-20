import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI learning assistant. Ask me anything about your uploaded documents.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply || data.message }]);
      } else {
        // Fallback/Mock
        setTimeout(() => {
          setMessages(prev => [...prev, { role: 'assistant', content: "This is a great question about Cloud Computing!" }]);
        }, 1000);
      }
    } catch (error) {
      // Fallback/Mock
      setTimeout(() => {
        setMessages(prev => [...prev, { role: 'assistant', content: "To deploy microservices, you often use Docker and Kubernetes." }]);
      }, 1000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      <h1 className="gradient-text" style={{ fontSize: '2rem', marginBottom: '1rem' }}>AI Chat</h1>

      <div style={{
        flex: 1,
        background: 'var(--bg-card)',
        borderRadius: '12px',
        border: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{
              display: 'flex',
              gap: '1rem',
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%'
            }}>
              {msg.role === 'assistant' && (
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Bot size={18} color="white" />
                </div>
              )}
              <div style={{
                background: msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                color: 'white',
                padding: '0.75rem 1rem',
                borderRadius: '12px',
                borderTopLeftRadius: msg.role === 'assistant' ? '4px' : '12px',
                borderTopRightRadius: msg.role === 'user' ? '4px' : '12px',
              }}>
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--bg-dark)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <User size={18} color="var(--text-muted)" />
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '1rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.75rem' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            style={{
              flex: 1,
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              background: 'var(--bg-dark)',
              border: '1px solid var(--border)',
              color: 'white',
              outline: 'none'
            }}
          />
          <button type="submit" disabled={loading} style={{
            background: 'var(--primary)',
            color: 'white',
            border: 'none',
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
