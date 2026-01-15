import { useState, useRef, useEffect } from 'react';

const API_BASE = "http://localhost:8000";

export default function Chat() {
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Hello! I'm your RAG assistant. Ask me anything about your documents." }
    ]);
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
        if (!query.trim()) return;

        const userMsg = { role: "user", content: query };
        setMessages(prev => [...prev, userMsg]);
        setQuery("");
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/tools/call`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: "ask_question",
                    arguments: { query: userMsg.content }
                })
            });

            const data = await res.json();

            let reply = "Something went wrong.";
            if (data.content && data.content[0]) {
                reply = data.content[0].text;
            } else if (data.isError) {
                reply = `Error: ${JSON.stringify(data.content)}`;
            }

            setMessages(prev => [...prev, { role: "assistant", content: reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: "assistant", content: `Network Error: ${err.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role === 'user' ? 'user-msg' : 'assistant-msg'}`}>
                        <div style={{ fontWeight: 600, marginBottom: '0.25rem', fontSize: '0.8rem', opacity: 0.7 }}>
                            {msg.role === 'user' ? 'YOU' : 'ASSISTANT'}
                        </div>
                        <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                    </div>
                ))}
                {loading && <div className="loading">Thinking...</div>}
                <div ref={bottomRef} />
            </div>

            <div className="input-group">
                <input
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    placeholder="Ask a question..."
                    disabled={loading}
                />
                <button className="btn" onClick={handleSend} disabled={loading || !query.trim()}>
                    Send
                </button>
            </div>
        </div>
    );
}
