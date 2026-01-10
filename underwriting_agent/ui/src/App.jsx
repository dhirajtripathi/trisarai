import React, { useState, useEffect } from 'react';
import { Activity, Heart, ShieldCheck, AlertCircle, Settings, Check, X, ChevronRight, Zap } from 'lucide-react';
import axios from 'axios';

function App() {
    const [view, setView] = useState('new'); // 'new', 'dashboard'
    const [activeCase, setActiveCase] = useState(null);

    // New Case State
    const [userId, setUserId] = useState('user123');
    const [provider, setProvider] = useState('Azure OpenAI');
    const [creds, setCreds] = useState({
        azure_key: '', azure_endpoint: '', azure_deployment: '', azure_api_version: '',
        aws_access_key: '', aws_secret_key: '', aws_region: 'us-east-1', aws_model_id: 'anthropic.claude-v2',
        google_key: '', google_model: 'gemini-pro'
    });

    // Dashboard State
    const [caseState, setCaseState] = useState(null);
    const [polling, setPolling] = useState(false);

    const handleCredChange = (e) => {
        setCreds({ ...creds, [e.target.name]: e.target.value });
    };

    const startCase = async () => {
        try {
            const res = await axios.post('/cases', {
                user_id: userId,
                provider: provider,
                credentials: creds
            });
            setActiveCase(`case_${userId}`);
            setView('dashboard');
            setPolling(true);
        } catch (err) {
            alert('Failed to start case');
        }
    };

    const fetchState = async () => {
        if (!activeCase) return;
        try {
            const res = await axios.get(`/cases/${activeCase}`);
            setCaseState(res.data);
            if (res.data.is_paused || res.data.final_policy) {
                setPolling(false); // Stop polling if paused or done
            }
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        let interval;
        if (polling) {
            fetchState();
            interval = setInterval(fetchState, 2000);
        }
        return () => clearInterval(interval);
    }, [polling, activeCase]);

    const submitDecision = async (decision) => {
        try {
            const res = await axios.post(`/cases/${activeCase}/resume`, { decision });
            setCaseState({ ...caseState, is_paused: false, final_policy: res.data.final_policy });
        } catch (err) {
            alert('Error submitting decision');
        }
    };

    const NavItem = ({ id, label, icon: Icon }) => (
        <button
            onClick={() => setView(id)}
            className={`w-full text-left p-4 rounded-xl transition-all duration-200 flex items-center gap-3 ${view === id
                    ? 'bg-emerald-500/10 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)] border border-emerald-500/20'
                    : 'text-slate-400 hover:bg-white/5 hover:text-emerald-300'
                }`}
        >
            <Icon className="w-5 h-5" />
            <span className="font-medium tracking-wide">{label}</span>
            {view === id && <ChevronRight className="w-4 h-4 ml-auto opacity-50" />}
        </button>
    );

    return (
        <div className="min-h-screen bg-black flex font-sans text-slate-200 selection:bg-emerald-500/30">

            {/* Sidebar */}
            <div className="w-72 bg-zinc-950 border-r border-zinc-900 p-6 flex flex-col gap-8 relative overflow-hidden">
                {/* Glow Effects */}
                <div className="absolute top-0 left-1/2 -ml-32 -mt-32 w-64 h-64 bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none"></div>

                <div className="relative z-10">
                    <h1 className="text-2xl font-bold flex items-center gap-3 tracking-tight text-white">
                        <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-lg shadow-lg shadow-emerald-500/20">
                            <Activity className="w-6 h-6 text-white" />
                        </div>
                        Aura<span className="text-emerald-500">Agent</span>
                    </h1>
                    <p className="text-xs text-zinc-500 mt-2 font-mono tracking-wider ml-1">RISK_OS v2.4.0</p>
                </div>

                <nav className="space-y-3 relative z-10">
                    <NavItem id="new" label="New Application" icon={Zap} />
                    <NavItem id="dashboard" label="Live Terminal" icon={Activity} />
                </nav>

                <div className="mt-auto relative z-10">
                    <div className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse box-shadow-[0_0_10px_#10b981]"></div>
                            <span className="text-xs font-bold text-emerald-500">SYSTEM ONLINE</span>
                        </div>
                        <div className="text-xs text-zinc-500 font-mono">LATENCY: 12ms</div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 p-10 overflow-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">

                {view === 'new' && (
                    <div className="max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="mb-8">
                            <h2 className="text-3xl font-bold text-white tracking-tight">Initialize Protocol</h2>
                            <p className="text-zinc-500 mt-2 font-light">Configure intelligence parameters for risk assessment.</p>
                        </div>

                        <div className="bg-zinc-900/80 backdrop-blur-xl rounded-2xl border border-zinc-800 p-1">
                            <div className="p-8 space-y-8">

                                {/* Applicant Section */}
                                <div>
                                    <label className="text-xs font-bold text-emerald-500 uppercase tracking-widest mb-3 block font-mono">Target Identity</label>
                                    <div className="relative group">
                                        <select value={userId} onChange={(e) => setUserId(e.target.value)}
                                            className="w-full p-4 bg-black border border-zinc-800 rounded-xl focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition-all font-medium text-slate-300 appearance-none group-hover:border-zinc-700">
                                            <option value="user123">John Doe (ID: user123) - High Risk Profile</option>
                                            <option value="user456">Jane Smith (ID: user456) - Medium Risk Profile</option>
                                        </select>
                                        <div className="absolute right-4 top-4 pointer-events-none text-zinc-500">▼</div>
                                    </div>
                                </div>

                                {/* AI Provider Section */}
                                <div>
                                    <label className="text-xs font-bold text-emerald-500 uppercase tracking-widest mb-3 block font-mono">Neural Engine</label>
                                    <div className="grid grid-cols-3 gap-4 mb-6">
                                        {['Azure OpenAI', 'AWS Bedrock', 'Google Gemini'].map(p => (
                                            <button
                                                key={p}
                                                onClick={() => setProvider(p)}
                                                className={`p-4 rounded-xl border text-sm font-bold transition-all ${provider === p
                                                        ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.1)]'
                                                        : 'border-zinc-800 bg-black text-zinc-500 hover:border-zinc-700 hover:text-zinc-300'
                                                    }`}
                                            >
                                                {p}
                                            </button>
                                        ))}
                                    </div>

                                    <div className="bg-black/50 p-6 rounded-xl border border-zinc-800 space-y-4">
                                        {provider === 'Azure OpenAI' && (
                                            <div className="space-y-4 animate-in fade-in">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <input name="azure_key" type="password" placeholder="API Key" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                    <input name="azure_endpoint" placeholder="Endpoint URL" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                </div>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <input name="azure_deployment" placeholder="Deployment Name (e.g. gpt-4)" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                    <input name="azure_api_version" placeholder="API Version (e.g. 2023-05-15)" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                </div>
                                            </div>
                                        )}

                                        {provider === 'AWS Bedrock' && (
                                            <div className="space-y-4 animate-in fade-in">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <input name="aws_access_key" type="password" placeholder="Access Key ID" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                    <input name="aws_secret_key" type="password" placeholder="Secret Access Key" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                </div>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <input name="aws_region" placeholder="Region (e.g. us-east-1)" defaultValue="us-east-1" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                    <input name="aws_model_id" placeholder="Model ID  (e.g. anthropic.claude-v2)" defaultValue="anthropic.claude-v2" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                </div>
                                            </div>
                                        )}

                                        {provider === 'Google Gemini' && (
                                            <div className="space-y-4 animate-in fade-in">
                                                <input name="google_key" type="password" placeholder="Google API Key" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                                <input name="google_model" placeholder="Model Name (e.g. gemini-pro)" defaultValue="gemini-pro" onChange={handleCredChange} className="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-white placeholder-zinc-600" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="bg-black/20 p-6 border-t border-zinc-800 flex justify-end rounded-b-2xl">
                                <button
                                    onClick={startCase}
                                    className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] hover:-translate-y-0.5 transition-all flex items-center gap-2 group"
                                >
                                    <Zap className="w-5 h-5 fill-current group-hover:scale-110 transition-transform" /> START PROCESS
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {view === 'dashboard' && (
                    <div className="max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="flex justify-between items-center mb-10">
                            <div>
                                <h2 className="text-3xl font-bold text-white tracking-tight">System Monitor // <span className="text-emerald-500">Risk Assessment</span></h2>
                                <p className="text-zinc-500 mt-1 font-mono text-sm">REAL-TIME DATA STREAM ACTIVE</p>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-xs font-mono font-bold text-zinc-500 bg-zinc-900 px-4 py-2 rounded-full border border-zinc-800">
                                    ID: <span className="text-emerald-500">{activeCase || 'N/A'}</span>
                                </span>
                                <button
                                    onClick={() => { setPolling(true); fetchState(); }}
                                    className="p-2 text-emerald-500 hover:bg-emerald-500/10 rounded-full transition-colors"
                                    title="Refresh Data"
                                >
                                    <Activity className={`w-5 h-5 ${polling ? 'animate-spin' : ''}`} />
                                </button>
                            </div>
                        </div>

                        {caseState && caseState.risk_analysis ? (
                            <div className="grid grid-cols-12 gap-8">

                                {/* Left Column: Data & Reasoning */}
                                <div className="col-span-8 space-y-8">

                                    {/* Medical History Card */}
                                    <div className="bg-zinc-900/80 backdrop-blur-md rounded-2xl border border-zinc-800 overflow-hidden">
                                        <div className="bg-black/20 p-6 border-b border-zinc-800 flex justify-between items-center">
                                            <h3 className="text-lg font-bold flex items-center gap-2 text-white">
                                                <Heart className="text-emerald-500 fill-emerald-500/20 w-5 h-5" /> Biological Metrics
                                            </h3>
                                            <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 bg-zinc-900 px-2 py-1 rounded border border-zinc-800">EHR Sync: OK</span>
                                        </div>
                                        <div className="p-6">
                                            <div className="space-y-3">
                                                {caseState.risk_analysis.relevant_conditions.map((c, i) => (
                                                    <div key={i} className="flex justify-between items-center p-4 bg-black/40 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-colors group">
                                                        <span className="font-bold text-slate-300 text-lg group-hover:text-emerald-400 transition-colors">{c.condition}</span>
                                                        <span className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide border ${c.status === 'Active' ? 'bg-amber-900/20 text-amber-500 border-amber-900/30' : 'bg-emerald-900/20 text-emerald-500 border-emerald-900/30'}`}>
                                                            {c.status}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Reasoning Card */}
                                    <div className="bg-zinc-900/80 backdrop-blur-md rounded-2xl border border-zinc-800 overflow-hidden">
                                        <div className="bg-black/20 p-6 border-b border-zinc-800">
                                            <h3 className="text-lg font-bold flex items-center gap-2 text-white">
                                                <ShieldCheck className="text-emerald-500 w-5 h-5" /> Analysis Log
                                            </h3>
                                        </div>
                                        <div className="p-8">
                                            <p className="text-slate-400 leading-relaxed text-lg font-mono">
                                                <span className="text-emerald-600">>></span> "{caseState.risk_analysis.reasoning || caseState.risk_analysis.reasoning_text}"
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Right Column: Pricing & Decision */}
                                <div className="col-span-4 space-y-8">
                                    {/* Premium Card */}
                                    <div className="bg-gradient-to-br from-emerald-900 to-black rounded-2xl border border-emerald-900/50 shadow-[0_0_30px_rgba(6,78,59,0.3)] p-8 relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-emerald-500 opacity-20 rounded-full blur-3xl group-hover:opacity-30 transition-opacity"></div>
                                        <h3 className="text-emerald-400 text-xs font-bold uppercase tracking-widest mb-2">Calculated Premium</h3>
                                        <div className="flex items-baseline gap-1">
                                            <span className="text-5xl font-bold tracking-tight text-white">${caseState.risk_analysis.suggested_premium}</span>
                                            <span className="text-zinc-500 font-medium">/mo</span>
                                        </div>
                                    </div>

                                    {/* Status/Action Card */}
                                    {caseState.is_paused ? (
                                        <div className="bg-zinc-900 rounded-2xl border-2 border-amber-500/50 shadow-[0_0_20px_rgba(245,158,11,0.1)] p-8 space-y-6">
                                            <div className="flex items-center gap-3 text-amber-500">
                                                <div className="p-2 bg-amber-500/10 rounded-lg animate-pulse">
                                                    <AlertCircle className="w-6 h-6" />
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-lg text-white">Review Required</h4>
                                                    <p className="text-zinc-500 text-sm">Policy exceeds automated threshold.</p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-4 pt-4">
                                                <button
                                                    onClick={() => submitDecision('Approve')}
                                                    className="py-4 bg-emerald-600/90 hover:bg-emerald-500 text-white font-bold rounded-xl transition-all flex flex-col items-center gap-1 border border-emerald-500/50"
                                                >
                                                    <Check className="w-6 h-6" /> APPROVE
                                                </button>
                                                <button
                                                    onClick={() => submitDecision('Reject')}
                                                    className="py-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-bold rounded-xl border border-zinc-700 hover:border-zinc-600 transition-all flex flex-col items-center gap-1"
                                                >
                                                    <X className="w-6 h-6" /> REJECT
                                                </button>
                                            </div>
                                        </div>
                                    ) : caseState.final_policy ? (
                                        <div className={`rounded-2xl p-8 border-2 ${caseState.final_policy.status === 'Active' ? 'bg-emerald-950/30 border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.1)]' : 'bg-rose-950/30 border-rose-500/30'}`}>
                                            <div className="text-center mb-6">
                                                <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 ${caseState.final_policy.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                                                    {caseState.final_policy.status === 'Active' ? <Check className="w-8 h-8" /> : <X className="w-8 h-8" />}
                                                </div>
                                                <h3 className={`font-bold text-2xl ${caseState.final_policy.status === 'Active' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    Policy {caseState.final_policy.status}
                                                </h3>
                                            </div>

                                            {caseState.final_policy.conditions && (
                                                <div className="bg-black/30 rounded-xl p-4 border border-white/5">
                                                    <h4 className="text-[10px] font-bold uppercase text-zinc-500 mb-3 tracking-widest">Nudges & Conditions</h4>
                                                    <ul className="space-y-2">
                                                        {caseState.final_policy.conditions.map((n, i) => (
                                                            <li key={i} className="text-sm text-zinc-300 flex items-start gap-2 font-light">
                                                                <span className="text-emerald-500 mt-1">›</span> {n}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-12 text-center text-zinc-500">
                                            <div className="w-12 h-12 border-4 border-zinc-800 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4"></div>
                                            Initializing Analysis...
                                        </div>
                                    )}
                                </div>

                            </div>
                        ) : (
                            <div className="text-center py-20 opacity-30">
                                <div className="w-24 h-24 bg-zinc-900 rounded-full mx-auto mb-6 flex items-center justify-center border border-zinc-800">
                                    <Activity className="w-10 h-10 text-zinc-600" />
                                </div>
                                <h3 className="text-xl font-medium text-zinc-500">System Awaiting Input</h3>
                                <p className="text-zinc-700">Initialize protocol to view telemetry.</p>
                            </div>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
}

export default App;
