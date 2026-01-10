import React, { useState } from 'react';
import { Shield, Upload, FileText, CheckCircle, AlertTriangle, Send, Settings, Book, Gavel, FileCheck } from 'lucide-react';
import axios from 'axios';

function App() {
    const [provider, setProvider] = useState('Azure OpenAI');
    const [showConfig, setShowConfig] = useState(false);
    const [credentials, setCredentials] = useState({
        api_key: '', endpoint: '', azure_deployment: '', azure_api_version: '',
        aws_access_key: '', aws_secret_key: '', aws_region: '', aws_model_id: '',
        google_key: '', google_model: ''
    });

    const [draftText, setDraftText] = useState("We are denying your claim because it doesn't meet our internal criteria. We used an AI system to decide this.");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    // Knowledge Base State
    const [kbSource, setKbSource] = useState('');
    const [kbText, setKbText] = useState('');
    const [kbLoading, setKbLoading] = useState(false);
    const [kbMessage, setKbMessage] = useState(null);

    const handleCredChange = (e) => {
        setCredentials({ ...credentials, [e.target.name]: e.target.value });
    };

    const handleScan = async () => {
        setLoading(true);
        setResult(null);
        try {
            const response = await axios.post('/api/scan', {
                draft_text: draftText,
                provider: provider,
                ...credentials
            });
            setResult(response.data);
        } catch (error) {
            console.error(error);
            alert('Error connecting to API');
        } finally {
            setLoading(false);
        }
    };

    const handleKbUpload = async () => {
        setKbLoading(true);
        setKbMessage(null);
        try {
            const formData = new FormData();
            formData.append('source', kbSource || 'Manual Entry');
            formData.append('text', kbText);

            const response = await axios.post('/api/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setKbMessage({ type: 'success', text: response.data.message });
            setKbText('');
            setKbSource('');
        } catch (error) {
            setKbMessage({ type: 'error', text: 'Failed to upload.' });
        } finally {
            setKbLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black flex font-sans text-slate-200 selection:bg-emerald-500/30">

            {/* Sidebar */}
            <div className="w-80 bg-zinc-950 border-r border-zinc-900 flex flex-col relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-32 bg-emerald-500/5 blur-[50px] pointer-events-none"></div>

                <div className="p-8 border-b border-zinc-900 relative z-10">
                    <div className="flex items-center gap-3 text-white font-bold text-xl tracking-tight">
                        <div className="p-2 bg-gradient-to-br from-emerald-600 to-emerald-900 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                            <Gavel className="w-5 h-5 text-emerald-100" />
                        </div>
                        <span>Regu<span className="text-emerald-500">Bot</span></span>
                    </div>
                    <p className="text-xs text-zinc-500 mt-2 font-mono ml-1">COMPLIANCE SENTINEL</p>
                </div>

                <div className="p-6 overflow-y-auto flex-1 space-y-8">

                    {/* Knowledge Base Section */}
                    <div>
                        <h3 className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Book className="w-3 h-3" /> Regulatory Ingestion
                        </h3>
                        <div className="space-y-3">
                            <input
                                value={kbSource}
                                onChange={(e) => setKbSource(e.target.value)}
                                placeholder="Regulation ID / Source"
                                className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none placeholder:text-zinc-700"
                            />
                            <textarea
                                value={kbText}
                                onChange={(e) => setKbText(e.target.value)}
                                placeholder="Paste regulatory text to update vector store..."
                                className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none h-24 placeholder:text-zinc-700 resize-none"
                            />
                            <button
                                onClick={handleKbUpload}
                                disabled={kbLoading || !kbText}
                                className="w-full py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-zinc-800 rounded-lg text-xs font-bold transition-all disabled:opacity-50"
                            >
                                {kbLoading ? 'Indexing...' : 'Update Knowledge Base'}
                            </button>
                            {kbMessage && (
                                <div className={`text-[10px] p-2 rounded border ${kbMessage.type === 'success' ? 'bg-emerald-950/30 border-emerald-900 text-emerald-400' : 'bg-rose-950/30 border-rose-900 text-rose-400'}`}>
                                    {kbMessage.text}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Config Toggle */}
                    <div>
                        <button
                            onClick={() => setShowConfig(!showConfig)}
                            className="flex items-center gap-2 text-xs text-zinc-500 hover:text-emerald-500 font-medium w-full transition-colors group"
                        >
                            <Settings className="w-4 h-4 group-hover:rotate-90 transition-transform" /> {showConfig ? 'Hide Config' : 'Model Configuration'}
                        </button>

                        {showConfig && (
                            <div className="mt-4 space-y-3 animate-in slide-in-from-left-2 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
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
                                        <input name="api_key" type="password" placeholder="API Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="endpoint" type="text" placeholder="Endpoint" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="azure_deployment" type="text" placeholder="Deployment" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="azure_api_version" type="text" placeholder="API Version" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    </div>
                                )}
                                {provider === 'AWS Bedrock' && (
                                    <div className="space-y-2">
                                        <input name="aws_access_key" type="password" placeholder="Access Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="aws_secret_key" type="password" placeholder="Secret Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="aws_region" type="text" placeholder="Region" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="aws_model_id" type="text" placeholder="Model ID" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    </div>
                                )}
                                {provider === 'Google Gemini' && (
                                    <div className="space-y-2">
                                        <input name="google_key" type="password" placeholder="API Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                        <input name="google_model" type="text" placeholder="Model Name" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-10 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">
                <header className="mb-10">
                    <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <FileCheck className="w-8 h-8 text-emerald-500" /> Compliance Scanner
                    </h1>
                    <p className="text-zinc-500 mt-2 font-light max-w-2xl">Use Retrieval-Augmented Generation (RAG) to scan outbound communications against the active regulatory knowledge base.</p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl">

                    {/* Input */}
                    <div className="bg-zinc-900/80 backdrop-blur-md p-8 rounded-2xl shadow-xl border border-zinc-800 flex flex-col h-[600px]">
                        <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <FileText className="w-4 h-4" /> Draft Communication
                        </h2>
                        <textarea
                            value={draftText}
                            onChange={(e) => setDraftText(e.target.value)}
                            className="flex-1 w-full bg-black border border-zinc-800 rounded-xl p-6 text-sm text-slate-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none resize-none leading-7 font-mono"
                            placeholder="Paste your draft email or letter here..."
                        />
                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={handleScan}
                                disabled={loading}
                                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all flex items-center gap-2 disabled:opacity-50"
                            >
                                {loading ? (
                                    <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Scanning...</>
                                ) : (
                                    <><Send className="w-4 h-4" /> Scan Compliance</>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Output */}
                    <div className="space-y-6 h-[600px] flex flex-col">
                        {!result && !loading && (
                            <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-zinc-800 rounded-2xl text-zinc-600">
                                <Shield className="w-12 h-12 mb-4 opacity-20" />
                                <span className="font-medium">Awaiting Input...</span>
                            </div>
                        )}

                        {loading && (
                            <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-zinc-800 rounded-2xl text-emerald-500">
                                <div className="w-16 h-16 border-4 border-zinc-800 border-t-emerald-500 rounded-full animate-spin mb-6"></div>
                                <span className="font-bold tracking-widest text-xs uppercase animate-pulse">Running Guardrails</span>
                            </div>
                        )}

                        {result && (
                            <div className="flex-1 overflow-y-auto pr-2 space-y-6 animate-in slide-in-from-bottom-8 duration-500">

                                {/* Status Banner */}
                                <div className={`p-6 rounded-2xl border flex items-center gap-4 ${result.compliance_status === 'VIOLATION'
                                        ? 'bg-rose-950/30 border-rose-500/30 shadow-[0_0_30px_rgba(244,63,94,0.1)]'
                                        : 'bg-emerald-950/30 border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.1)]'
                                    }`}>
                                    <div className={`p-3 rounded-full ${result.compliance_status === 'VIOLATION' ? 'bg-rose-500/10 text-rose-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                                        {result.compliance_status === 'VIOLATION' ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle className="w-6 h-6" />}
                                    </div>
                                    <div>
                                        <h3 className={`font-bold text-lg ${result.compliance_status === 'VIOLATION' ? 'text-rose-400' : 'text-emerald-400'}`}>
                                            {result.compliance_status}
                                        </h3>
                                        {result.feedback && <p className="text-sm text-zinc-400 mt-1">{result.feedback}</p>}
                                    </div>
                                </div>

                                {/* Rewritten Output */}
                                <div className="bg-zinc-900/50 rounded-xl border border-zinc-800 p-6">
                                    <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-4">
                                        {result.compliance_status === 'VIOLATION' ? 'Corrected Response' : 'Confimred Response'}
                                    </h3>
                                    <div className="text-sm leading-7 text-slate-300 font-mono bg-black/50 p-4 rounded-lg border border-zinc-800/50">
                                        {result.final_output}
                                    </div>
                                </div>

                                {/* Citations */}
                                {result.relevant_regulations?.length > 0 && (
                                    <div className="bg-zinc-900/50 rounded-xl border border-zinc-800 p-6">
                                        <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-4">Regulatory Citations</h3>
                                        <ul className="space-y-3">
                                            {result.relevant_regulations.map((reg, i) => (
                                                <li key={i} className="text-xs text-zinc-400 pl-4 border-l-2 border-emerald-500/30">
                                                    {reg}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
