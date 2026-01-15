export function ConfigurationView() {
    return (
        <div>
            <h1>System Configuration</h1>
            <div className="card" style={{ padding: '2rem' }}>
                <h3>Features</h3>
                <div style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input type="checkbox" checked readOnly />
                        Human-in-the-Loop Workflow
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input type="checkbox" checked readOnly />
                        Audit Trail Logging
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input type="checkbox" checked readOnly />
                        SQLite Persistence
                    </label>
                </div>

                <h3 style={{ marginTop: '2rem' }}>Risk Thresholds</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Low/Medium Cutoff</label>
                        <input type="number" value="20" readOnly style={{ padding: '0.5rem', width: '100%' }} />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Medium/High Cutoff</label>
                        <input type="number" value="80" readOnly style={{ padding: '0.5rem', width: '100%' }} />
                    </div>
                </div>
                <p style={{ marginTop: '1rem', color: '#666', fontSize: '0.9rem' }}>
                    * Configuration is currently read-only in this demo version.
                </p>
            </div>
        </div>
    );
}

export function GlobalAuditView() {
    return (
        <div>
            <h1>Global Audit Logs</h1>
            <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                <p>This view would aggregate detailed logs across ALL cases for compliance officers.</p>
                <p>For now, please view the Audit Trail within individual Case Details.</p>
            </div>
        </div>
    );
}
