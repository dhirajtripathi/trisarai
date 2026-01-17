import React, { useState } from 'react';
import {
    Shield, Sparkles, Activity, FileText, ArrowRight, Zap, ExternalLink, RefreshCw,
    Database, Search, Code, Layers, FileJson, Server, Globe
} from 'lucide-react';

function App() {
    const [filter, setFilter] = useState('all');

    const domains = [
        { id: 'all', label: 'All Agents' },
        { id: 'data', label: 'Data Intelligence' },
        { id: 'fsi', label: 'Financial Services' },
        { id: 'dev', label: 'Developer Tools' }
    ];

    const cards = [
        // --- Data Intelligence ---
        {
            title: "Text-to-SQL Platform",
            description: "Natural language database analysis for business users. Supports SQL & NoSQL.",
            icon: Database,
            color: "blue",
            domain: "data",
            url: "http://localhost:5173" // Known running port
        },
        {
            title: "RAG Knowledge Base",
            title: "RAG Knowledge Base",
            description: "Enterprise Q&A system. Ingest documents and chat with your policies via VectorDB.",
            icon: Search,
            color: "indigo",
            domain: "data",
            url: "http://localhost:5174"
        },

        // --- Financial Services ---
        {
            title: "Dynamic Underwriter",
            title: "Dynamic Underwriter",
            description: "AI-driven risk assessment using Medical History & IoT Data. Features Human-in-the-Loop review.",
            icon: Activity,
            color: "emerald",
            domain: "fsi",
            url: "http://localhost:8503"
        },
        {
            title: "Classic KYC Platform",
            title: "Classic KYC Platform",
            description: "Agentic workflow (Doc -> Risk -> Compliance) with stepped human verification.",
            icon: FileText,
            color: "teal",
            domain: "fsi",
            url: "http://localhost:5175"
        },
        {
            title: "Computer Vision FNOL",
            title: "Computer Vision FNOL",
            description: "Analyze accident photos (Blurry/Clear) and voice transcripts for instant claims estimation.",
            icon: Zap,
            color: "yellow",
            domain: "fsi",
            url: "http://localhost:8501"
        },
        {
            title: "Fraud Investigator",
            title: "Fraud Investigator",
            description: "SIU workbench for investigating suspicious claims with evidentiary logs.",
            icon: Shield,
            color: "rose",
            domain: "fsi",
            url: "http://localhost:8502"
        },
        {
            title: "Compliance Bot",
            title: "Compliance Bot",
            description: "Regulatory firewall that scans draft decisions and rewrites them for safety.",
            icon: Globe,
            color: "amber",
            domain: "fsi",
            url: "http://localhost:8504"
        },

        // --- Developer Tools ---
        {
            title: "API Transformer",
            title: "API Transformer",
            description: "Modernize legacy WSDL/XML interfaces to REST/OpenAPI specs automatically.",
            icon: Server,
            color: "cyan",
            domain: "dev",
            url: "http://localhost:5176"
        },
        {
            title: "Migration Agent",
            title: "Integration Migration",
            description: "Reverse-engineer legacy ESB flows (XML) into Spring Boot/Java + JUnit tests.",
            icon: RefreshCw,
            color: "sky",
            domain: "dev",
            url: "http://localhost:5177"
        },
        {
            title: "Lifecycle Manager",
            title: "Lifecycle Manager",
            description: "Proactive policy management. Simulates life events (Marriage, Home) to Upsell/Cross-sell.",
            icon: Layers,
            color: "purple",
            domain: "dev",
            url: "http://localhost:8506"
        },
        {
            title: "AI DDO",
            title: "AI DDO",
            description: "Digital Delivery Orchestrator: specialized agents (PO, SM, PM) for Agile management.",
            icon: FileJson,
            color: "fuchsia",
            domain: "dev",
            url: "http://localhost:5178"
        }
    ];

    const filteredCards = filter === 'all' ? cards : cards.filter(c => c.domain === filter);

    return (
        <div className="min-h-screen bg-black text-slate-200 font-sans selection:bg-emerald-500/30">

            {/* Background Elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/2 -ml-[500px] -mt-[500px] w-[1000px] h-[1000px] bg-emerald-500/5 rounded-full blur-[120px] opacity-50"></div>
                <div className="absolute bottom-0 right-1/2 -mr-[500px] -mb-[500px] w-[1000px] h-[1000px] bg-blue-500/5 rounded-full blur-[120px] opacity-30"></div>
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-20 flex flex-col justify-center min-h-screen">

                {/* Header */}
                <div className="text-center mb-16 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <div className="inline-flex items-center gap-2 text-emerald-500 font-mono text-xs font-bold uppercase tracking-[0.2em] mb-4 bg-emerald-500/10 px-4 py-2 rounded-full border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Nexus_OS v3.1 (Full Suite)
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black text-white tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-500">
                        Agentic<span className="text-emerald-500">AIs</span>
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto font-light leading-relaxed mb-8">
                        The ultimate suite for Enterprise Intelligence.
                    </p>

                    {/* Filter Tabs */}
                    <div className="inline-flex bg-zinc-900/80 backdrop-blur rounded-full p-1 border border-zinc-800">
                        {domains.map(d => (
                            <button
                                key={d.id}
                                onClick={() => setFilter(d.id)}
                                className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${filter === d.id
                                    ? 'bg-zinc-800 text-white shadow-lg'
                                    : 'text-zinc-500 hover:text-zinc-300'
                                    }`}
                            >
                                {d.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredCards.map((card, idx) => (
                        <a
                            key={idx}
                            href={card.url}
                            target="_blank"
                            rel="noreferrer"
                            className="group relative bg-zinc-900/40 backdrop-blur-sm border border-zinc-800 rounded-3xl p-8 hover:bg-zinc-900/80 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl overflow-hidden block flex flex-col"
                        >
                            {/* Glow on hover */}
                            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-tr from-${card.color}-500/10 to-transparent pointer-events-none`}></div>

                            <div className="relative z-10 flex items-start justify-between mb-auto">
                                <div className="flex-1">
                                    <div className={`w-14 h-14 rounded-2xl bg-zinc-950 border border-zinc-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg text-${card.color}-500`}>
                                        <card.icon className="w-7 h-7" />
                                    </div>

                                    <h3 className="text-xl font-bold text-white mb-3 group-hover:text-emerald-400 transition-colors">
                                        {card.title}
                                    </h3>
                                    <p className="text-slate-400 leading-relaxed font-light text-sm">
                                        {card.description}
                                    </p>
                                </div>
                            </div>

                            <div className="mt-8 flex items-center justify-between border-t border-zinc-800 pt-6">
                                <div className="flex items-center gap-2 text-xs font-bold text-zinc-600 group-hover:text-white transition-colors uppercase tracking-widest">
                                    Launch Module <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                                </div>
                                <div className={`p-2 rounded-full border border-zinc-800 text-zinc-600 group-hover:border-${card.color}-500 group-hover:text-${card.color}-500 transition-all duration-300 opacity-50 group-hover:opacity-100`}>
                                    <ExternalLink className="w-4 h-4" />
                                </div>
                            </div>
                        </a>
                    ))}
                </div>

                <footer className="mt-24 text-center text-zinc-600 text-sm font-mono">
                    &copy; 2024 DEEPMIND AGENTIC CODING. SECURE ENVIRONMENT.
                </footer>

            </div>
        </div>
    );
}

export default App;
