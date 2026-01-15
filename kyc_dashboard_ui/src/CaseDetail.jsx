import { useState, useEffect } from 'react';

const STEPS = [
    'ANALYZING_DOCS',
    'REVIEW_DOCS',
    'VERIFYING',
    'REVIEW_CHECKS',
    'ASSESSING_RISK',
    'REVIEW_RISK',
    'GENERATING_DECISION',
    'REVIEW_DECISION',
    'CLOSED'
];

export default function CaseDetail({ caseId, onBack }) {
    const [data, setData] = useState(null);
    const [edits, setEdits] = useState({});

    useEffect(() => {
        const interval = setInterval(() => {
            fetch(`http://localhost:8000/cases/${caseId}`)
                .then(res => res.json())
                .then(d => {
                    setData(d);
                    // Pre-fill edits if empty
                    if (Object.keys(edits).length === 0 && d.extracted_data) {
                        setEdits(d.extracted_data);
                    }
                });
        }, 1000);
        return () => clearInterval(interval);
    }, [caseId, edits]);

    const handleAction = async (action, body = {}) => {
        await fetch(`http://localhost:8000/cases/${caseId}/actions/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
    };

    if (!data) return <div>Loading...</div>;

    return (
        <div>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
                <button onClick={onBack} className="btn" style={{ background: 'transparent', color: '#666', marginRight: '1rem' }}>
                    ← Back
                </button>
                <h1>{data.customer_id}</h1>
            </div>

            {/* STEPPER */}
            <div className="card" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', overflowX: 'auto' }}>
                {['Docs', 'Review', 'Checks', 'Review', 'Risk', 'Review', 'Decision'].map((label, i) => (
                    <div key={i} style={{
                        opacity: STEPS.indexOf(data.status) >= i ? 1 : 0.3,
                        fontWeight: STEPS.indexOf(data.status) === i ? 'bold' : 'normal',
                        color: STEPS.indexOf(data.status) === i ? 'var(--accent)' : 'inherit'
                    }}>
                        {i + 1}. {label} {STEPS.indexOf(data.status) > i ? '✓' : ''}
                    </div>
                ))}
            </div>

            <div className="detail-grid">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                    {/* ACTION CARD */}
                    <div className="card" style={{ padding: '2rem', borderTop: '4px solid var(--accent)' }}>
                        <h2>Current Task: {data.status}</h2>

                        {data.status === 'REVIEW_DOCS' && (
                            <div>
                                <p>Please review and edit the extracted data before verifying.</p>
                                <div style={{ display: 'grid', gap: '1rem', marginBottom: '1rem' }}>
                                    <label>
                                        Full Name:
                                        <input
                                            value={edits.full_name || ''}
                                            onChange={e => setEdits({ ...edits, full_name: e.target.value })}
                                            style={{ width: '100%', padding: '0.5rem' }}
                                        />
                                    </label>
                                    <label>
                                        ID Number:
                                        <input
                                            value={edits.id_number || ''}
                                            onChange={e => setEdits({ ...edits, id_number: e.target.value })}
                                            style={{ width: '100%', padding: '0.5rem' }}
                                        />
                                    </label>
                                </div>
                                <button className="btn" onClick={() => handleAction('approve_doc', { extracted_data: edits })}>
                                    ✅ Confirm & Verify
                                </button>
                            </div>
                        )}

                        {data.status === 'REVIEW_CHECKS' && (
                            <div>
                                <p>Review the automated verification checks.</p>
                                <ul style={{ marginBottom: '1rem' }}>
                                    {data.verification_checks.map((c, i) => (
                                        <li key={i} style={{ color: c.passed ? 'green' : 'red' }}>
                                            {c.check_name}: {c.details}
                                        </li>
                                    ))}
                                </ul>
                                <button className="btn" onClick={() => handleAction('approve_checks')}>
                                    ✅ Accept Checks & Assess Risk
                                </button>
                            </div>
                        )}

                        {data.status === 'REVIEW_RISK' && (
                            <div>
                                <p>Review the calculated risk score.</p>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                                    {data.risk_assessment.score} / 100
                                    <span style={{ fontSize: '1rem', fontWeight: 'normal', marginLeft: '1rem' }}>
                                        ({data.risk_assessment.level})
                                    </span>
                                </div>
                                <button className="btn" onClick={() => handleAction('approve_risk')}>
                                    ✅ Accept Risk Score
                                </button>
                            </div>
                        )}

                        {data.status === 'REVIEW_DECISION' && (
                            <div>
                                <p>System Proposal: <strong>{data.final_decision_reason}</strong></p>
                                <div style={{ display: 'flex', gap: '1rem' }}>
                                    <button className="btn" onClick={() => handleAction('finalize', { decision: 'APPROVED' })}>
                                        ✅ Final Approve
                                    </button>
                                    <button className="btn" style={{ background: 'var(--danger)' }} onClick={() => handleAction('finalize', { decision: 'REJECTED' })}>
                                        ❌ Final Reject
                                    </button>
                                </div>
                            </div>
                        )}

                        {data.status.includes('CLOSED') && (
                            <div style={{ color: 'green', fontWeight: 'bold' }}>
                                Case Closed. Final Status: {data.status}
                            </div>
                        )}

                        {data.status.includes('ANALYZING') || data.status.includes('VERIFYING') || data.status.includes('ASSESSING') ? (
                            <div>Agents are working... 🤖</div>
                        ) : null}
                    </div>

                </div>

                <div>
                    <h3>📜 Audit Trail</h3>
                    <div className="audit-trail">
                        {data.audit_log.entries.slice().reverse().map((entry, i) => (
                            <div key={i} className="audit-item">
                                <div className="audit-meta">
                                    {new Date(entry.timestamp).toLocaleTimeString()}
                                </div>
                                <div className="audit-content">
                                    <div className="audit-agent">{entry.agent_id}</div>
                                    <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{entry.action}</div>
                                    <div>{entry.details}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
