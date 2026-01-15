import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

export default function ErDiagramView({ dbName }) {
    const [diagram, setDiagram] = useState('');
    const ref = useRef(null);

    useEffect(() => {
        mermaid.initialize({ startOnLoad: true });

        fetch('/api/mcp/tools/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: "get_er_diagram",
                arguments: { db_name: dbName }
            })
        })
            .then(res => res.json())
            .then(data => {
                setDiagram(data.content?.[0]?.text);
            });
    }, [dbName]);

    useEffect(() => {
        if (diagram && ref.current) {
            mermaid.render('mermaid-chart', diagram).then(res => {
                ref.current.innerHTML = res.svg;
            });
        }
    }, [diagram]);

    if (!diagram) return <div>Loading Diagram...</div>;

    return (
        <div style={{ padding: '2rem', height: '100%', overflow: 'auto' }}>
            <h2>ER Diagram: {dbName}</h2>
            <div ref={ref} />
        </div>
    );
}
