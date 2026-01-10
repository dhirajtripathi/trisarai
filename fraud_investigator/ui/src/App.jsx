import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle, Search, FileText, Settings, User, ChevronRight, Zap } from 'lucide-react';
import axios from 'axios';

function App() {
    const [claims, setClaims] = useState([]);
    const [selectedClaim, setSelectedClaim] = useState(null);
    const [loading, setLoading] = useState(false);
    const [investigationResult, setInvestigationResult] = useState(null);

    // Configuration State
    const [provider, setProvider] = useState('Azure OpenAI');
    const [showConfig, setShowConfig] = useState(false);
    const [creds, setCreds] = useState({
        azure_key: '', azure_endpoint: '',
        aws_access_key: '', aws_secret_key: '', aws_region: '', aws_model_id: '',
        google_key: '', google_model: ''
    });

    useEffect(() => {
        fetchClaims();
    }, []);

    const fetchClaims = async () => {
        try {
            const res = await axios.get('/api/claims');
            setClaims(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleCredChange = (e) => {
        setCreds({ ...creds, [e.target.name]: e.target.value });
    };

    const handleInvestigate = async (claim) => {
        setSelectedClaim(claim);
        setLoading(true);
        setInvestigationResult(null);
        try {
            const res = await axios.post('/api/investigate', {
                claim_id: claim.id,
                claimant_name: claim.name,
                claim_date: claim.date,
                claim_description: claim.desc,
                photo_id: claim.photo,
                provider: provider,
                ...creds
            });
            setInvestigationResult(res.data);
        } catch (err) {
            alert('Error running investigation');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black flex font-sans text-slate-200">

            {/* Sidebar: Claims Feed */}
            <div className="w-80 bg-zinc-950 border-r border-zinc-900 flex flex-col relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-32 bg-emerald-500/5 blur-[50px] pointer-events-none"></div>

                <div className="p-6 border-b border-zinc-900 relative z-10">
                    <div className="flex items-center gap-3 text-white font-bold text-xl tracking-tight">
                        <div className="p-2 bg-gradient-to-br from-emerald-600 to-emerald-800 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.3)]">
                            <Shield className="w-5 h-5 text-white" />
                        </div>
                        <span>Fraud<span className="text-emerald-500">Guard</span></span>
                    </div>
                    <p className="text-[10px] text-zinc-500 mt-2 font-mono ml-1 uppercase tracking-wider">SIU INTELLIGENCE UNIT</p>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-3 relative z-10">
                    <h3 className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-3 pl-1">Incoming Stream</h3>
                    {claims.map(claim => (
                        <div
                            key={claim.id}
                            onClick={() => handleInvestigate(claim)}
                            className={`p-4 rounded-xl border cursor-pointer transition-all group ${selectedClaim?.id === claim.id
                                    ? 'border-emerald-500/50 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
                                    : 'border-zinc-800 bg-zinc-900/50 hover:bg-zinc-900 hover:border-zinc-700'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className={`font-mono text-xs font-bold ${selectedClaim?.id === claim.id ? 'text-emerald-400' : 'text-zinc-500'}`}>{claim.id}</span>
                                <span className="text-[10px] text-zinc-600">{claim.date}</span>
                            </div>
                            <div className={`font-bold text-sm mb-1 ${selectedClaim?.id === claim.id ? 'text-white' : 'text-zinc-300'}`}>{claim.name}</div>
                            <p className="text-xs text-zinc-500 line-clamp-2 leading-relaxed">{claim.desc}</p>
                        </div>
                    ))}
                </div>

                {/* Config Toggle */}
                <div className="p-4 border-t border-zinc-900 bg-zinc-950 relative z-10">
                    <button
                        onClick={() => setShowConfig(!showConfig)}
                        className="flex items-center gap-2 text-xs text-zinc-500 hover:text-emerald-500 font-medium w-full transition-colors"
                    >
                        <Settings className="w-4 h-4" /> {showConfig ? 'Close Configuration' : 'System Configuration'}
                    </button>

                    {showConfig && (
                        <div className="mt-4 space-y-3 animate-in slide-in-from-bottom-2 bg-zinc-900/80 p-4 rounded-xl border border-zinc-800 backdrop-blur-sm">
                            <select
                                value={provider}
                                onChange={(e) => setProvider(e.target.value)}
                                className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none"
                            >
                                <option>Azure OpenAI</option>
                                <option>AWS Bedrock</option>
                                <option>Google Gemini</option>
                            </select>

                            {provider === 'Azure OpenAI' && (
                                <div className="space-y-2">
                                    <input name="azure_key" type="password" placeholder="API Key" value={creds.azure_key} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="azure_endpoint" type="text" placeholder="Endpoint" value={creds.azure_endpoint} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                </div>
                            )}
                            {provider === 'AWS Bedrock' && (
                                <div className="space-y-2">
                                    <input name="aws_access_key" type="password" placeholder="Access Key" value={creds.aws_access_key} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="aws_secret_key" type="password" placeholder="Secret Key" value={creds.aws_secret_key} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="aws_region" type="text" placeholder="Region" value={creds.aws_region} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="aws_model_id" type="text" placeholder="Model ID" value={creds.aws_model_id} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                </div>
                            )}
                            {provider === 'Google Gemini' && (
                                <div className="space-y-2">
                                    <input name="google_key" type="password" placeholder="API Key" value={creds.google_key} onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-10 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">
                {!selectedClaim ? (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-700 border-2 border-dashed border-zinc-900 rounded-3xl">
                        <div className="w-24 h-24 bg-zinc-950 rounded-full flex items-center justify-center mb-6">
                            <Search className="w-10 h-10 text-zinc-800" />
                        </div>
                        <p className="text-xl font-bold text-zinc-600">No Active Case</p>
                        <p className="text-sm text-zinc-700 mt-2">Select a flagged claim from the feed to initiate investigation.</p>
                    </div>
                ) : (
                    <div className="max-w-5xl mx-auto space-y-8 animate-in slide-in-from-bottom-4 duration-500">

                        {/* Header */}
                        <header className="flex justify-between items-start pb-6 border-b border-zinc-900">
                            <div>
                                <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                                    Case File <span className="text-emerald-500 font-mono">#{selectedClaim.id}</span>
                                </h1>
                                <div className="flex items-center gap-6 text-sm text-zinc-500">
                                    <span className="flex items-center gap-2"><User className="w-4 h-4 text-zinc-600" /> {selectedClaim.name}</span>
                                    <span className="flex items-center gap-2"><FileText className="w-4 h-4 text-zinc-600" /> {selectedClaim.date}</span>
                                </div>
                            </div>
                            <div className={`px-4 py-2 rounded-lg border text-sm font-bold shadow-lg ${investigationResult
                                    ? (investigationResult.requires_human_review ? 'bg-amber-950/20 border-amber-900/50 text-amber-500' : 'bg-emerald-950/20 border-emerald-900/50 text-emerald-500')
                                    : 'bg-zinc-900 border-zinc-800 text-zinc-500'
                                }`}>
                                STATUS: {investigationResult ? (investigationResult.requires_human_review ? 'FLAGGED FOR REVIEW' : 'CLEARED') : 'PENDING ANALYSIS'}
                            </div>
                        </header>

                        {loading && (
                            <div className="bg-zinc-900/50 p-20 rounded-2xl border border-zinc-800 text-center animate-pulse">
                                <div className="w-16 h-16 border-4 border-zinc-800 border-t-emerald-500 rounded-full animate-spin mx-auto mb-6"></div>
                                <h3 className="text-xl font-bold text-white mb-2">RUNNING INVESTIGATION PROTOCOLS</h3>
                                <p className="text-zinc-500 font-mono text-sm">Cross-referencing databases • Analyzing Metadata • Checking Social Graph</p>
                            </div>
                        )}

                        {investigationResult && !loading && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">

                                {/* Score Card */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                    <div className={`col-span-1 p-8 rounded-2xl border relative overflow-hidden flex flex-col justify-between ${investigationResult.fraud_score > 70
                                            ? 'bg-rose-950/30 border-rose-500/30'
                                            : 'bg-emerald-950/30 border-emerald-500/30'
                                        }`}>
                                        <div className={`absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-20 -mr-10 -mt-10 ${investigationResult.fraud_score > 70 ? 'bg-rose-500' : 'bg-emerald-500'}`}></div>
                                        <div>
                                            <h3 className="text-xs font-bold uppercase tracking-widest mb-1 opacity-70">Fraud Probability Score</h3>
                                            <div className={`text-6xl font-black tracking-tighter my-4 ${investigationResult.fraud_score > 70 ? 'text-rose-500' : 'text-emerald-500'
                                                }`}>
                                                {investigationResult.fraud_score}
                                            </div>
                                        </div>
                                        <div className="mt-2 text-xs font-bold uppercase tracking-wider bg-black/30 p-2 rounded text-center backdrop-blur-md">
                                            {investigationResult.fraud_score > 70 ? 'CRITICAL RISK DETECTED' : 'LOW RISK PROFILE'}
                                        </div>
                                    </div>

                                    <div className="col-span-2 bg-zinc-900/50 backdrop-blur-md p-8 rounded-2xl border border-zinc-800 shadow-xl">
                                        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-500 mb-4 flex items-center gap-2">
                                            <Zap className="w-4 h-4 text-emerald-500" /> AI Reasoning Engine
                                        </h3>
                                        <p className="text-slate-300 leading-8 font-light text-lg">
                                            "{investigationResult.risk_reasoning}"
                                        </p>
                                    </div>
                                </div>

                                {/* Evidence Board */}
                                <div className="bg-zinc-900/30 rounded-2xl border border-zinc-800 shadow-xl overflow-hidden">
                                    <div className="px-8 py-5 border-b border-zinc-800 bg-black/40 flex items-center gap-3">
                                        <Search className="w-5 h-5 text-emerald-500" />
                                        <h3 className="font-bold text-white">Evidence Log</h3>
                                    </div>
                                    <div className="divide-y divide-zinc-900">
                                        {investigationResult.evidence_log.map((log, idx) => (
                                            <div key={idx} className="p-5 flex gap-5 items-start hover:bg-zinc-900/50 transition-colors">
                                                <div className={`mt-1 flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${log.includes('Red Flag') || log.includes('CRITICAL')
                                                        ? 'bg-rose-500/10 text-rose-500'
                                                        : 'bg-emerald-500/10 text-emerald-500'
                                                    }`}>
                                                    {log.includes('Red Flag') || log.includes('CRITICAL') ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle className="w-3 h-3" />}
                                                </div>
                                                <p className="text-sm text-zinc-400 font-mono">{log}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Actions */}
                                {investigationResult.requires_human_review && (
                                    <div className="bg-gradient-to-r from-amber-950/40 to-black rounded-2xl border border-amber-900/50 p-8 flex items-center justify-between shadow-[0_0_30px_rgba(245,158,11,0.05)]">
                                        <div className="flex items-center gap-4 text-amber-500">
                                            <div className="p-3 bg-amber-500/10 rounded-xl animate-pulse">
                                                <AlertTriangle className="w-8 h-8" />
                                            </div>
                                            <div>
                                                <span className="font-bold text-lg text-amber-100">SIU Intervention Required</span>
                                                <p className="text-amber-500/70 text-sm mt-1">Confidence threshold not met. Manual review mandated.</p>
                                            </div>
                                        </div>
                                        <div className="flex gap-4">
                                            <button className="px-6 py-3 bg-black border border-rose-900/50 text-rose-500 font-bold rounded-xl hover:bg-rose-950/20 hover:border-rose-700 transition-all shadow-lg hover:shadow-rose-900/20">CONFIRM FRAUD</button>
                                            <button className="px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all">DISMISS & PAY</button>
                                        </div>
                                    </div>
                                )}

                            </div>
                        )}

                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
