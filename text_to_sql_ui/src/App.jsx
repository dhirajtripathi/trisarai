import { useState } from 'react';
import SchemaBrowser from './SchemaBrowser';
import ErDiagramView from './ErDiagramView';
import SettingsView from './SettingsView';
import PortalHome from './PortalHome';
import './App.css';

function App() {
    const [dbName, setDbName] = useState('demo_sql');
    const [activeView, setActiveView] = useState('home'); // home | chat | diagram | settings
    const [query, setQuery] = useState('');
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    // Helper: Download CSV
    const downloadCSV = (data) => {
        if (!data || !data.length) return;
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(h => JSON.stringify(row[h])).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'export.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleGenerate = async () => {
        setLoading(true);
        const res = await fetch('/api/mcp/tools/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: "generate_query",
                arguments: {
                    query: query,
                    db_name: dbName,
                    type: dbName.includes('sql') ? 'sql' : 'nosql'
                }
            })
        });
        const data = await res.json();
        const generated = data.content?.[0]?.text; // { query, reasoning, confidence }

        setHistory([...history, { type: 'user', text: query }, { type: 'ai', data: generated }]);
        setQuery('');
        setLoading(false);
    };

    const handleExecute = async (script, index) => {
        const res = await fetch('/api/mcp/tools/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: "execute_query",
                arguments: {
                    script: script,
                    type: dbName.includes('sql') ? 'sql' : 'nosql'
                }
            })
        });
        const data = await res.json();

        const newHistory = [...history];
        newHistory[index].result = data.content?.[0]?.text;
        newHistory[index].isError = data.isError;
        setHistory(newHistory);
    };

    // --- RENDER HELPERS ---

    const renderHeader = () => (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #eee' }}>
            <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => setActiveView('home')}>
                <span style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>🌌</span>
                <h2 style={{ margin: 0, background: 'linear-gradient(45deg, #007bff, #6610f2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Enterprise AI Portal
                </h2>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button onClick={() => setActiveView('home')} style={{ background: 'transparent', color: '#666', border: '1px solid #ddd' }}>🏠 Home</button>
                <button onClick={() => setActiveView('settings')} className={activeView === 'settings' ? 'active' : ''}>⚙️ Settings</button>
            </div>
        </div>
    );

    // --- MAIN RENDER ---

    if (activeView === 'home') {
        return <PortalHome onNavigate={setActiveView} />;
    }

    return (
        <div style={{ display: 'flex', height: '100vh', flexDirection: 'column' }}>
            {/* Top Bar (Navigation) */}
            <div style={{ padding: '0 2rem', borderBottom: '1px solid #ddd', background: 'white' }}>
                {renderHeader()}
            </div>

            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                {/* Sidebar - Only show for Data/Diagram views */}
                {(activeView === 'chat' || activeView === 'diagram') && (
                    <SchemaBrowser dbName={dbName} />
                )}

                {/* Main Content Area */}
                <div style={{ flex: 1, padding: '2rem', overflowY: 'auto', background: '#f8f9fa' }}>

                    {activeView === 'settings' && <SettingsView />}

                    {activeView === 'diagram' && <ErDiagramView dbName={dbName} />}

                    {activeView === 'chat' && (
                        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                            <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem' }}>
                                {history.length === 0 && (
                                    <div style={{ textAlign: 'center', marginTop: '3rem', color: '#aaa' }}>
                                        <h3>👋 Ready to Analyze</h3>
                                        <p>Ask questions about your data in plain English.</p>
                                    </div>
                                )}
                                {history.map((item, i) => (
                                    <div key={i} style={{ marginBottom: '2rem', textAlign: item.type === 'user' ? 'right' : 'left' }}>
                                        {item.type === 'user' ? (
                                            <div style={{ display: 'inline-block', background: '#007bff', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '20px 20px 0 20px', fontSize: '1.1rem' }}>
                                                {item.text}
                                            </div>
                                        ) : (
                                            <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', textAlign: 'left' }}>
                                                <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Thinking Process 🧠</h4>
                                                <div style={{ color: '#666', fontStyle: 'italic', marginBottom: '1rem' }}>"{item.data.reasoning}"</div>

                                                <details style={{ marginBottom: '1rem' }}>
                                                    <summary style={{ cursor: 'pointer', color: '#007bff', fontSize: '0.9rem' }}>Show Technical Details (SQL)</summary>
                                                    <div style={{ fontFamily: 'monospace', background: '#222', color: '#0f0', padding: '0.5rem', marginTop: '0.5rem', borderRadius: '4px' }}>
                                                        {typeof item.data.query === 'object' ? JSON.stringify(item.data.query) : item.data.query}
                                                    </div>
                                                </details>

                                                {!item.result && (
                                                    <button onClick={() => handleExecute(item.data.query, i)} style={{ cursor: 'pointer', padding: '0.75rem 1.5rem', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', fontWeight: 'bold' }}>
                                                        ▶ Run Analysis
                                                    </button>
                                                )}

                                                {item.result && (
                                                    <div style={{ marginTop: '1.5rem' }}>
                                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                                            <strong>Results ({item.result.length || 0} rows)</strong>
                                                            {!item.isError && (
                                                                <button onClick={() => downloadCSV(item.result)} style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem', background: '#6c757d' }}>⬇ CSV</button>
                                                            )}
                                                        </div>

                                                        {item.isError ? (
                                                            <div style={{ color: 'red', background: '#ffe6e6', padding: '1rem' }}>{item.result}</div>
                                                        ) : (
                                                            <div style={{ overflowX: 'auto', border: '1px solid #dee2e6' }}>
                                                                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                                                                    <thead style={{ background: '#e9ecef' }}>
                                                                        <tr>
                                                                            {item.result.length > 0 && Object.keys(item.result[0]).map(k => (
                                                                                <th key={k} style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>{k}</th>
                                                                            ))}
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody>
                                                                        {item.result.map((row, rowI) => (
                                                                            <tr key={rowI} style={{ borderBottom: '1px solid #dee2e6' }}>
                                                                                {Object.values(row).map((val, colI) => (
                                                                                    <td key={colI} style={{ padding: '0.75rem' }}>{val}</td>
                                                                                ))}
                                                                            </tr>
                                                                        ))}
                                                                    </tbody>
                                                                </table>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {loading && <div style={{ color: '#999', fontStyle: 'italic' }}>🤖 Analyzing request...</div>}
                            </div>

                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <input
                                    value={query}
                                    onChange={e => setQuery(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && handleGenerate()}
                                    placeholder="Type your question here (e.g. 'What is the total revenue?')"
                                    style={{ flex: 1, padding: '1.25rem', borderRadius: '8px', border: '1px solid #ccc', fontSize: '1.1rem', boxShadow: '0 2px 5px rgba(0,0,0,0.05)' }}
                                />
                                <button onClick={handleGenerate} disabled={loading} style={{ padding: '0 2rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '1.1rem', fontWeight: 'bold' }}>
                                    Ask
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;
