import React from 'react';

export default function PortalHome({ onNavigate }) {
    const cardStyle = {
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        border: '1px solid #eee'
    };

    const hoverStyle = (e) => {
        e.currentTarget.style.transform = 'translateY(-5px)';
        e.currentTarget.style.boxShadow = '0 8px 15px rgba(0,0,0,0.1)';
    };

    const unhoverStyle = (e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    };

    return (
        <div style={{ padding: '4rem 2rem', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
                <h1 style={{ fontSize: '3rem', marginBottom: '1rem', background: 'linear-gradient(45deg, #007bff, #6610f2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Enterprise AI Portal
                </h1>
                <p style={{ fontSize: '1.2rem', color: '#666' }}>
                    Unified Access to Intelligent Data Tools
                </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                {/* Use Case 1: Chat Analysis */}
                <div
                    style={cardStyle}
                    onClick={() => onNavigate('chat')}
                    onMouseEnter={hoverStyle}
                    onMouseLeave={unhoverStyle}
                >
                    <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>💬</div>
                    <h2 style={{ marginBottom: '1rem' }}>Ask Data</h2>
                    <p style={{ color: '#666', lineHeight: '1.6' }}>
                        Interact with your SQL & NoSQL databases using natural language.
                        Generating insights, executing queries, and exporting results.
                    </p>
                    <button style={{ marginTop: 'auto', padding: '0.8rem 2rem', borderRadius: '50px', border: 'none', background: '#e9ecef', color: '#333', fontWeight: 'bold', cursor: 'pointer' }}>
                        Launch Studio &rarr;
                    </button>
                </div>

                {/* Use Case 2: Schema Viz */}
                <div
                    style={cardStyle}
                    onClick={() => onNavigate('diagram')}
                    onMouseEnter={hoverStyle}
                    onMouseLeave={unhoverStyle}
                >
                    <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🖇️</div>
                    <h2 style={{ marginBottom: '1rem' }}>Knowledge Graph</h2>
                    <p style={{ color: '#666', lineHeight: '1.6' }}>
                        Visualize complex database schemas, foreign key relationships,
                        and business context in an interactive diagram.
                    </p>
                    <button style={{ marginTop: 'auto', padding: '0.8rem 2rem', borderRadius: '50px', border: 'none', background: '#e9ecef', color: '#333', fontWeight: 'bold', cursor: 'pointer' }}>
                        View Diagrams &rarr;
                    </button>
                </div>

                {/* Use Case 3: Admin */}
                <div
                    style={cardStyle}
                    onClick={() => onNavigate('settings')}
                    onMouseEnter={hoverStyle}
                    onMouseLeave={unhoverStyle}
                >
                    <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>⚙️</div>
                    <h2 style={{ marginBottom: '1rem' }}>System Config</h2>
                    <p style={{ color: '#666', lineHeight: '1.6' }}>
                        Configure LLM Models (OpenAI, Gemini, Bedrock)
                        and manage Database connections dynamically.
                    </p>
                    <button style={{ marginTop: 'auto', padding: '0.8rem 2rem', borderRadius: '50px', border: 'none', background: '#e9ecef', color: '#333', fontWeight: 'bold', cursor: 'pointer' }}>
                        Manage Settings &rarr;
                    </button>
                </div>
            </div>
        </div>
    );
}
