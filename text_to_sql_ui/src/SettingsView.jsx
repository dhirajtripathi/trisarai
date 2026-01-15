import { useState, useEffect } from 'react';

export default function SettingsView() {
    const [config, setConfig] = useState({
        llm_model: 'mock',
        database_url: '',
        api_keys: {}
    });
    const [status, setStatus] = useState('');
    const [connectionStatus, setConnectionStatus] = useState('');

    useEffect(() => {
        fetch('/api/mcp/config')
            .then(res => res.json())
            .then(data => {
                setConfig(prev => ({
                    ...prev,
                    llm_model: data.llm_model,
                    database_url: data.database_url
                }));
            });
    }, []);

    const handleChange = (field, value) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };

    const handleKeyChange = (key, value) => {
        setConfig(prev => ({
            ...prev,
            api_keys: { ...prev.api_keys, [key]: value }
        }));
    };

    const handleSave = async () => {
        setStatus('Saving...');
        await fetch('/api/mcp/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        setStatus('✅ Configuration Saved & Reloaded');
        setTimeout(() => setStatus(''), 3000);
    };

    const handleTest = async () => {
        setConnectionStatus('Testing...');
        const res = await fetch('/api/mcp/config/test', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'ok') {
            setConnectionStatus('✅ Database Connected!');
        } else {
            setConnectionStatus(`❌ Error: ${data.message}`);
        }
    };

    return (
        <div style={{ padding: '2rem', height: '100%', overflow: 'auto', maxWidth: '800px', margin: '0 auto' }}>
            <h2>⚙️ System Configuration (Demo Mode)</h2>
            <p style={{ color: '#666', marginBottom: '2rem' }}>Configure LLM and Database connections on the fly.</p>

            <div style={{ marginBottom: '2rem', padding: '1.5rem', border: '1px solid #ddd', borderRadius: '8px', background: 'white' }}>
                <h3>🧠 LLM Intelligence</h3>

                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Model Provider</label>
                <select
                    value={config.llm_model}
                    onChange={e => handleChange('llm_model', e.target.value)}
                    style={{ width: '100%', padding: '0.75rem', marginBottom: '1rem' }}
                >
                    <option value="mock">🧪 Mock (Heuristics)</option>
                    <option value="gpt-4o">OpenAI (gpt-4o)</option>
                    <option value="azure/gpt-4">Azure OpenAI</option>
                    <option value="bedrock/anthropic.claude-3-sonnet">AWS Bedrock (Claude 3)</option>
                    <option value="gemini/gemini-1.5-pro">Google Gemini 1.5</option>
                </select>

                {config.llm_model !== 'mock' && (
                    <div style={{ background: '#f8f9fa', padding: '1rem', borderRadius: '4px' }}>
                        {config.llm_model.includes('azure') && <>
                            <input
                                placeholder="AZURE_API_KEY"
                                onChange={e => handleKeyChange('AZURE_API_KEY', e.target.value)}
                                style={inputStyle} type="password"
                            />
                            <input
                                placeholder="AZURE_API_BASE (https://...)"
                                onChange={e => handleKeyChange('AZURE_API_BASE', e.target.value)}
                                style={inputStyle}
                            />
                            <input
                                placeholder="AZURE_API_VERSION (2024-02-15-preview)"
                                onChange={e => handleKeyChange('AZURE_API_VERSION', e.target.value)}
                                style={inputStyle}
                            />
                        </>}

                        {config.llm_model.includes('gpt') && !config.llm_model.includes('azure') && (
                            <input
                                placeholder="OPENAI_API_KEY"
                                onChange={e => handleKeyChange('OPENAI_API_KEY', e.target.value)}
                                style={inputStyle} type="password"
                            />
                        )}

                        {config.llm_model.includes('bedrock') && <>
                            <input
                                placeholder="AWS_ACCESS_KEY_ID"
                                onChange={e => handleKeyChange('AWS_ACCESS_KEY_ID', e.target.value)}
                                style={inputStyle}
                            />
                            <input
                                placeholder="AWS_SECRET_ACCESS_KEY"
                                onChange={e => handleKeyChange('AWS_SECRET_ACCESS_KEY', e.target.value)}
                                style={inputStyle} type="password"
                            />
                            <input
                                placeholder="AWS_REGION_NAME"
                                onChange={e => handleKeyChange('AWS_REGION_NAME', e.target.value)}
                                style={inputStyle}
                            />
                        </>}

                        {config.llm_model.includes('gemini') && (
                            <input
                                placeholder="GEMINI_API_KEY"
                                onChange={e => handleKeyChange('GEMINI_API_KEY', e.target.value)}
                                style={inputStyle} type="password"
                            />
                        )}
                    </div>
                )}
            </div>

            <div style={{ marginBottom: '2rem', padding: '1.5rem', border: '1px solid #ddd', borderRadius: '8px', background: 'white' }}>
                <h3>🔌 Database Connection</h3>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Connection String (SQLAlchemy format)</label>
                <input
                    placeholder="postgresql://user:pass@localhost:5432/mydb"
                    value={config.database_url}
                    onChange={e => handleChange('database_url', e.target.value)}
                    style={inputStyle}
                />
                <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
                    Leave empty to use internal Mock DB.
                </div>
                <div style={{ marginTop: '1rem' }}>
                    <button onClick={handleTest} style={{ background: '#6c757d', color: 'white', marginRight: '1rem' }}>Test Connection</button>
                    <span>{connectionStatus}</span>
                </div>
            </div>

            <button onClick={handleSave} style={{ width: '100%', background: '#007bff', color: 'white', padding: '1rem', fontSize: '1.1rem' }}>
                💾 Save Configuration
            </button>
            <div style={{ textAlign: 'center', marginTop: '1rem', color: 'green', fontWeight: 'bold' }}>{status}</div>
        </div>
    );
}

const inputStyle = {
    width: '100%',
    padding: '0.75rem',
    marginBottom: '0.5rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    boxSizing: 'border-box'
};
