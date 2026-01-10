import React from 'react';
import { Shield, Sparkles, Activity, FileText, ArrowRight, Zap, ExternalLink, RefreshCw } from 'lucide-react';

function App() {
    const cards = [
        {
            title: "Dynamic Underwriter",
            description: "Real-time life & health risk pricing using IoT data and context engineering.",
            icon: Activity,
            color: "emerald",
            url: "http://localhost:5173"
        },
        {
            title: "Computer Vision FNOL",
            description: "Autonomous claims intake and damage analysis using vision models.",
            icon: Zap,
            color: "blue",
            url: "http://localhost:5174"
        },
        {
            title: "Lifecycle Manager",
            description: "Hyper-personalized policy recommendations based on simulated life events.",
            icon: Sparkles,
            color: "purple",
            url: "http://localhost:5175"
        },
        {
            title: "Fraud Investigator",
            description: "SIU counter-intelligence dashboard for detecting anomalies and ghost broking.",
            icon: Shield,
            color: "rose",
            url: "http://localhost:5176"
        },
        {
            title: "Compliance Bot",
            description: "Automated regulatory scanning and RAG-based response compliance.",
            icon: ExternalLink,
            color: "amber",
            url: "http://localhost:5177"
        },
        {
            title: "Migration Agent",
            description: "Legacy to Cloud-Native transformation (WebMethods -> Spring Boot) with SRS generation.",
            icon: RefreshCw,
            color: "cyan",
            url: "http://localhost:5178"
        }
    ];

    return (
        <div className="min-h-screen bg-black text-slate-200 font-sans selection:bg-emerald-500/30">

            {/* Background Elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/2 -ml-[500px] -mt-[500px] w-[1000px] h-[1000px] bg-emerald-500/5 rounded-full blur-[120px] opacity-50"></div>
                <div className="absolute bottom-0 right-1/2 -mr-[500px] -mb-[500px] w-[1000px] h-[1000px] bg-blue-500/5 rounded-full blur-[120px] opacity-30"></div>
            </div>

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-20 flex flex-col justify-center min-h-screen">

                {/* Header */}
                <div className="text-center mb-24 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <div className="inline-flex items-center gap-2 text-emerald-500 font-mono text-xs font-bold uppercase tracking-[0.2em] mb-4 bg-emerald-500/10 px-4 py-2 rounded-full border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Nexus_OS v3.0
                    </div>
                    <h1 className="text-6xl md:text-8xl font-black text-white tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-500">
                        Agentic<span className="text-emerald-500">AIs</span>
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto font-light leading-relaxed">
                        A suite of autonomous agents powered by <span className="text-white font-medium">Azure OpenAI</span>, <span className="text-white font-medium">Bedrock</span>, and <span className="text-white font-medium">Gemini</span>.
                        Designed for the future of insurance.
                    </p>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {cards.map((card, idx) => (
                        <a
                            key={idx}
                            href={card.url}
                            target="_blank"
                            rel="noreferrer"
                            className="group relative bg-zinc-900/40 backdrop-blur-sm border border-zinc-800 rounded-3xl p-8 hover:bg-zinc-900/80 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl overflow-hidden block"
                        >
                            {/* Glow on hover */}
                            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-tr from-${card.color}-500/10 to-transparent pointer-events-none`}></div>

                            <div className="relative z-10 flex items-start justify-between">
                                <div className="flex-1">
                                    <div className={`w-14 h-14 rounded-2xl bg-zinc-950 border border-zinc-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg text-${card.color}-500`}>
                                        <card.icon className="w-7 h-7" />
                                    </div>

                                    <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-emerald-400 transition-colors">
                                        {card.title}
                                    </h3>
                                    <p className="text-slate-400 leading-relaxed font-light">
                                        {card.description}
                                    </p>
                                </div>

                                <div className={`p-2 rounded-full border border-zinc-800 text-zinc-600 group-hover:border-${card.color}-500 group-hover:text-${card.color}-500 transition-all duration-300 opacity-50 group-hover:opacity-100`}>
                                    <ExternalLink className="w-5 h-5" />
                                </div>
                            </div>

                            <div className="mt-8 flex items-center gap-2 text-sm font-bold text-zinc-600 group-hover:text-white transition-colors uppercase tracking-widest">
                                Launch Module <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
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
