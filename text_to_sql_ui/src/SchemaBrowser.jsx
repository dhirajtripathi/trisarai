import { useState, useEffect } from 'react';

export default function SchemaBrowser({ dbName }) {
    const [schema, setSchema] = useState(null);

    useEffect(() => {
        // Always fetch 'demo_sql' which is mapped to the 'Active SQL DB' in the backend
        // In the future, we could have an API that returns the actual connected DB Name
        fetch('/api/mcp/tools/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: "get_schema",
                arguments: { db_name: "demo_sql" }
            })
        })
            .then(res => res.json())
            .then(data => {
                const schemaData = data.content?.[0]?.text;
                setSchema(schemaData);
            })
            .catch(err => console.error(err));
    }, [dbName]); // Reload if dbName prop changes (e.g. after config update)

    return (
        <div style={{ padding: '1rem', borderRight: '1px solid #ccc', height: '100vh', width: '250px', background: '#f8f9fa' }}>
            <h3 style={{ borderBottom: '1px solid #ddd', paddingBottom: '1rem' }}>🗄️ Active Schema</h3>

            {schema ? (
                <div style={{ fontSize: '0.9rem', overflowY: 'auto', height: 'calc(100vh - 100px)' }}>
                    {schema.tables?.length === 0 && <div>No tables found.</div>}

                    {schema.tables?.map(t => (
                        <div key={t.name} style={{ marginBottom: '1rem' }}>
                            <div style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                                <span style={{ marginRight: '0.5rem' }}>📄</span> {t.name}
                            </div>
                            {t.description && <div style={{ fontSize: '0.8em', color: '#666', fontStyle: 'italic', marginLeft: '1.2rem' }}>{t.description}</div>}

                            <ul style={{ paddingLeft: '1.2rem', margin: '0.25rem 0', color: '#555' }}>
                                {t.columns?.map(c => (
                                    <li key={c.name} style={{ marginBottom: '0.2rem' }}>
                                        {c.name} <span style={{ fontSize: '0.7em', color: '#999' }}>({c.type})</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                    {schema.collections?.map(c => (
                        <div key={c} style={{ marginBottom: '0.5rem' }}>
                            <strong>📦 {c}</strong> (Collection)
                        </div>
                    ))}
                </div>
            ) : (
                <div style={{ color: '#666', fontStyle: 'italic' }}>Waiting for connection...</div>
            )}
        </div>
    );
}
