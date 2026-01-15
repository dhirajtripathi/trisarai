import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowRight, Code2, FileJson, Layers, Rocket, CheckCircle, Terminal, UploadCloud, Settings, Save, X, Plus, Cpu, AlertCircle } from 'lucide-react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import yaml from 'react-syntax-highlighter/dist/esm/languages/hljs/yaml';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

SyntaxHighlighter.registerLanguage('yaml', yaml);

function App() {
    const [activeTab, setActiveTab] = useState('transform');

    // Dynamic Config
    const [platforms, setPlatforms] = useState([]);

    // Model Settings State - Initialized to prevent null errors
    const [config, setConfig] = useState({
        llm_provider: 'azure',
        azure_config: {
            endpoint: '',
            api_key: '',
            deployment_name: '',
            model_name: 'gpt-4',
            api_version: '2023-05-15'
        },
        aws_config: {
            region: 'us-east-1',
            profile_name: 'default',
            model_id: 'anthropic.claude-3-sonnet-20240229-v1:0',
            access_key_id: '',
            secret_access_key: ''
        },
        google_config: {
            project_id: '',
            location: 'us-central1',
            model_name: 'gemini-1.5-pro'
        }
    });
    const [modelLoading, setModelLoading] = useState(false);
    const [configLoaded, setConfigLoaded] = useState(false);

    // Transformation State
    const [sourceType, setSourceType] = useState('apigee');
    const [targetType, setTargetType] = useState('kong');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    // Prompt Management State
    const [prompts, setPrompts] = useState({});
    const [selectedPrompt, setSelectedPrompt] = useState(null);
    const [promptContent, setPromptContent] = useState('');
    const [promptLoading, setPromptLoading] = useState(false);

    // New Platform State
    const [showAddPlatform, setShowAddPlatform] = useState(false);
    const [newPlatformName, setNewPlatformName] = useState('');

    // Initial Load
    useEffect(() => {
        fetchPrompts();
        fetchConfig();
    }, []);

    const fetchPrompts = async () => {
        try {
            const res = await axios.get('http://localhost:8007/prompts');
            setPrompts(res.data);
            setPlatforms(Object.keys(res.data));
        } catch (err) {
            console.error("Failed to load prompts", err);
        }
    };

    const fetchConfig = async () => {
        try {
            const res = await axios.get('http://localhost:8007/config');
            if (res.data) {
                // Merge with default to ensure structural integrity
                setConfig(prev => ({ ...prev, ...res.data }));
            }
            setConfigLoaded(true);
        } catch (err) {
            console.error("Failed to load config", err);
            // Even if fail, mark loaded so UI shows (with defaults)
            setConfigLoaded(true);
        }
    };

    // --- Configuration Handlers ---
    const handleConfigUpdate = async () => {
        setModelLoading(true);
        try {
            await axios.post('http://localhost:8007/config', config);
            alert("Configuration Saved Successfully!");
        } catch (err) {
            alert("Failed to save config: " + err.message);
        } finally {
            setModelLoading(false);
        }
    };

    const handleProviderChange = (provider) => {
        setConfig({ ...config, llm_provider: provider });
    };

    // --- Transformation Handlers ---
    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleTransform = async () => {
        if (!file) {
            setError("Please upload a source file first.");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('source_type', sourceType);
        formData.append('target_type', targetType);

        try {
            const res = await axios.post('http://localhost:8007/transform', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(res.data);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Transformation Failed");
        } finally {
            setLoading(false);
        }
    };

    // --- Prompt Handlers ---
    const handleSelectPrompt = async (platform, name) => {
        setSelectedPrompt({ platform, name });
        setPromptLoading(true);
        try {
            const res = await axios.get(`http://localhost:8007/prompts/${platform}/${name}`);
            setPromptContent(res.data.content);
        } catch (err) {
            console.error(err);
        } finally {
            setPromptLoading(false);
        }
    };

    const handleSavePrompt = async () => {
        if (!selectedPrompt) return;
        try {
            await axios.post(`http://localhost:8007/prompts/${selectedPrompt.platform}/${selectedPrompt.name}`, {
                content: promptContent
            });
            alert("Prompt saved successfully!");
        } catch (err) {
            alert("Failed to save prompt");
            console.error(err);
        }
    };

    const handleAddPlatform = async () => {
        if (!newPlatformName) return;
        try {
            await axios.post(`http://localhost:8007/platforms/${newPlatformName}`);
            setNewPlatformName('');
            setShowAddPlatform(false);
            fetchPrompts(); // Refresh list
        } catch (err) {
            alert("Failed to create platform: " + (err.response?.data?.detail || err.message));
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 p-8 font-sans text-slate-100">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Header */}
                <div className="flex items-center justify-between border-b border-slate-700 pb-6">
                    <div className="flex items-center gap-4">
                        <div className="bg-blue-600 p-3 rounded-xl shadow-lg shadow-blue-900/50">
                            <Layers className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                                API Transformation Agent
                            </h1>
                            <p className="text-slate-400">Universal API Migration Utility (Any-to-Any)</p>
                        </div>
                    </div>

                    <div className="flex bg-slate-800 rounded-lg p-1">
                        <button
                            onClick={() => setActiveTab('transform')}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'transform' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                        >
                            Transformation
                        </button>
                        <button
                            onClick={() => setActiveTab('prompts')}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'prompts' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                        >
                            <Settings className="w-4 h-4" /> Prompts
                        </button>
                        <button
                            onClick={() => setActiveTab('models')}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'models' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                        >
                            <Cpu className="w-4 h-4" /> Models
                        </button>
                    </div>
                </div>

                {/* --- TRANSFORMATION VIEW --- */}
                {activeTab === 'transform' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1 space-y-6">

                            {/* Source Config */}
                            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><FileJson className="w-5 h-5 text-blue-400" /> Source System</h2>
                                <div className="space-y-4">
                                    <div>
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Platform</label>
                                        <select
                                            value={sourceType}
                                            onChange={(e) => setSourceType(e.target.value)}
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm focus:border-blue-500 focus:outline-none"
                                        >
                                            {platforms.map(p => (
                                                <option key={p} value={p}>{p.toUpperCase()}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="border-2 border-dashed border-slate-700 rounded-xl p-6 text-center hover:border-blue-500/50 transition-colors bg-slate-900/50">
                                        <input
                                            type="file"
                                            id="file-upload"
                                            className="hidden"
                                            onChange={handleFileChange}
                                            accept=".zip,.xml,.yaml,.yml,.json,.tf,.txt,.conf"
                                        />
                                        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-2">
                                            <UploadCloud className="w-8 h-8 text-slate-400" />
                                            <span className="text-sm font-bold text-slate-300">
                                                {file ? file.name : "Click to Upload Config"}
                                            </span>
                                            <span className="text-xs text-slate-500">
                                                {file ? `${(file.size / 1024).toFixed(1)} KB` : "Supports Any Config File"}
                                            </span>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            {/* Target Config */}
                            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Terminal className="w-5 h-5 text-emerald-400" /> Target System</h2>
                                <div className="space-y-4">
                                    <div>
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Platform</label>
                                        <select
                                            value={targetType}
                                            onChange={(e) => setTargetType(e.target.value)}
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm focus:border-emerald-500 focus:outline-none"
                                        >
                                            {platforms.map(p => (
                                                <option key={p} value={p}>{p.toUpperCase()}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <button
                                        onClick={handleTransform}
                                        disabled={loading}
                                        className="w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-900/20 transition-all flex items-center justify-center gap-2"
                                    >
                                        {loading ? <Rocket className="w-5 h-5 animate-bounce" /> : <Rocket className="w-5 h-5" />}
                                        {loading ? "Transforming..." : "Start Migration"}
                                    </button>
                                </div>
                            </div>

                            {result && (
                                <div className="bg-emerald-900/20 border border-emerald-500/20 rounded-2xl p-6">
                                    <h3 className="text-emerald-400 font-bold mb-2 flex items-center gap-2"><CheckCircle className="w-4 h-4" /> Transformation Complete</h3>
                                    <div className="text-xs text-slate-400 space-y-1">
                                        <p>Source Detected: <span className="text-white">{result.metadata.source}</span></p>
                                        <p>Target Generated: <span className="text-white">{result.target}</span></p>
                                    </div>
                                </div>
                            )}

                            {error && (
                                <div className="bg-red-900/20 border border-red-500/20 rounded-2xl p-6 text-red-400 text-sm">
                                    <strong>Error:</strong> {error}
                                </div>
                            )}
                        </div>

                        {/* Results View */}
                        <div className="lg:col-span-2">
                            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 h-full min-h-[500px] flex flex-col">
                                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Code2 className="w-5 h-5 text-slate-400" /> Generated Configuration</h2>
                                <div className="flex-1 bg-slate-950 rounded-xl overflow-hidden border border-slate-800 relative">
                                    {result ? (
                                        <SyntaxHighlighter
                                            language={targetType === 'kong' ? 'yaml' : 'hcl'}
                                            style={atomOneDark}
                                            customStyle={{ background: 'transparent', padding: '1.5rem', fontSize: '0.9rem' }}
                                            showLineNumbers={true}
                                        >
                                            {result.config_content}
                                        </SyntaxHighlighter>
                                    ) : (
                                        <div className="absolute inset-0 flex items-center justify-center text-slate-600">
                                            <div className="text-center">
                                                <Layers className="w-12 h-12 mx-auto mb-3 opacity-20" />
                                                <p>Select source file and start transformation...</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* --- PROMPTS VIEW --- */}
                {activeTab === 'prompts' && (
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[600px]">
                        {/* Sidebar List */}
                        <div className="lg:col-span-1 bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden flex flex-col">
                            <div className="p-4 border-b border-slate-700 bg-slate-800/80 flex justify-between items-center">
                                <h2 className="font-bold text-slate-200">Prompts</h2>
                                <button onClick={() => setShowAddPlatform(true)} className="p-1 hover:bg-slate-700 rounded text-blue-400" title="Add Platform">
                                    <Plus className="w-5 h-5" />
                                </button>
                            </div>

                            {showAddPlatform && (
                                <div className="p-3 bg-slate-800 border-b border-slate-700">
                                    <input
                                        autoFocus
                                        placeholder="Platform Name (e.g. aws)"
                                        className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm mb-2 focus:border-blue-500 outline-none"
                                        value={newPlatformName}
                                        onChange={e => setNewPlatformName(e.target.value)}
                                    />
                                    <div className="flex gap-2">
                                        <button onClick={handleAddPlatform} className="text-xs bg-blue-600 px-2 py-1 rounded text-white flex-1">Add</button>
                                        <button onClick={() => setShowAddPlatform(false)} className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300">Cancel</button>
                                    </div>
                                </div>
                            )}

                            <div className="flex-1 overflow-y-auto p-2 space-y-4">
                                {Object.entries(prompts).map(([platform, files]) => (
                                    <div key={platform}>
                                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2 mb-2">{platform}</h3>
                                        <div className="space-y-1">
                                            {files.map(file => (
                                                <button
                                                    key={file}
                                                    onClick={() => handleSelectPrompt(platform, file)}
                                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${selectedPrompt?.name === file && selectedPrompt?.platform === platform ? 'bg-blue-600/20 text-blue-400 border border-blue-600/30' : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200'}`}
                                                >
                                                    {file}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Editor Area */}
                        <div className="lg:col-span-3 bg-slate-800/50 border border-slate-700 rounded-2xl flex flex-col overflow-hidden">
                            {selectedPrompt ? (
                                <>
                                    <div className="p-4 border-b border-slate-700 bg-slate-800/80 flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="bg-slate-700 text-xs px-2 py-1 rounded text-slate-300">{selectedPrompt.platform}</span>
                                            <span className="font-mono text-sm font-bold text-blue-300">{selectedPrompt.name}</span>
                                        </div>
                                        <button
                                            onClick={handleSavePrompt}
                                            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
                                        >
                                            <Save className="w-4 h-4" /> Save Changes
                                        </button>
                                    </div>
                                    <div className="flex-1 relative">
                                        {promptLoading ? (
                                            <div className="absolute inset-0 flex items-center justify-center text-slate-500">Loading...</div>
                                        ) : (
                                            <textarea
                                                value={promptContent}
                                                onChange={(e) => setPromptContent(e.target.value)}
                                                className="w-full h-full bg-slate-950 p-6 font-mono text-sm text-slate-300 focus:outline-none resize-none"
                                                spellCheck="false"
                                            />
                                        )}
                                    </div>
                                </>
                            ) : (
                                <div className="flex-1 flex items-center justify-center text-slate-600">
                                    <p>Select a prompt to edit</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* --- MODELS VIEW --- */}
                {activeTab === 'models' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {!configLoaded ? (
                            <div className="col-span-3 text-center py-20 text-slate-500">
                                <Rocket className="w-10 h-10 mx-auto mb-4 animate-spin opacity-50" />
                                <p>Loading Configuration...</p>
                                <button onClick={fetchConfig} className="mt-4 text-blue-400 text-sm hover:underline">Retry</button>
                            </div>
                        ) : (
                            <>
                                {/* Provider Select */}
                                <div className="col-span-1 space-y-4">
                                    {['azure', 'aws', 'google'].map(p => (
                                        <div
                                            key={p}
                                            onClick={() => handleProviderChange(p)}
                                            className={`p-4 rounded-xl border cursor-pointer transition-all ${config.llm_provider === p ? 'bg-blue-600/20 border-blue-500 shadow-lg shadow-blue-900/20' : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800'}`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`w-4 h-4 rounded-full border-2 ${config.llm_provider === p ? 'border-blue-400 bg-blue-400' : 'border-slate-500'}`} />
                                                <span className="font-bold text-lg capitalize">{p}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Config Form */}
                                <div className="md:col-span-2 bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
                                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                        <Cpu className="w-5 h-5 text-blue-400" />
                                        Configure {config.llm_provider ? config.llm_provider.toUpperCase() : "LLM"}
                                    </h2>

                                    <div className="space-y-4">
                                        {config.llm_provider === 'azure' && (
                                            <>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="col-span-2">
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Azure Endpoint</label>
                                                        <input
                                                            value={config.azure_config?.endpoint || ''}
                                                            onChange={(e) => setConfig({ ...config, azure_config: { ...config.azure_config, endpoint: e.target.value } })}
                                                            placeholder="https://your-resource.openai.azure.com/"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div className="col-span-2">
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">API Key</label>
                                                        <input
                                                            type="password"
                                                            value={config.azure_config?.api_key || ''}
                                                            onChange={(e) => setConfig({ ...config, azure_config: { ...config.azure_config, api_key: e.target.value } })}
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Deployment Name</label>
                                                        <input
                                                            value={config.azure_config?.deployment_name || ''}
                                                            onChange={(e) => setConfig({ ...config, azure_config: { ...config.azure_config, deployment_name: e.target.value } })}
                                                            placeholder="gpt-4-deployment"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">API Version</label>
                                                        <input
                                                            value={config.azure_config?.api_version || ''}
                                                            onChange={(e) => setConfig({ ...config, azure_config: { ...config.azure_config, api_version: e.target.value } })}
                                                            placeholder="2023-05-15"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div className="col-span-2">
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Model Name (Optional)</label>
                                                        <input
                                                            value={config.azure_config?.model_name || ''}
                                                            onChange={(e) => setConfig({ ...config, azure_config: { ...config.azure_config, model_name: e.target.value } })}
                                                            placeholder="gpt-4"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                </div>
                                            </>
                                        )}

                                        {config.llm_provider === 'aws' && (
                                            <>
                                                <div className="bg-blue-900/10 border border-blue-500/20 p-3 rounded mb-2 text-xs text-blue-300">
                                                    <AlertCircle className="w-3 h-3 inline mr-1" />
                                                    Use Profile Name for local credentials (e.g. `~/.aws/credentials`). Or enter Keys below.
                                                </div>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">AWS Profile Name</label>
                                                        <input
                                                            value={config.aws_config?.profile_name || ''}
                                                            onChange={(e) => setConfig({ ...config, aws_config: { ...config.aws_config, profile_name: e.target.value } })}
                                                            placeholder="default"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Region</label>
                                                        <input
                                                            value={config.aws_config?.region || ''}
                                                            onChange={(e) => setConfig({ ...config, aws_config: { ...config.aws_config, region: e.target.value } })}
                                                            placeholder="us-east-1"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div className="col-span-2">
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Model ID (Bedrock)</label>
                                                        <input
                                                            value={config.aws_config?.model_id || ''}
                                                            onChange={(e) => setConfig({ ...config, aws_config: { ...config.aws_config, model_id: e.target.value } })}
                                                            placeholder="anthropic.claude-3-sonnet-20240229-v1:0"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Access Key ID (Optional)</label>
                                                        <input
                                                            value={config.aws_config?.access_key_id || ''}
                                                            onChange={(e) => setConfig({ ...config, aws_config: { ...config.aws_config, access_key_id: e.target.value } })}
                                                            type="password"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Secret Access Key (Optional)</label>
                                                        <input
                                                            value={config.aws_config?.secret_access_key || ''}
                                                            onChange={(e) => setConfig({ ...config, aws_config: { ...config.aws_config, secret_access_key: e.target.value } })}
                                                            type="password"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                </div>
                                            </>
                                        )}

                                        {config.llm_provider === 'google' && (
                                            <>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Project ID</label>
                                                        <input
                                                            value={config.google_config?.project_id || ''}
                                                            onChange={(e) => setConfig({ ...config, google_config: { ...config.google_config, project_id: e.target.value } })}
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Location</label>
                                                        <input
                                                            value={config.google_config?.location || ''}
                                                            onChange={(e) => setConfig({ ...config, google_config: { ...config.google_config, location: e.target.value } })}
                                                            placeholder="us-central1"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                    <div className="col-span-2">
                                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">Model Name</label>
                                                        <input
                                                            value={config.google_config?.model_name || ''}
                                                            onChange={(e) => setConfig({ ...config, google_config: { ...config.google_config, model_name: e.target.value } })}
                                                            placeholder="gemini-1.5-pro"
                                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm focus:border-blue-500 outline-none"
                                                        />
                                                    </div>
                                                </div>
                                            </>
                                        )}

                                        <div className="pt-4">
                                            <button
                                                onClick={handleConfigUpdate}
                                                disabled={modelLoading}
                                                className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-900/30"
                                            >
                                                {modelLoading ? <Rocket className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                                                Save Configuration
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
}

export default App;
