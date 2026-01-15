import React, { useState } from 'react';
import axios from 'axios';
import {
    LayoutDashboard,
    GitPullRequest,
    AlertTriangle,
    CheckCircle2,
    Play,
    FileText,
    ShieldCheck,
    Activity,
    Zap,
    ArrowRight,
    Layers,
    Target,
    Calendar,
    Briefcase,
    Globe,
    Gavel,
    Lock,
    Unlock,
    Settings,
    Save,
    Server
} from 'lucide-react';

function App() {
    const [role, setRole] = useState('PO'); // PO, SM, PMA, PROJMA, PGMA, ORCH

    // PO State
    const [feature, setFeature] = useState('');
    const [poThread, setPoThread] = useState(null);
    const [stories, setStories] = useState([]);
    const [poStatus, setPoStatus] = useState('IDLE');

    // SM State
    const [smThread, setSmThread] = useState(null);
    const [anomalies, setAnomalies] = useState([]);
    const [smStatus, setSmStatus] = useState('IDLE');

    // PMA State (Product Manager)
    const [strategyGoal, setStrategyGoal] = useState('');
    const [pmaThread, setPmaThread] = useState(null);
    const [roadmap, setRoadmap] = useState([]);
    const [pmaStatus, setPmaStatus] = useState('IDLE');

    // ProjMA State (Project Manager)
    const [projThread, setProjThread] = useState(null);
    const [forecast, setForecast] = useState(null);
    const [risks, setRisks] = useState([]);
    const [projStatus, setProjStatus] = useState('IDLE');

    // PgMA State (Program Manager)
    const [pgStatus, setPgStatus] = useState('IDLE');
    const [pgReport, setPgReport] = useState(null);

    // Orch State (Portfolio Orchestrator)
    const [orchStatus, setOrchStatus] = useState('IDLE');
    const [policyDecision, setPolicyDecision] = useState(null);

    // Settings State
    const [config, setConfig] = useState(null);
    const [configStatus, setConfigStatus] = useState('IDLE');

    // --- Handlers ---

    // Load Config on Mount (or when Settings clicked)
    const loadConfig = async () => {
        try {
            const res = await axios.get('/config');
            setConfig(res.data);
        } catch (e) {
            console.error(e);
        }
    };

    const saveConfig = async () => {
        setConfigStatus('SAVING');
        try {
            await axios.post('/config', { config });
            setConfigStatus('SAVED');
            setTimeout(() => setConfigStatus('IDLE'), 2000);
        } catch (e) {
            console.error(e);
            setConfigStatus('ERROR');
        }
    };

    const handleConfigChange = (section, key, value) => {
        setConfig(prev => {
            if (section) {
                return { ...prev, [section]: { ...prev[section], [key]: value } };
            } else {
                return { ...prev, [key]: value };
            }
        });
    };

    const startRefinement = async () => {
        setPoStatus('THINKING');
        try {
            const res = await axios.post('/po/draft', { feature });
            setPoThread(res.data.thread_id);
            setStories(res.data.stories);
            setPoStatus('REVIEW');
        } catch (e) { console.error(e); setPoStatus('ERROR'); }
    };

    const approveStories = async () => {
        try {
            await axios.post('/po/approve', { thread_id: poThread, decision: "APPROVE" });
            setPoStatus('COMMITTED');
            setTimeout(() => setStories([]), 2000);
        } catch (e) { console.error(e); }
    };

    const analyzeSprint = async () => {
        setSmStatus('ANALYZING');
        try {
            const res = await axios.post('/sm/analyze', { action: "analyze" });
            setSmThread(res.data.thread_id);
            setAnomalies(res.data.anomalies);
            if (res.data.status === "ALERT_TRIGGERED") {
                setSmStatus('ALERT');
            } else {
                setSmStatus('HEALTHY');
            }
        } catch (e) { console.error(e); }
    };

    const ackAlert = async () => {
        try {
            await axios.post('/sm/acknowledge', { thread_id: smThread, decision: "ACK" });
            setSmStatus('RESOLVED');
        } catch (e) { console.error(e); }
    };

    const generateRoadmap = async () => {
        setPmaStatus('STRATEGIZING');
        try {
            const res = await axios.post('/pma/roadmap', { goal: strategyGoal });
            setPmaThread(res.data.thread_id);
            setRoadmap(res.data.roadmap);
            setPmaStatus('REVIEW');
        } catch (e) { console.error(e); setPmaStatus('ERROR'); }
    };

    const approveRoadmap = async () => {
        try {
            await axios.post('/pma/approve', { thread_id: pmaThread, decision: "APPROVE" });
            setPmaStatus('PUBLISHED');
        } catch (e) { console.error(e); }
    };

    const forecastDelivery = async () => {
        setProjStatus('FORECASTING');
        try {
            const res = await axios.post('/projma/forecast', { action: "forecast" });
            setProjThread(res.data.thread_id);
            setForecast(res.data.forecast);
            setRisks(res.data.risks);
            setProjStatus('COMPLETE');
        } catch (e) { console.error(e); setProjStatus('ERROR'); }
    };

    const checkProgramHealth = async () => {
        setPgStatus('SCANNING');
        try {
            const res = await axios.post('/pgma/health', { action: "check" });
            setPgReport(res.data.report);
            setPgStatus('COMPLETE');
        } catch (e) { console.error(e); setPgStatus('ERROR'); }
    };

    const enforceGovernance = async () => {
        setOrchStatus('GOVERNING');
        try {
            const res = await axios.post('/orch/govern', { action: "govern" });
            setPolicyDecision(res.data.decision);
            setOrchStatus(res.data.status === 'GATE_LOCKED' ? 'LOCKED' : 'APPROVED');
        } catch (e) { console.error(e); setOrchStatus('ERROR'); }
    };

    const handleTestConnection = async (type) => {
        const endpoint = type === 'llm' ? '/config/test-llm' : '/config/test-jira';
        try {
            // Check required fields before testing
            if (type === 'llm' && config.llm_provider === 'azure' && !config.azure_config.api_key) {
                alert("Please enter an API Key first."); return;
            }
            // Add other checks as needed or let backend fail

            const res = await axios.post(endpoint, { config });
            if (res.data.status === 'SUCCESS') {
                alert(`✅ Success: ${res.data.message}`);
            } else {
                alert(`❌ Connection Failed: ${res.data.message}`);
            }
        } catch (e) {
            console.error(e);
            alert(`❌ Error: ${e.message}`);
        }
    };




    return (
        <div className="min-h-screen bg-black text-slate-200 font-sans selection:bg-emerald-500/30 font-light">

            {/* Ambient Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-emerald-900/10 rounded-full blur-[120px] opacity-50 mix-blend-screen"></div>
                <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-blue-900/10 rounded-full blur-[120px] opacity-30 mix-blend-screen"></div>
            </div>

            <div className="relative z-10 flex h-screen overflow-hidden">

                {/* Glass Sidebar */}
                <aside className="w-80 bg-zinc-950/50 backdrop-blur-xl border-r border-white/5 flex flex-col justify-between p-6 overflow-y-auto">
                    <div>
                        <div className="flex items-center gap-3 mb-10 px-2">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-900/20">
                                <ShieldCheck className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="font-bold text-white tracking-tight text-lg">AI-DDO</h1>
                                <p className="text-xs text-emerald-500 font-mono tracking-widest uppercase">Digital Delivery</p>
                            </div>
                        </div>

                        <nav className="space-y-8">
                            <div>
                                <div className="text-xs font-bold text-indigo-500 uppercase tracking-widest mb-3 pl-4">Portfolio Layer</div>
                                <div className="space-y-1">
                                    <RoleButton active={role === 'ORCH'} onClick={() => setRole('ORCH')} icon={Gavel} label="Orchestrator" desc="Governance & Policy" />
                                    <RoleButton active={role === 'PGMA'} onClick={() => setRole('PGMA')} icon={Globe} label="Program Manager" desc="Cross-Team Health" />
                                </div>
                            </div>

                            <div>
                                <div className="text-xs font-bold text-blue-500 uppercase tracking-widest mb-3 pl-4">Strategy Layer</div>
                                <div className="space-y-1">
                                    <RoleButton active={role === 'PMA'} onClick={() => setRole('PMA')} icon={Target} label="Product Manager" desc="Strategy & Roadmap" />
                                    <RoleButton active={role === 'PROJMA'} onClick={() => setRole('PROJMA')} icon={Calendar} label="Project Manager" desc="Schedule & Risk" />
                                </div>
                            </div>

                            <div>
                                <div className="text-xs font-bold text-zinc-600 uppercase tracking-widest mb-3 pl-4">Execution Layer</div>
                                <div className="space-y-1">
                                    <RoleButton active={role === 'PO'} onClick={() => setRole('PO')} icon={LayoutDashboard} label="Product Owner" desc="Backlog & Stories" />
                                    <RoleButton active={role === 'SM'} onClick={() => setRole('SM')} icon={Activity} label="Scrum Master" desc="Flow & Blockers" />
                                </div>
                            </div>
                        </nav>

                        <div className="mt-10 pt-6 border-t border-white/5">
                            <button
                                onClick={() => { setRole('SETTINGS'); loadConfig(); }}
                                className={`group w-full text-left p-3 rounded-xl flex items-center gap-3 transition-all ${role === 'SETTINGS' ? 'bg-white/10 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
                            >
                                <Settings className="w-5 h-5" />
                                <span className="font-medium">Configuration</span>
                            </button>
                        </div>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto p-12">

                    {/* --- EXECUTION LAYER --- */}
                    {role === 'PO' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <Header title="Backlog Refinement" subtitle="Generative Context Engineering for Agile Requirements" badge="PO AGENT" />
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[600px]">
                                <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-6 flex flex-col">
                                    <label className="text-xs font-bold text-emerald-500 mb-4 tracking-widest uppercase flex items-center gap-2"><FileText className="w-4 h-4" /> Feature Input</label>
                                    <textarea value={feature} onChange={(e) => setFeature(e.target.value)} className="flex-1 bg-transparent border-none focus:ring-0 text-lg leading-relaxed text-zinc-300 placeholder:text-zinc-700 resize-none p-0" placeholder="Describe the feature requirement here..." />
                                    <button onClick={startRefinement} disabled={poStatus === 'THINKING'} className="mt-6 w-full bg-white text-black hover:bg-emerald-400 font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50">
                                        {poStatus === 'THINKING' ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5 fill-current" />} Generate Stories
                                    </button>
                                </div>
                                <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-8 overflow-y-auto">
                                    <label className="text-xs font-bold text-zinc-500 mb-6 tracking-widest uppercase flex items-center justify-between"><span>Generated Artifacts</span>{poStatus === 'REVIEW' && <span className="text-amber-400 flex items-center gap-1 animate-pulse"><AlertTriangle className="w-3 h-3" /> Review Required</span>}</label>
                                    <div className="space-y-4">
                                        {stories.map((story, idx) => (
                                            <div key={idx} className="group bg-black/40 border border-white/5 p-6 rounded-2xl transition-all hover:border-emerald-500/50">
                                                <div className="flex justify-between items-start mb-3"><h4 className="font-semibold text-white group-hover:text-emerald-400 transition-colors">{story.title}</h4><span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded">WSJF {story.wsjf}</span></div>
                                                <p className="text-sm text-zinc-400 mb-4">{story.description}</p>
                                                <div className="text-xs font-mono bg-zinc-950 p-3 rounded-lg text-emerald-300/80 border-l-2 border-emerald-500/50">{story.ac}</div>
                                            </div>
                                        ))}
                                        {stories.length === 0 && <div className="text-zinc-700 text-center mt-20">Waiting for context...</div>}
                                    </div>
                                    {poStatus === 'REVIEW' && (<div className="sticky bottom-0 mt-8 pt-4 border-t border-white/5 bg-zinc-900/90 backdrop-blur flex gap-4"><button onClick={approveStories} className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-black py-3 rounded-xl font-bold">Approve</button><button onClick={() => setStories([])} className="px-6 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl font-medium">Discard</button></div>)}
                                </div>
                            </div>
                        </div>
                    )}

                    {role === 'SM' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <Header title="Sprint Health" subtitle="Flow Optimization & Anomaly Detection" badge="SM AGENT" />
                            <div className="grid grid-cols-3 gap-6">
                                <MetricCard label="Velocity" value="38" trend="+5%" color="emerald" />
                                <MetricCard label="Cycle Time" value="4.2d" trend="-12%" color="emerald" />
                                <MetricCard label="Flow Efficiency" value="32%" trend="Stable" color="zinc" />
                            </div>
                            <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-8 min-h-[400px]">
                                <div className="flex justify-between items-center mb-8">
                                    <h3 className="font-bold text-white text-xl">Impediment Scanner</h3>
                                    <button onClick={analyzeSprint} disabled={smStatus === 'ANALYZING'} className="bg-white/5 hover:bg-white/10 text-white border border-white/10 px-6 py-3 rounded-full text-sm font-bold flex items-center gap-3">
                                        {smStatus === 'ANALYZING' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4 text-emerald-400" />} Scan Board
                                    </button>
                                </div>
                                <div className="space-y-4">
                                    {smStatus === 'ALERT' && anomalies.map((alert, i) => (
                                        <div key={i} className="bg-red-500/10 border border-red-500/30 p-6 rounded-2xl flex items-center justify-between">
                                            <div className="flex items-center gap-4"><AlertTriangle className="w-6 h-6 text-red-500" /><div><h4 className="font-bold text-white">Anomaly Detected</h4><p className="text-red-300/80 text-sm">{alert}</p></div></div>
                                            <button onClick={ackAlert} className="bg-red-500 hover:bg-red-400 text-black px-4 py-2 rounded-lg font-bold">Escalate</button>
                                        </div>
                                    ))}
                                    {smStatus === 'HEALTHY' && <div className="text-center py-20 text-emerald-500">Flow is optimal.</div>}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* --- STRATEGY LAYER --- */}
                    {role === 'PMA' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <Header title="Strategic Roadmap" subtitle="Aligning Business Goals with Delivery Execution" badge="PM AGENT" />
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                <div className="lg:col-span-1 bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-6 h-fit">
                                    <label className="text-xs font-bold text-blue-500 mb-4 tracking-widest uppercase block">Business Goal</label>
                                    <textarea value={strategyGoal} onChange={(e) => setStrategyGoal(e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-xl p-4 text-white mb-4 h-32 focus:border-blue-500 focus:outline-none" placeholder="e.g. Expand into Enterprise Market in Q3..." />
                                    <button onClick={generateRoadmap} disabled={pmaStatus === 'STRATEGIZING'} className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2">
                                        {pmaStatus === 'STRATEGIZING' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4" />} Generate Roadmap
                                    </button>
                                </div>
                                <div className="lg:col-span-2 space-y-6">
                                    {roadmap.map((item, i) => (
                                        <div key={i} className="bg-zinc-900/50 border border-white/5 p-6 rounded-2xl flex items-center gap-6 group hover:border-blue-500/30 transition-all">
                                            <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold text-xl shrink-0">{item.quarter}</div>
                                            <div className="flex-1">
                                                <div className="flex justify-between items-start"><h4 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">{item.initiative}</h4><div className="bg-blue-900/30 text-blue-200 text-xs px-2 py-1 rounded border border-blue-500/20">{item.confidence * 100}% Conf.</div></div>
                                                <p className="text-zinc-500 text-sm mt-1">{item.theme}</p>
                                                <div className="mt-3 flex items-center gap-2 text-xs text-zinc-400"><CheckCircle2 className="w-3 h-3 text-emerald-500" /><span>Aligned: {item.okr_alignment}</span></div>
                                            </div>
                                        </div>
                                    ))}
                                    {pmaStatus === 'REVIEW' && (<div className="flex justify-end gap-4 mt-8"><button onClick={approveRoadmap} className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-blue-900/20">Publish Roadmap</button></div>)}
                                    {pmaStatus === 'PUBLISHED' && (<div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl text-emerald-400 text-center font-bold">Roadmap Published to Execution Layer</div>)}
                                </div>
                            </div>
                        </div>
                    )}

                    {role === 'PROJMA' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <Header title="Delivery Forecast" subtitle="Predictive Schedule & Risk Analysis" badge="PROJ MANAGER AGENT" />
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                                <MetricCard label="Confidence" value={forecast ? "Low" : "-"} trend="Needs Attention" color="amber" />
                                <MetricCard label="Variance" value={forecast ? `+${forecast.variance_days}d` : "-"} trend="Slippage" color="red" />
                                <MetricCard label="Target Date" value="Sept 30" trend="Fixed" color="zinc" />
                            </div>
                            <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-8">
                                <div className="flex justify-between items-center mb-8">
                                    <h3 className="text-xl font-bold text-white">Risk Register</h3>
                                    <button onClick={forecastDelivery} disabled={projStatus === 'FORECASTING'} className="bg-white/5 hover:bg-white/10 text-white border border-white/10 px-6 py-3 rounded-full text-sm font-bold flex items-center gap-3">
                                        {projStatus === 'FORECASTING' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Briefcase className="w-4 h-4 text-emerald-400" />} Update Forecast
                                    </button>
                                </div>
                                {projStatus === 'COMPLETE' && (
                                    <div className="space-y-4">
                                        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-200">
                                            <div className="text-xs font-bold text-red-500 uppercase mb-1">Forecast Alert</div>
                                            <div className="text-lg font-bold text-white">Predicted Completion: {forecast.predicted_date}</div>
                                            <div className="text-sm opacity-70">Current plan exceeds deadline by {forecast.variance_days} days.</div>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                                            {risks.map((risk, i) => (<div key={i} className="bg-black/40 p-4 rounded-xl border border-white/5 flex gap-3"><AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" /><div className="text-sm text-zinc-300">{risk}</div></div>))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* --- PORTFOLIO LAYER (Phase 3) --- */}

                    {role === 'PGMA' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <Header title="Program Health" subtitle="Cross-Team Dependency & Risk Management" badge="PGM MANAGER AGENT" />

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                <div className="bg-zinc-900/40 border border-white/10 p-6 rounded-3xl">
                                    <div className="text-zinc-500 text-xs font-bold uppercase tracking-widest mb-4">Portfolio Risks</div>
                                    <div className="text-4xl font-bold text-white mb-2">{pgReport ? pgReport.risk_heatmap['Mobile App Refresh'] === 'HIGH' ? 'Critical' : 'Stable' : '-'}</div>
                                    <div className="text-sm text-zinc-400">Systemic bottlenecks detected</div>
                                </div>
                                <div className="bg-zinc-900/40 border border-white/10 p-6 rounded-3xl">
                                    <div className="text-zinc-500 text-xs font-bold uppercase tracking-widest mb-4">Critical Path</div>
                                    <div className="text-4xl font-bold text-white mb-2">{pgReport ? pgReport.critical_path_blockers.length : '-'} Blockers</div>
                                    <div className="text-sm text-zinc-400">Cross-team dependencies</div>
                                </div>
                            </div>

                            <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-8 min-h-[400px]">
                                <div className="flex justify-between items-center mb-8">
                                    <h3 className="text-xl font-bold text-white">Program Dependency Graph</h3>
                                    <button onClick={checkProgramHealth} disabled={pgStatus === 'SCANNING'} className="bg-white/5 hover:bg-white/10 text-white border border-white/10 px-6 py-3 rounded-full text-sm font-bold flex items-center gap-3">
                                        {pgStatus === 'SCANNING' ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4 text-indigo-400" />} Scan Dependencies
                                    </button>
                                </div>

                                {pgStatus === 'COMPLETE' && (
                                    <div className="space-y-6">
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            {Object.entries(pgReport.risk_heatmap).map(([prog, risk]) => (
                                                <div key={prog} className={`p-6 rounded-2xl border ${risk === 'HIGH' ? 'bg-red-500/10 border-red-500/30' : risk === 'MEDIUM' ? 'bg-amber-500/10 border-amber-500/30' : 'bg-emerald-500/10 border-emerald-500/30'}`}>
                                                    <div className="font-bold text-white mb-2">{prog}</div>
                                                    <div className={`text-xs font-bold px-2 py-1 rounded inline-block ${risk === 'HIGH' ? 'bg-red-500 text-white' : risk === 'MEDIUM' ? 'bg-amber-500 text-black' : 'bg-emerald-500 text-white'}`}>{risk} RISK</div>
                                                </div>
                                            ))}
                                        </div>

                                        <div className="mt-8">
                                            <h4 className="text-lg font-bold text-white mb-4">Dependency Collisions</h4>
                                            {pgReport.critical_path_blockers.map((blocker, i) => (
                                                <div key={i} className="flex items-center gap-4 bg-black/40 p-4 rounded-xl border-l-4 border-indigo-500">
                                                    <Layers className="w-5 h-5 text-indigo-400" />
                                                    <span className="text-zinc-300">{blocker}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {role === 'ORCH' && (
                        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <Header title="Governance Console" subtitle="Portfolio Policy Enforcement & Audit" badge="PORTFOLIO ORCHESTRATOR" />

                            <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-8 min-h-[500px] flex flex-col items-center justify-center text-center relative overflow-hidden">
                                {/* Background decoration */}
                                <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/5 to-transparent pointer-events-none"></div>

                                {orchStatus === 'IDLE' && (
                                    <div className="max-w-md space-y-6 relative z-10">
                                        <div className="w-20 h-20 bg-indigo-500/20 rounded-full flex items-center justify-center mx-auto text-indigo-400">
                                            <Gavel className="w-10 h-10" />
                                        </div>
                                        <h3 className="text-2xl font-bold text-white">Policy Enforcement Gate</h3>
                                        <p className="text-zinc-400">Verify all active programs against corporate governance policies (Budget, Security, Compliance).</p>
                                        <button onClick={enforceGovernance} className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-indigo-900/20">
                                            Run Compliance Check
                                        </button>
                                    </div>
                                )}

                                {orchStatus === 'GOVERNING' && (
                                    <div className="flex flex-col items-center gap-4">
                                        <RefreshCw className="w-12 h-12 text-indigo-500 animate-spin" />
                                        <div className="text-indigo-300 font-mono animate-pulse">Auditing Financial Context...</div>
                                    </div>
                                )}

                                {orchStatus === 'LOCKED' && (
                                    <div className="max-w-2xl w-full text-left space-y-6 animate-in zoom-in duration-300">
                                        <div className="bg-red-950/40 border border-red-500/50 p-8 rounded-3xl relative overflow-hidden">
                                            <div className="absolute top-0 right-0 p-4 opacity-20"><Lock className="w-32 h-32 text-red-500" /></div>
                                            <div className="relative z-10">
                                                <h3 className="text-3xl font-bold text-red-500 mb-2 flex items-center gap-3"><AlertTriangle className="w-8 h-8" /> Gate Locked</h3>
                                                <p className="text-red-200/80 text-lg mb-6">Governance violations detected. Workflow paused pending Executive Approval.</p>

                                                <div className="space-y-3 bg-black/40 p-6 rounded-xl border border-red-500/20">
                                                    {policyDecision.violations.map((v, i) => (
                                                        <div key={i} className="flex items-start gap-3 text-red-100 font-mono text-sm">
                                                            <span className="text-red-500">{">>"}</span> {v}
                                                        </div>
                                                    ))}
                                                </div>

                                                <div className="mt-8 flex gap-4">
                                                    <button className="flex-1 bg-red-600 hover:bg-red-500 text-white py-3 rounded-xl font-bold">Request Override</button>
                                                    <button onClick={() => setOrchStatus('IDLE')} className="px-8 bg-zinc-800 hover:bg-zinc-700 text-white py-3 rounded-xl font-bold">Dismiss</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {orchStatus === 'APPROVED' && (
                                    <div className="text-center animate-in zoom-in duration-300">
                                        <div className="w-24 h-24 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto text-emerald-500 mb-6">
                                            <Unlock className="w-12 h-12" />
                                        </div>
                                        <h3 className="text-3xl font-bold text-white mb-2">Governance Approved</h3>
                                        <p className="text-emerald-400">All policies passed confidence thresholds.</p>
                                        <button onClick={() => setOrchStatus('IDLE')} className="mt-8 px-8 bg-zinc-800 hover:bg-zinc-700 text-white py-3 rounded-xl font-bold">Done</button>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {role === 'SETTINGS' && !config && (
                        <div className="flex flex-col items-center justify-center h-[500px] animate-in fade-in">
                            <RefreshCw className="w-10 h-10 text-emerald-500 animate-spin mb-4" />
                            <div className="text-zinc-500 font-mono">Loading System Configuration...</div>
                        </div>
                    )}
                    {role === 'SETTINGS' && config && (
                        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <Header title="System Configuration" subtitle="Manage LLM Providers & Integrations" badge="SETTINGS" />

                            <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 rounded-3xl p-8 space-y-8">

                                {/* LLM Provider Section */}
                                <div className="space-y-6">
                                    <div className="flex items-center gap-3 pb-4 border-b border-white/5">
                                        <Server className="w-5 h-5 text-emerald-500" />
                                        <h3 className="text-xl font-bold text-white">LLM Connection</h3>
                                    </div>

                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="col-span-2">
                                            <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Active Provider</label>
                                            <div className="flex bg-black/40 rounded-xl p-1 border border-white/5">
                                                {['mock', 'azure', 'aws', 'google'].map(p => (
                                                    <button
                                                        key={p}
                                                        onClick={() => handleConfigChange(null, 'llm_provider', p)}
                                                        className={`flex-1 py-2 rounded-lg font-bold text-sm transition-all ${config.llm_provider === p ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-900/20' : 'text-zinc-500 hover:text-zinc-300'}`}
                                                    >
                                                        {p.toUpperCase()}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Dynamic Fields based on Provider */}
                                        {config.llm_provider === 'azure' && (
                                            <>
                                                <div className="col-span-2"><label className="text-xs text-zinc-500 uppercase font-bold">Endpoint</label><input value={config.azure_config.endpoint} onChange={(e) => handleConfigChange('azure_config', 'endpoint', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">API Key</label><input type="password" value={config.azure_config.api_key} onChange={(e) => handleConfigChange('azure_config', 'api_key', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Deployment</label><input value={config.azure_config.deployment} onChange={(e) => handleConfigChange('azure_config', 'deployment', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Model Name</label><input value={config.azure_config.model_name} onChange={(e) => handleConfigChange('azure_config', 'model_name', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">API Version</label><input value={config.azure_config.api_version} onChange={(e) => handleConfigChange('azure_config', 'api_version', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                            </>
                                        )}

                                        {config.llm_provider === 'aws' && (
                                            <>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Access Key ID</label><input value={config.aws_config.access_key_id} onChange={(e) => handleConfigChange('aws_config', 'access_key_id', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Secret Access Key</label><input type="password" value={config.aws_config.secret_access_key} onChange={(e) => handleConfigChange('aws_config', 'secret_access_key', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Region</label><input value={config.aws_config.region} onChange={(e) => handleConfigChange('aws_config', 'region', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Model ID</label><input value={config.aws_config.model_id} onChange={(e) => handleConfigChange('aws_config', 'model_id', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                            </>
                                        )}

                                        {config.llm_provider === 'google' && (
                                            <>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">API Key</label><input type="password" value={config.google_config.api_key} onChange={(e) => handleConfigChange('google_config', 'api_key', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                                <div><label className="text-xs text-zinc-500 uppercase font-bold">Model Name</label><input value={config.google_config.model} onChange={(e) => handleConfigChange('google_config', 'model', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                            </>
                                        )}
                                    </div>
                                    <div className="mt-4 flex justify-end">
                                        <button onClick={() => handleTestConnection('llm')} className="text-xs bg-emerald-900/40 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-500/30 px-4 py-2 rounded-lg font-bold transition-all">
                                            Test LLM Connection
                                        </button>
                                    </div>
                                </div>

                                {/* JIRA Section */}
                                <div className="space-y-6 pt-6">
                                    <div className="flex items-center gap-3 pb-4 border-b border-white/5">
                                        <Layers className="w-5 h-5 text-blue-500" />
                                        <h3 className="text-xl font-bold text-white">Jira Integration</h3>
                                    </div>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="col-span-2"><label className="text-xs text-zinc-500 uppercase font-bold">Jira URL</label><input value={config.jira_config.url} onChange={(e) => handleConfigChange('jira_config', 'url', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                        <div><label className="text-xs text-zinc-500 uppercase font-bold">Email (User)</label><input value={config.jira_config.email} onChange={(e) => handleConfigChange('jira_config', 'email', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                        <div><label className="text-xs text-zinc-500 uppercase font-bold">API Token</label><input type="password" value={config.jira_config.api_token} onChange={(e) => handleConfigChange('jira_config', 'api_token', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                        <div><label className="text-xs text-zinc-500 uppercase font-bold">Space Key</label><input value={config.jira_config.space_key} onChange={(e) => handleConfigChange('jira_config', 'space_key', e.target.value)} className="w-full bg-black/50 border border-white/10 rounded-lg p-3 text-white mt-1" /></div>
                                    </div>
                                    <div className="mt-4 flex justify-end">
                                        <button onClick={() => handleTestConnection('jira')} className="text-xs bg-blue-900/40 hover:bg-blue-900/60 text-blue-300 border border-blue-500/30 px-4 py-2 rounded-lg font-bold transition-all">
                                            Test Jira Connection
                                        </button>
                                    </div>
                                </div>

                                <div className="pt-6 flex justify-end">
                                    <button
                                        onClick={saveConfig}
                                        disabled={configStatus === 'SAVING'}
                                        className="bg-white text-black hover:bg-emerald-400 font-bold px-8 py-4 rounded-xl flex items-center gap-2 transition-all shadow-lg"
                                    >
                                        {configStatus === 'SAVING' ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                                        {configStatus === 'SAVED' ? 'Configuration Saved' : 'Save Changes'}
                                    </button>
                                </div>

                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}

// --- Components ---

function Header({ title, subtitle, badge }) {
    return (
        <div className="flex justify-between items-end pb-6 border-b border-white/5">
            <div>
                <div className="text-xs font-bold text-emerald-500 tracking-widest uppercase mb-2">{badge}</div>
                <h2 className="text-4xl font-bold text-white mb-2 tracking-tight">{title}</h2>
                <p className="text-zinc-500 font-light text-lg">{subtitle}</p>
            </div>
        </div>
    )
}

function RoleButton({ active, onClick, icon: Icon, label, desc }) {
    return (
        <button
            onClick={onClick}
            className={`group w-full text-left p-4 rounded-2xl flex items-center gap-4 transition-all duration-300 border ${active
                ? 'bg-emerald-500/10 border-emerald-500/50 shadow-lg shadow-emerald-900/20'
                : 'bg-transparent border-transparent hover:bg-white/5 text-zinc-500 hover:text-zinc-300'
                }`}
        >
            <div className={`p-2 rounded-lg transition-colors ${active ? 'text-emerald-400 bg-emerald-500/20' : 'group-hover:text-white group-hover:bg-white/10'}`}>
                <Icon className="w-5 h-5" />
            </div>
            <div>
                <div className={`font-semibold ${active ? 'text-white' : 'text-zinc-400 group-hover:text-white'}`}>{label}</div>
                <div className={`text-xs ${active ? 'text-emerald-400/70' : 'text-zinc-600'}`}>{desc}</div>
            </div>
            {active && <ArrowRight className="w-4 h-4 ml-auto text-emerald-500 animate-in slide-in-from-left-2" />}
        </button>
    )
}

function MetricCard({ label, value, trend, color }) {
    const colorMap = {
        emerald: "text-emerald-400",
        red: "text-red-400",
        amber: "text-amber-400",
        zinc: "text-zinc-400"
    }

    return (
        <div className="bg-zinc-900/40 backdrop-blur-md border border-white/10 p-6 rounded-3xl hover:border-white/20 transition-all cursor-default">
            <div className="text-zinc-500 text-xs font-bold uppercase tracking-widest mb-4">{label}</div>
            <div className="flex items-end gap-3">
                <div className="text-5xl font-bold text-white tracking-tighter">{value}</div>
                <div className={`text-sm font-medium mb-1.5 ${colorMap[color] || 'text-zinc-500'}`}>{trend}</div>
            </div>
        </div>
    )
}

function RefreshCw({ className }) {
    return <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M3 21v-5h5" /></svg>
}

export default App;
