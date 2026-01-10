import React, { useState } from 'react';
import { Upload, FileCode, ArrowRight, ArrowLeft, CheckCircle, Database, Layers, Play, Settings, RefreshCw, FileText, Edit3, Save, Plus, BookOpen, Trash2 } from 'lucide-react';
import axios from 'axios';

function App() {
  const [stage, setStage] = useState('UPLOAD'); // UPLOAD, SRS, ARCH, CODE, PROMPTS
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState(null);

  // Inputs
  const [sourceSys, setSourceSys] = useState('webmethods');
  const [targetSys, setTargetSys] = useState('springboot');
  const [files, setFiles] = useState([]);

  // Results
  const [srsContent, setSrsContent] = useState('');
  const [archContent, setArchContent] = useState('');
  const [codeContent, setCodeContent] = useState('');
  const [testContent, setTestContent] = useState('');

  // Config
  const [provider, setProvider] = useState('Azure OpenAI');
  const [showConfig, setShowConfig] = useState(false);
  const [creds, setCreds] = useState({});

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleCredChange = (e) => {
    setCreds({ ...creds, [e.target.name]: e.target.value });
  };

  const startAnalysis = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('source_system', sourceSys);
    formData.append('target_system', targetSys);
    formData.append('provider', provider);
    // Add credentials as JSON string or individual fields ideally, 
    // but for PoC we rely on env vars or manual update if needed
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await axios.post('/cases', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setThreadId(res.data.thread_id);
      pollStatus(res.data.thread_id);
    } catch (e) {
      alert('Failed to start analysis');
      setLoading(false);
    }
  };

  const pollStatus = async (tid) => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`/cases/${tid}`);
        const values = res.data.values;

        if (values.srs_content && stage === 'UPLOAD') {
          setSrsContent(values.srs_content);
          setStage('SRS');
          setLoading(false);
          clearInterval(interval);
        }

        if (values.generated_code && stage === 'ARCH') {
          setCodeContent(values.generated_code);
          setTestContent(values.test_cases);
          setStage('CODE');
          setLoading(false);
          clearInterval(interval);
        }

      } catch (e) {
        console.error("Poll error", e);
      }
    }, 2000);
  };

  const approveSRS = async () => {
    setLoading(true);
    setStage('ARCH'); // Optimistic UI
    try {
      await axios.post(`/cases/${threadId}/approve`);
      pollStatus(threadId); // Start polling for code
    } catch (e) {
      alert("Approval failed");
      setLoading(false);
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
              <RefreshCw className="w-5 h-5 text-emerald-100" />
            </div>
            <span>Migration<span className="text-emerald-500">AI</span></span>
          </div>
          <p className="text-[10px] text-zinc-500 mt-2 font-mono ml-1 uppercase tracking-wider">LEGACY MODERNIZATION ENGINE</p>
        </div>

        <div className="p-6 space-y-8 overflow-y-auto">

          {/* Steps */}
          <div>
            <h3 className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-4">Migration Pipeline</h3>
            <div className="space-y-4">
              <div className={`p-3 rounded-xl border flex items-center gap-3 ${stage === 'UPLOAD' ? 'bg-emerald-900/20 border-emerald-500/50 text-emerald-400' : 'bg-zinc-900/50 border-zinc-800 text-zinc-500'}`}>
                <Upload className="w-4 h-4" /> <span className="text-xs font-bold">1. Ingestion</span>
              </div>
              <div className={`p-3 rounded-xl border flex items-center gap-3 ${stage === 'SRS' ? 'bg-emerald-900/20 border-emerald-500/50 text-emerald-400' : (stage === 'UPLOAD' ? 'bg-zinc-900/50 border-zinc-800 text-zinc-700' : 'bg-emerald-900/10 border-emerald-500/20 text-emerald-600')}`}>
                <FileText className="w-4 h-4" /> <span className="text-xs font-bold">2. Reverse Engineer</span>
              </div>
              <div className={`p-3 rounded-xl border flex items-center gap-3 ${stage === 'ARCH' ? 'bg-emerald-900/20 border-emerald-500/50 text-emerald-400' : (stage === 'CODE' ? 'bg-emerald-900/10 border-emerald-500/20 text-emerald-600' : 'bg-zinc-900/50 border-zinc-800 text-zinc-700')}`}>
                <Layers className="w-4 h-4" /> <span className="text-xs font-bold">3. Architecture</span>
              </div>
              <div className={`p-3 rounded-xl border flex items-center gap-3 ${stage === 'CODE' ? 'bg-emerald-900/20 border-emerald-500/50 text-emerald-400' : 'bg-zinc-900/50 border-zinc-800 text-zinc-700'}`}>
                <FileCode className="w-4 h-4" /> <span className="text-xs font-bold">4. Forward Engineer</span>
              </div>
            </div>
          </div>

          {/* Config */}
          <div>
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="flex items-center gap-2 text-xs text-zinc-500 hover:text-emerald-500 font-medium w-full transition-colors group"
            >
              <Settings className="w-4 h-4 group-hover:rotate-90 transition-transform" /> {showConfig ? 'Hide Config' : 'Configure LLM'}
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
                    <input name="azure_key" type="password" placeholder="API Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="azure_endpoint" type="text" placeholder="Endpoint URL" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="azure_deployment" type="text" placeholder="Deployment Name" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="azure_api_version" type="text" placeholder="API Version (2023-05-15)" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                  </div>
                )}

                {provider === 'AWS Bedrock' && (
                  <div className="space-y-2">
                    <input name="aws_access_key" type="password" placeholder="Access Key ID" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="aws_secret_key" type="password" placeholder="Secret Access Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="aws_region" type="text" placeholder="Region (us-east-1)" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="aws_model_id" type="text" placeholder="Model ID (anthropic.claude-v2)" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                  </div>
                )}

                {provider === 'Google Gemini' && (
                  <div className="space-y-2">
                    <input name="google_key" type="password" placeholder="Google API Key" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                    <input name="google_model" type="text" placeholder="Model Name (gemini-pro)" onChange={handleCredChange} className="w-full text-xs p-2 bg-black border border-zinc-800 rounded text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Prompt Library Toggle */}
          <div className="mt-8 pt-6 border-t border-zinc-900 space-y-2">
            <button
              onClick={() => setStage('PROMPTS')}
              className={`flex items-center gap-3 w-full p-3 rounded-xl transition-all ${stage === 'PROMPTS' ? 'bg-emerald-900/20 text-emerald-400' : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900'}`}
            >
              <Edit3 className="w-5 h-5" />
              <span className="text-sm font-bold">Prompt Library</span>
            </button>
            <button
              onClick={() => setStage('KB')}
              className={`flex items-center gap-3 w-full p-3 rounded-xl transition-all ${stage === 'KB' ? 'bg-emerald-900/20 text-emerald-400' : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900'}`}
            >
              <BookOpen className="w-5 h-5" />
              <span className="text-sm font-bold">Knowledge Base</span>
            </button>
          </div>

        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-10 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">

        {stage === 'PROMPTS' && <PromptLibrary onBack={() => setStage('UPLOAD')} />}
        {stage === 'KB' && <KnowledgeBase onBack={() => setStage('UPLOAD')} />}

        {stage === 'UPLOAD' && (
          <div className="max-w-2xl mx-auto mt-20 text-center animate-in fade-in zoom-in duration-500">
            <div className="w-24 h-24 bg-zinc-900 rounded-full flex items-center justify-center mx-auto mb-8 border border-zinc-800 shadow-2xl">
              <Database className="w-10 h-10 text-emerald-500" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-4 tracking-tight">System Migration</h1>
            <p className="text-zinc-500 mb-10 max-w-lg mx-auto">Upload legacy source files to generate comprehensive SRS and auto-migrate to modern architecture.</p>

            <div className="bg-zinc-900/50 p-8 rounded-2xl border border-zinc-800 backdrop-blur-sm shadow-xl">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-left">
                  <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block mb-2">From (Legacy)</label>
                  <select value={sourceSys} onChange={(e) => setSourceSys(e.target.value)} className="w-full p-3 rounded-xl bg-black border border-zinc-800 text-sm font-bold text-white focus:ring-1 focus:ring-emerald-500 outline-none">
                    <option value="webmethods">Software AG WebMethods</option>
                    <option value="tibco">TIBCO BW</option>
                  </select>
                </div>
                <div className="text-left">
                  <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block mb-2">To (Target)</label>
                  <select value={targetSys} onChange={(e) => setTargetSys(e.target.value)} className="w-full p-3 rounded-xl bg-black border border-zinc-800 text-sm font-bold text-white focus:ring-1 focus:ring-emerald-500 outline-none">
                    <option value="springboot">Spring Boot 3.x</option>
                    <option value="aws_lambda">AWS Lambda (Node.js)</option>
                  </select>
                </div>
              </div>

              <div className="border-2 border-dashed border-zinc-800 rounded-xl p-8 hover:border-emerald-500/50 transition-colors cursor-pointer bg-black/50 group text-center relative">
                <input type="file" multiple onChange={handleFileChange} className="absolute inset-0 opacity-0 cursor-pointer" />
                <Upload className="w-8 h-8 text-zinc-600 group-hover:text-emerald-500 mx-auto mb-3 transition-colors" />
                <p className="text-sm text-zinc-400 font-medium">{files.length > 0 ? `${files.length} files selected` : "Drag source files (XML, Java) here"}</p>
              </div>

              <button
                onClick={startAnalysis}
                disabled={loading || files.length === 0}
                className="mt-6 w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : <><Play className="w-5 h-5 fill-current" /> Initialize Analysis</>}
              </button>
            </div>
          </div>
        )}

        {stage === 'SRS' && (
          <div className="max-w-5xl mx-auto space-y-6 animate-in slide-in-from-bottom-8 duration-500">
            <header className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-3"><FileText className="w-6 h-6 text-emerald-500" /> SRS Generated</h2>
                <p className="text-zinc-500 text-sm mt-1">Review the reverse-engineered requirements before proceeding.</p>
              </div>
            </header>

            <div className="prose prose-invert max-w-none text-sm bg-zinc-900/50 p-8 rounded-2xl border border-zinc-800 font-mono leading-relaxed shadow-xl">
              <pre className="whitespace-pre-wrap">{srsContent}</pre>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <button className="px-6 py-3 text-zinc-400 hover:text-white font-bold text-sm transition-colors">Reject & Iterate</button>
              <button
                onClick={approveSRS}
                disabled={loading}
                className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl flex items-center gap-2 shadow-[0_0_20px_rgba(16,185,129,0.2)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all"
              >
                {loading ? 'Generating Code...' : <><CheckCircle className="w-4 h-4" /> Approve & Generate Architecture</>}
              </button>
            </div>
          </div>
        )}

        {stage === 'CODE' && (
          <div className="max-w-6xl mx-auto animate-in fade-in zoom-in duration-500">
            <header className="mb-8 text-center">
              <div className="inline-flex items-center gap-2 text-emerald-500 font-mono text-xs font-bold uppercase tracking-widest mb-4 bg-emerald-500/10 px-4 py-2 rounded-full border border-emerald-500/20">
                <CheckCircle className="w-3 h-3" /> Migration Complete
              </div>
              <h1 className="text-3xl font-bold text-white">Target Artifacts</h1>
            </header>

            <div className="grid grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
                  <div className="px-6 py-4 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between">
                    <span className="text-sm font-bold text-emerald-400 flex items-center gap-2"><FileCode className="w-4 h-4" /> Source Code</span>
                    <span className="text-xs text-zinc-600 font-mono">JAVA / SPRING BOOT</span>
                  </div>
                  <div className="p-6 overflow-x-auto">
                    <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap">{codeContent}</pre>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
                  <div className="px-6 py-4 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between">
                    <span className="text-sm font-bold text-blue-400 flex items-center gap-2"><CheckCircle className="w-4 h-4" /> Unit Tests</span>
                    <span className="text-xs text-zinc-600 font-mono">JUNIT 5</span>
                  </div>
                  <div className="p-6 overflow-x-auto">
                    <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap">{testContent}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

function PromptLibrary({ onBack }) {
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);

  // New Prompt State
  const [isCreating, setIsCreating] = useState(false);
  const [newPath, setNewPath] = useState('');

  const fetchPrompts = () => {
    axios.get('/prompts').then(res => setPrompts(res.data.prompts));
  };

  React.useEffect(() => {
    fetchPrompts();
  }, []);

  const loadPrompt = async (path) => {
    setIsCreating(false);
    setSelectedPrompt(path);
    const formData = new FormData();
    formData.append('path', path);
    const res = await axios.post('/prompts/content', formData);
    setContent(res.data.content);
  };

  const startCreating = () => {
    setIsCreating(true);
    setSelectedPrompt(null);
    setContent('');
    setNewPath('source/new_system/srs_generation.txt');
  };

  const savePrompt = async () => {
    setSaving(true);
    const path = isCreating ? newPath : selectedPrompt;

    try {
      await axios.post('/prompts/save', { path, content });
      alert('Prompt saved successfully!');
      if (isCreating) {
        setIsCreating(false);
        fetchPrompts(); // Refresh list to show new file
        setSelectedPrompt(path);
      }
    } catch (e) {
      alert('Failed to save prompt');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-500">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-zinc-500 hover:text-emerald-500 text-xs font-bold uppercase tracking-wider mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Edit3 className="w-8 h-8 text-emerald-500" /> Prompt Engineering
          </h1>
          <p className="text-zinc-500 mt-2 font-light">Customize the context engineering instructions for each migration stage.</p>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-6 h-[600px]">
        {/* List */}
        <div className="col-span-4 bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 overflow-y-auto flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Available Prompts</h3>
            <button onClick={startCreating} className="p-1 hover:bg-zinc-800 rounded text-emerald-500 hover:text-emerald-400">
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2 flex-1">
            {prompts.map(p => (
              <button
                key={p}
                onClick={() => loadPrompt(p)}
                className={`w-full text-left p-3 rounded-lg text-sm font-mono truncate transition-all ${selectedPrompt === p ? 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/30' : 'text-zinc-400 hover:bg-zinc-800'}`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Editor */}
        <div className="col-span-8 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col">
          {(selectedPrompt || isCreating) ? (
            <>
              <div className="px-6 py-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-950">
                {isCreating ? (
                  <input
                    type="text"
                    value={newPath}
                    onChange={(e) => setNewPath(e.target.value)}
                    className="bg-black border border-zinc-700 rounded p-2 text-sm font-mono text-emerald-500 w-96 focus:ring-1 focus:ring-emerald-500 outline-none"
                  />
                ) : (
                  <span className="text-xs font-mono text-emerald-500">{selectedPrompt}</span>
                )}

                <button
                  onClick={savePrompt}
                  disabled={saving}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center gap-2"
                >
                  <Save className="w-3 h-3" /> {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="flex-1 bg-black p-6 font-mono text-sm text-slate-300 resize-none outline-none focus:bg-zinc-950/50 transition-colors leading-relaxed"
                spellCheck="false"
                placeholder={isCreating ? "Enter prompt template content here..." : ""}
              />
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-zinc-600">
              Select a prompt to edit or create new
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function KnowledgeBase({ onBack }) {
  const [platform, setPlatform] = useState('webmethods');
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const fetchFiles = () => {
    axios.get(`/kb/${platform}`).then(res => setFiles(res.data.files));
  };

  React.useEffect(() => {
    fetchFiles();
  }, [platform]);

  const handleUpload = async (e) => {
    if (!e.target.files.length) return;
    setUploading(true);
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`/kb/${platform}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchFiles();
    } catch (e) {
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-500">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-zinc-500 hover:text-emerald-500 text-xs font-bold uppercase tracking-wider mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-emerald-500" /> VectorDB Ingestion
          </h1>
          <p className="text-zinc-500 mt-2 font-light">Upload technical documentation or legacy code patterns to the RAG engine.</p>
        </div>

        <div className="flex items-center gap-4">
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="bg-black border border-zinc-800 text-white p-2 rounded-lg text-sm outline-none focus:ring-1 focus:ring-emerald-500"
          >
            <option value="webmethods">WebMethods</option>
            <option value="tibco">TIBCO</option>
            <option value="springboot">Spring Boot</option>
            <option value="aws_lambda">AWS Lambda</option>
          </select>
        </div>
      </header>

      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-8">
        <div className="border-2 border-dashed border-zinc-800 rounded-xl p-8 hover:border-emerald-500/50 transition-colors cursor-pointer bg-black/20 group text-center relative mb-8">
          <input type="file" onChange={handleUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
          <Upload className="w-8 h-8 text-zinc-600 group-hover:text-emerald-500 mx-auto mb-3 transition-colors" />
          <p className="text-sm text-zinc-400 font-medium">
            {uploading ? "Uploading to VectorDB..." : `Upload ${platform} Knowledge (PDF, TXT, MD)`}
          </p>
        </div>

        <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-4">Indexed Documents</h3>
        {files.length === 0 ? (
          <p className="text-zinc-600 text-sm italic">No documents indexed for this platform.</p>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {files.map(f => (
              <div key={f} className="p-4 bg-zinc-950 border border-zinc-900 rounded-lg flex items-center gap-3">
                <FileText className="w-4 h-4 text-emerald-500" />
                <span className="text-sm text-zinc-300 font-mono truncate">{f}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
