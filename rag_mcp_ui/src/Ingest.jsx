import { useState } from 'react';

const API_BASE = "http://localhost:8000";

export default function Ingest() {
    const [uploading, setUploading] = useState(false);
    const [logs, setLogs] = useState([]);

    const addLog = (msg) => setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        addLog(`Uploading ${file.name}...`);

        try {
            // 1. Upload to Server
            const formData = new FormData();
            formData.append("file", file);

            const uploadRes = await fetch(`${API_BASE}/api/upload`, {
                method: "POST",
                body: formData
            });

            if (!uploadRes.ok) throw new Error("Upload failed");

            const { file_path } = await uploadRes.json();
            addLog(`File uploaded to ${file_path}. Starting ingestion...`);

            // 2. Call Ingest Tool
            const ingestRes = await fetch(`${API_BASE}/tools/call`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: "ingest_file",
                    arguments: {
                        file_path,
                        metadata: { source: "web-ui" }
                    }
                })
            });

            const ingestData = await ingestRes.json();

            if (ingestData.isError) {
                addLog(`Ingestion Error: ${JSON.stringify(ingestData)}`);
            } else {
                const result = JSON.parse(ingestData.content[0].text);
                addLog(`✅ Success! Doc ID: ${result.document_id} (${result.chunks_count} chunks)`);
            }

        } catch (err) {
            addLog(`❌ Error: ${err.message}`);
        } finally {
            setUploading(false);
            e.target.value = null; // reset input
        }
    };

    return (
        <div style={{ textAlign: 'center' }}>
            <h2>Add Knowledge</h2>
            <p style={{ color: '#666', marginBottom: '2rem' }}>
                Upload PDF or Text files to expand the RAG knowledge base.
            </p>

            <div className="drop-zone" onClick={() => document.getElementById('file-input').click()}>
                <input
                    id="file-input"
                    type="file"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    accept=".pdf,.txt,.md"
                />
                <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📄</div>
                {uploading ? (
                    <div>Processing...</div>
                ) : (
                    <div>
                        <strong>Click to upload</strong> or drag and drop
                    </div>
                )}
            </div>

            {logs.length > 0 && (
                <div style={{ marginTop: '2rem', textAlign: 'left', background: '#f9fafb', padding: '1rem', borderRadius: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#6b7280', marginBottom: '0.5rem' }}>ACTIVITY LOG</div>
                    {logs.map((log, i) => (
                        <div key={i} style={{ fontSize: '0.9rem', marginBottom: '0.25rem' }}>{log}</div>
                    ))}
                </div>
            )}
        </div>
    );
}
