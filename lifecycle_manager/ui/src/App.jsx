import React, { useState, useEffect } from 'react';
import { Home, Car, Heart, Shield, Activity, Send, Settings, ChevronRight, User } from 'lucide-react';
import axios from 'axios';

function App() {
    const [customer, setCustomer] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    // Configuration State
    const [provider, setProvider] = useState('Azure OpenAI');
    const [showConfig, setShowConfig] = useState(false);
    const [creds, setCreds] = useState({
        azure_key: '', azure_endpoint: '', azure_deployment: '', azure_api_version: '',
        aws_access_key: '', aws_secret_key: '', aws_region: '', aws_model_id: '',
        google_key: '', google_model: ''
    });

    useEffect(() => {
        fetchCustomer();
    }, []);

    const fetchCustomer = async () => {
        try {
            const res = await axios.get('/api/customer');
            setCustomer(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleCredChange = (e) => {
        setCreds({ ...creds, [e.target.name]: e.target.value });
    };

    const handleEvent = async (type, desc) => {
        setLoading(true);
        setResult(null);
        try {
            const res = await axios.post('/api/simulate-event', {
                event_type: type,
                description: desc,
                provider: provider,
                ...creds
            });
            setResult(res.data);
        } catch (err) {
            alert('Error simulating event');
        } finally {
            setLoading(false);
        }
    };

    if (!customer) return <div className="min-h-screen bg-black flex items-center justify-center text-emerald-500 font-mono animate-pulse">Initializing Data Stream...</div>;

    return (
        <div className="min-h-screen bg-black flex flex-col md:flex-row font-sans text-slate-200">

            {/* Sidebar / Config */}
            <div className="w-full md:w-80 bg-zinc-950 border-r border-zinc-900 p-6 flex flex-col gap-6 overflow-y-auto relative">
                <div className="absolute top-0 left-0 w-full h-32 bg-emerald-500/5 blur-[50px] pointer-events-none"></div>

                <div className="flex items-center gap-3 text-white font-bold text-xl relative z-10">
                    <div className="p-2 bg-gradient-to-br from-emerald-600 to-emerald-900 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                        <Activity className="w-5 h-5 text-emerald-100" />
                    </div>
                    <span>LifeCycle<span className="text-emerald-500">AI</span></span>
                </div>

                {/* Profile Card */}
                <div className="p-5 bg-zinc-900/80 backdrop-blur-sm rounded-2xl border border-zinc-800 shadow-lg group hover:border-emerald-500/30 transition-all">
                    <h3 className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <User className="w-3 h-3" /> Target Profile
                    </h3>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between items-center pb-2 border-b border-white/5">
                            <span className="text-zinc-500">Identity</span>
                            <span className="font-bold text-white">{customer.name}</span>
                        </div>
                        <div className="flex justify-between items-center pb-2 border-b border-white/5">
                            <span className="text-zinc-500">Age</span>
                            <span className="font-mono text-emerald-400">{customer.age}</span>
                        </div>
                        <div className="flex justify-between items-center pb-2 border-b border-white/5">
                            <span className="text-zinc-500">Active Policies</span>
                            <span className="font-medium text-slate-300 text-right max-w-[120px] truncate">{customer.existing_policies.join(', ')}</span>
                        </div>
                        <div className="flex justify-between items-center pt-1">
                            <span className="text-zinc-500">Annual Premium</span>
                            <span className="font-bold text-emerald-400">${customer.annual_premium}</span>
                        </div>
                    </div>
                </div>

                {/* Simulation Buttons */}
                <div className="space-y-3">
                    <h3 className="text-xs font-bold text-zinc-600 uppercase tracking-widest px-1">Simulate Life Event</h3>

                    <button
                        onClick={() => handleEvent('Marriage', 'Got married to Sarah.')}
                        disabled={loading}
                        className="w-full text-left p-3 rounded-xl border border-zinc-800 hover:border-rose-500/50 hover:bg-rose-500/10 hover:text-rose-200 transition-all flex items-center gap-4 bg-black group"
                    >
                        <div className="w-10 h-10 rounded-lg bg-zinc-900 group-hover:bg-rose-500/20 text-rose-500 flex items-center justify-center transition-colors">
                            <Heart className="w-5 h-5" />
                        </div>
                        <span className="font-medium text-sm text-zinc-400 group-hover:text-rose-100">Marriage Event</span>
                        <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-rose-500" />
                    </button>

                    <button
                        onClick={() => handleEvent('New Home', 'Purchased a 3-bedroom house.')}
                        disabled={loading}
                        className="w-full text-left p-3 rounded-xl border border-zinc-800 hover:border-emerald-500/50 hover:bg-emerald-500/10 hover:text-emerald-200 transition-all flex items-center gap-4 bg-black group"
                    >
                        <div className="w-10 h-10 rounded-lg bg-zinc-900 group-hover:bg-emerald-500/20 text-emerald-500 flex items-center justify-center transition-colors">
                            <Home className="w-5 h-5" />
                        </div>
                        <span className="font-medium text-sm text-zinc-400 group-hover:text-emerald-100">Property Purchase</span>
                        <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-emerald-500" />
                    </button>

                    <button
                        onClick={() => handleEvent('New Car', 'Bought a 2024 Tesla Model Y.')}
                        disabled={loading}
                        className="w-full text-left p-3 rounded-xl border border-zinc-800 hover:border-blue-500/50 hover:bg-blue-500/10 hover:text-blue-200 transition-all flex items-center gap-4 bg-black group"
                    >
                        <div className="w-10 h-10 rounded-lg bg-zinc-900 group-hover:bg-blue-500/20 text-blue-500 flex items-center justify-center transition-colors">
                            <Car className="w-5 h-5" />
                        </div>
                        <span className="font-medium text-sm text-zinc-400 group-hover:text-blue-100">Vehicle Acquisition</span>
                        <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-blue-500" />
                    </button>
                </div>

                {/* Configuration Section */}
                <div className="mt-auto pt-6 border-t border-zinc-900">
                    <button
                        onClick={() => setShowConfig(!showConfig)}
                        className="flex items-center gap-2 text-xs text-zinc-500 hover:text-emerald-500 font-medium transition-colors"
                    >
                        <Settings className="w-3 h-3" /> System Configuration
                    </button>

                    {showConfig && (
                        <div className="mt-4 space-y-3 animate-in slide-in-from-bottom-2 duration-200 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                            <div>
                                <label className="block text-[10px] font-bold text-zinc-500 uppercase mb-2">Provider</label>
                                <select
                                    value={provider}
                                    onChange={(e) => setProvider(e.target.value)}
                                    className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none"
                                >
                                    <option>Azure OpenAI</option>
                                    <option>AWS Bedrock</option>
                                    <option>Google Gemini</option>
                                </select>
                            </div>

                            {provider === 'Azure OpenAI' && (
                                <div className="space-y-2">
                                    <input name="azure_key" type="password" placeholder="API Key" value={creds.azure_key} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="azure_endpoint" type="text" placeholder="Endpoint URL" value={creds.azure_endpoint} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="azure_deployment" type="text" placeholder="Deployment Name" value={creds.azure_deployment} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="azure_api_version" type="text" placeholder="API Version" value={creds.azure_api_version} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                </div>
                            )}

                            {provider === 'AWS Bedrock' && (
                                <div className="space-y-2">
                                    <input name="aws_access_key" type="password" placeholder="Access Key ID" value={creds.aws_access_key} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="aws_secret_key" type="password" placeholder="Secret Key" value={creds.aws_secret_key} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="aws_region" type="text" placeholder="Region" value={creds.aws_region} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="aws_model_id" type="text" placeholder="Model ID" value={creds.aws_model_id} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                </div>
                            )}

                            {provider === 'Google Gemini' && (
                                <div className="space-y-2">
                                    <input name="google_key" type="password" placeholder="API Key" value={creds.google_key} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    <input name="google_model" type="text" placeholder="Model Name" value={creds.google_model} onChange={handleCredChange} className="w-full text-xs p-2 border border-zinc-800 rounded bg-black text-white focus:ring-1 focus:ring-emerald-500 outline-none" />
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-10 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">
                <header className="mb-12">
                    <h1 className="text-3xl font-bold text-white tracking-tight">Activity Stream</h1>
                    <p className="text-zinc-500 mt-2 font-light">Real-time analysis of customer life events and proactive outreach generation.</p>
                </header>

                {loading && (
                    <div className="flex flex-col items-center justify-center h-64 gap-6 animate-in fade-in duration-500">
                        <div className="w-16 h-16 border-4 border-zinc-800 border-t-emerald-500 rounded-full animate-spin"></div>
                        <div className="text-center">
                            <p className="text-sm font-bold text-white uppercase tracking-widest mb-2">Processing Event</p>
                            <div className="flex gap-2 text-[10px] text-zinc-500 font-mono">
                                <span className="bg-zinc-900 px-3 py-1 rounded border border-zinc-800 animate-pulse">RISK_CALC</span>
                                <span className="bg-zinc-900 px-3 py-1 rounded border border-zinc-800 animate-pulse delay-75">PRICING_ENGINE</span>
                                <span className="bg-zinc-900 px-3 py-1 rounded border border-zinc-800 animate-pulse delay-150">GENERATING_COPY</span>
                            </div>
                        </div>
                    </div>
                )}

                {!loading && !result && (
                    <div className="h-64 flex flex-col items-center justify-center border-2 border-dashed border-zinc-800 rounded-2xl text-zinc-600 bg-zinc-900/20">
                        <Activity className="w-12 h-12 mb-4 opacity-50" />
                        <span className="font-medium">Waiting for Event Simulation...</span>
                    </div>
                )}

                {result && !loading && (
                    <div className="max-w-4xl mx-auto space-y-8 animate-in slide-in-from-bottom-8 duration-700">

                        {/* Proposal Card */}
                        <div className="bg-zinc-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-zinc-800 overflow-hidden group">
                            <div className="bg-gradient-to-r from-emerald-600 to-emerald-800 px-8 py-5 flex justify-between items-center text-white relative overflow-hidden">
                                <div className="absolute top-0 right-0 -mr-4 -mt-4 w-24 h-24 bg-white opacity-10 rounded-full blur-xl"></div>
                                <span className="font-bold flex items-center gap-3 relative z-10 text-lg">
                                    <Shield className="w-5 h-5" /> Recommendation Engine
                                </span>
                                <span className="bg-black/30 backdrop-blur-md px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider relative z-10 border border-white/10">
                                    {result.proposal.policy_type}
                                </span>
                            </div>
                            <div className="p-8">
                                <h2 className="text-2xl font-bold text-white mb-4">{result.proposal.recommended_action}</h2>
                                <p className="text-zinc-400 mb-8 leading-relaxed text-lg font-light">{result.proposal.reasoning}</p>

                                <div className="grid grid-cols-2 gap-6">
                                    <div className="p-6 bg-black rounded-xl border border-zinc-800 group-hover:border-emerald-500/20 transition-colors">
                                        <span className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">Premium Adjustment</span>
                                        <span className={`text-3xl font-bold tracking-tight ${result.proposal.premium_change > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                            {result.proposal.premium_change > 0 ? '+' : ''}${result.proposal.premium_change}
                                        </span>
                                    </div>
                                    <div className="p-6 bg-black rounded-xl border border-zinc-800 group-hover:border-emerald-500/20 transition-colors">
                                        <span className="block text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-2">New Annual Total</span>
                                        <span className="text-3xl font-bold text-white tracking-tight">${result.proposal.new_total_premium}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Email Draft */}
                        <div className="bg-zinc-900/80 backdrop-blur-xl rounded-2xl shadow-xl border border-zinc-800 overflow-hidden">
                            <div className="px-8 py-5 border-b border-zinc-800 bg-black/40 flex justify-between items-center">
                                <h3 className="font-bold text-zinc-300 flex items-center gap-3">
                                    <Send className="w-4 h-4 text-emerald-500" /> Generated Outreach
                                </h3>
                                <span className="text-xs font-mono text-zinc-600">TEMPLATE: CLIENT_ENGAGEMENT</span>
                            </div>
                            <div className="p-8">
                                <div className="prose prose-invert max-w-none text-sm bg-black border border-zinc-800 rounded-xl p-8 font-medium text-zinc-300 leading-7 font-mono shadow-inner">
                                    {result.draft_message}
                                </div>
                                <div className="mt-8 flex justify-end gap-4">
                                    <button className="px-6 py-3 text-sm font-bold text-zinc-500 hover:text-white transition-colors">Discard Draft</button>
                                    <button className="px-8 py-3 text-sm font-bold bg-emerald-600 text-white rounded-xl hover:bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] hover:-translate-y-0.5 transition-all flex items-center gap-2">
                                        <Send className="w-4 h-4" /> Approve & Send
                                    </button>
                                </div>
                            </div>
                        </div>

                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
