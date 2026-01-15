import { useState, useEffect } from 'react';

export default function CaseDashboard({ onSelectCase }) {
    const [cases, setCases] = useState([]);
    const [uploading, setUploading] = useState(false);

    const fetchCases = () => {
        fetch('http://localhost:8000/cases')
            .then(res => res.json())
            .then(setCases);
    };

    useEffect(() => {
        fetchCases();
        const interval = setInterval(fetchCases, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);

        // 1. Create Case
        const res = await fetch('http://localhost:8000/cases', { method: 'POST' });
        const { case_id } = await res.json();

        // 2. Upload File
        const formData = new FormData();
        formData.append('file', file);

        await fetch(`http://localhost:8000/cases/${case_id}/upload`, {
            method: 'POST',
            body: formData
        });

        setUploading(false);
        fetchCases();
        onSelectCase(case_id);
    };

    return (
        <div>
            <div className="header">
                <h1>Active Claims</h1>
                <div style={{ position: 'relative' }}>
                    <input
                        type="file"
                        id="case-upload"
                        style={{ display: 'none' }}
                        onChange={handleUpload}
                    />
                    <button className="btn" onClick={() => document.getElementById('case-upload').click()} disabled={uploading}>
                        {uploading ? 'Uploading...' : '+ New KYC Case'}
                    </button>
                </div>
            </div>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>Case ID</th>
                            <th>Customer ID</th>
                            <th>Status</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cases.map(c => (
                            <tr key={c.case_id} onClick={() => onSelectCase(c.case_id)}>
                                <td style={{ fontFamily: 'monospace' }}>{c.case_id}</td>
                                <td>{c.customer_id}</td>
                                <td>
                                    <span className={`badge ${c.status.toLowerCase().split('_')[0]}`}>
                                        {c.status.replace(/_/g, " ")}
                                    </span>
                                </td>
                                <td>{new Date(c.created_at).toLocaleString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
