import { useState } from 'react';
import './App.css';
import Chat from './Chat';
import Ingest from './Ingest';

function App() {
    const [tab, setTab] = useState('chat');

    return (
        <div className="container">
            <header>
                <h1>RAG MCP Server</h1>
                <p style={{ marginTop: '0.5rem', color: '#666' }}>Chat with your documents via Model Context Protocol</p>
            </header>

            <div className="tabs">
                <div
                    className={`tab ${tab === 'chat' ? 'active' : ''}`}
                    onClick={() => setTab('chat')}
                >
                    💬 Chat
                </div>
                <div
                    className={`tab ${tab === 'ingest' ? 'active' : ''}`}
                    onClick={() => setTab('ingest')}
                >
                    📄 Add Documents
                </div>
            </div>

            <div className="card">
                {tab === 'chat' ? <Chat /> : <Ingest />}
            </div>
        </div>
    );
}

export default App;
