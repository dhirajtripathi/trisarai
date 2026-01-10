import React, { useState } from 'react';
import { Camera, Mic, CheckCircle, AlertTriangle, XCircle, Settings, Play, ChevronRight, Shield } from 'lucide-react';
import axios from 'axios';

function App() {
  const [imageStatus, setImageStatus] = useState('clear');
  const [transcript, setTranscript] = useState("I was driving on the highway and a rock hit my windshield. It's cracked.");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Configuration
  const [provider, setProvider] = useState('Azure OpenAI');
  const [showConfig, setShowConfig] = useState(false);
  const [creds, setCreds] = useState({
    azure_key: '', azure_endpoint: '',
    aws_access_key: '', aws_secret_key: '', aws_region: 'us-east-1', aws_model_id: 'anthropic.claude-v2',
    google_key: '', google_model: 'gemini-pro'
  });

  const handleCredChange = (e) => {
    setCreds({ ...creds, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await axios.post('/api/submit', {
        image_status: imageStatus,
        voice_transcript: transcript,
        provider: provider,
        credentials: creds
      });
      setResult(res.data);
    } catch (err) {
      alert('Error extracting claim data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex font-sans text-slate-200 selection:bg-emerald-500/30">

      {/* Sidebar Config */}
      <div className="w-80 bg-zinc-950 border-r border-zinc-900 flex flex-col relative overflow-hidden">
        {/* Glow */}
        <div className="absolute top-0 left-0 w-full h-32 bg-emerald-500/5 blur-[50px] pointer-events-none"></div>

        <div className="p-8 border-b border-zinc-900 relative z-10">
          <div className="flex items-center gap-3 text-white font-bold text-xl tracking-tight">
            <div className="p-2 bg-gradient-to-br from-emerald-600 to-emerald-800 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.3)]">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span>Claims<span className="text-emerald-500">AI</span></span>
          </div>
          <p className="text-xs text-zinc-500 mt-2 font-mono ml-1">FNOL AUTONOMOUS UNIT</p>
        </div>

        <div className="p-6">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="flex items-center gap-2 text-xs text-zinc-400 hover:text-emerald-400 font-medium w-full mb-6 transition-colors group"
          >
            <Settings className="w-4 h-4 group-hover:rotate-90 transition-transform" /> {showConfig ? 'Hide Protocol Config' : 'Configure Neural Link'}
          </button>

          {showConfig && (
            <div className="space-y-4 animate-in slide-in-from-left-2 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none"
              >
                <option>Azure OpenAI</option>
                <option>AWS Bedrock</option>
                <option>Google Gemini</option>
              </select>

              {provider === 'Azure OpenAI' && (
                <div className="space-y-3">
                  <input name="azure_key" type="password" placeholder="API Key" value={creds.azure_key} onChange={handleCredChange} className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                  <input name="azure_endpoint" type="text" placeholder="Endpoint" value={creds.azure_endpoint} onChange={handleCredChange} className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                </div>
              )}
              {provider === 'AWS Bedrock' && (
                <div className="space-y-3">
                  <input name="aws_access_key" type="password" placeholder="Access Key" value={creds.aws_access_key} onChange={handleCredChange} className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                  <input name="aws_secret_key" type="password" placeholder="Secret Key" value={creds.aws_secret_key} onChange={handleCredChange} className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                  <input name="aws_region" type="text" placeholder="Region" value={creds.aws_region} onChange={handleCredChange} className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                </div>
              )}
              {provider === 'Google Gemini' && (
                <div className="space-y-3">
                  <input name="google_key" type="password" placeholder="API Key" value={creds.google_key} onChange={handleCredChange} className="w-full text-xs p-3 bg-black border border-zinc-800 rounded-lg text-zinc-300 focus:ring-1 focus:ring-emerald-500 outline-none" />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="mt-auto p-6 border-t border-zinc-900">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse box-shadow-[0_0_10px_#10b981]"></div>
            <span className="text-[10px] font-bold text-emerald-500 tracking-wider">SYSTEM READY</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-10 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black">
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10">

          {/* Input Form */}
          <div className="space-y-6">
            <div className="bg-zinc-900/80 backdrop-blur-md p-8 rounded-2xl shadow-2xl border border-zinc-800">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-3 text-white">
                <div className="p-2 bg-emerald-500/10 rounded-lg"><Camera className="w-5 h-5 text-emerald-500" /></div>
                Evidence Submission
              </h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-bold text-emerald-500 uppercase tracking-widest mb-3">Visual Data Quality</label>
                  <div className="flex gap-4">
                    <label className={`flex-1 p-4 border rounded-xl cursor-pointer flex items-center justify-center gap-3 transition-all ${imageStatus === 'clear'
                        ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)]'
                        : 'bg-black border-zinc-800 text-zinc-500 hover:border-zinc-700'
                      }`}>
                      <input type="radio" name="status" value="clear" checked={imageStatus === 'clear'} onChange={() => setImageStatus('clear')} className="hidden" />
                      <CheckCircle className="w-5 h-5" /> High Res
                    </label>
                    <label className={`flex-1 p-4 border rounded-xl cursor-pointer flex items-center justify-center gap-3 transition-all ${imageStatus === 'blurry'
                        ? 'bg-amber-500/10 border-amber-500/50 text-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.1)]'
                        : 'bg-black border-zinc-800 text-zinc-500 hover:border-zinc-700'
                      }`}>
                      <input type="radio" name="status" value="blurry" checked={imageStatus === 'blurry'} onChange={() => setImageStatus('blurry')} className="hidden" />
                      <AlertTriangle className="w-5 h-5" /> Corruption Detected
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-emerald-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <Mic className="w-4 h-4" /> Audio Transcript
                  </label>
                  <textarea
                    className="w-full h-40 p-4 bg-black border border-zinc-800 rounded-xl text-sm text-slate-300 focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none leading-relaxed resize-none"
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                  />
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl flex items-center justify-center gap-3 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] transition-all transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                  {loading ? (
                    <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    <><Play className="w-5 h-5 fill-current group-hover:scale-110 transition-transform" /> INITIATE PROCESSING</>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Agent Output */}
          <div className="space-y-6">
            {!result && !loading && (
              <div className="h-full flex flex-col items-center justify-center opacity-30 border-2 border-dashed border-zinc-800 rounded-2xl p-12">
                <div className="w-20 h-20 bg-zinc-900 rounded-full flex items-center justify-center mb-6">
                  <Shield className="w-10 h-10 text-zinc-600" />
                </div>
                <p className="text-zinc-500 font-mono text-sm">Case File Empty. Awaiting Data input.</p>
              </div>
            )}

            {result && (
              <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">

                {/* Status Banner */}
                <div className={`p-6 rounded-2xl border mb-8 text-center shadow-lg relative overflow-hidden backdrop-blur-xl ${result.status === 'completed' ? 'bg-emerald-950/30 border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.1)]' :
                    result.status === 'denied' ? 'bg-rose-950/30 border-rose-500/30 shadow-[0_0_30px_rgba(244,63,94,0.1)]' :
                      'bg-amber-950/30 border-amber-500/30 shadow-[0_0_30px_rgba(245,158,11,0.1)]'
                  }`}>
                  <div className={`absolute top-0 left-0 w-full h-1 ${result.status === 'completed' ? 'bg-emerald-500' :
                      result.status === 'denied' ? 'bg-rose-500' : 'bg-amber-500'
                    }`}></div>

                  <h3 className={`text-2xl font-bold mb-2 flex items-center justify-center gap-3 ${result.status === 'completed' ? 'text-emerald-400' :
                      result.status === 'denied' ? 'text-rose-400' :
                        'text-amber-400'
                    }`}>
                    {result.status === 'completed' ? <CheckCircle className="w-8 h-8" /> :
                      result.status === 'denied' ? <XCircle className="w-8 h-8" /> :
                        <AlertTriangle className="w-8 h-8" />}
                    {result.status === 'completed' ? 'CLAIM SETTLED' :
                      result.status === 'denied' ? 'CLAIM DENIED' :
                        'ATTENTION REQUIRED'}
                  </h3>
                  <p className="text-sm text-zinc-400 mt-2 font-medium">{result.final_message}</p>
                </div>

                {/* Steps */}
                <div className="space-y-4">

                  {/* Intake */}
                  <div className="bg-zinc-900/50 p-5 rounded-xl border border-zinc-800">
                    <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-3 ml-1">Step 1: Intake Analysis</h4>
                    {result.intake_result?.is_valid ? (
                      <div className="flex items-center gap-3 text-emerald-400 text-sm font-bold p-3 bg-emerald-500/5 rounded-lg border border-emerald-500/10">
                        <CheckCircle className="w-5 h-5" />
                        Damage Validated: "{result.intake_result.damage_detected}"
                      </div>
                    ) : (
                      <div className="flex items-center gap-3 text-rose-400 text-sm font-bold p-3 bg-rose-500/5 rounded-lg border border-rose-500/10">
                        <AlertTriangle className="w-5 h-5" />
                        Input Error: {result.intake_result?.error_reason}
                      </div>
                    )}
                  </div>

                  {/* Verification */}
                  {result.coverage_verdict && (
                    <div className="bg-zinc-900/50 p-5 rounded-xl border border-zinc-800">
                      <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-3 ml-1">Step 2: Policy Verification</h4>
                      {result.coverage_verdict.is_covered ? (
                        <div className="space-y-2">
                          <div className="flex items-center gap-3 text-emerald-400 text-sm font-bold p-3 bg-emerald-500/5 rounded-lg border border-emerald-500/10">
                            <CheckCircle className="w-5 h-5" /> Coverage Confirmed
                          </div>
                          <p className="text-xs text-zinc-400 pl-2 border-l-2 border-zinc-800">{result.coverage_verdict.reason}</p>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <div className="flex items-center gap-3 text-rose-400 text-sm font-bold p-3 bg-rose-500/5 rounded-lg border border-rose-500/10">
                            <XCircle className="w-5 h-5" /> Coverage Denied
                          </div>
                          <p className="text-xs text-zinc-400 pl-2 border-l-2 border-rose-900">{result.coverage_verdict?.reason}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Estimation */}
                  {result.estimate_details && result.estimate_details.total && (
                    <div className="bg-gradient-to-br from-zinc-900 to-black p-6 rounded-xl border border-zinc-800 relative overflow-hidden group">
                      <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-colors"></div>
                      <h4 className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-4">Step 3: Final Estimation</h4>

                      <div className="flex justify-between items-end relative z-10">
                        <div>
                          <p className="text-xs text-zinc-500 mb-1">Total Payout</p>
                          <div className="text-4xl font-bold text-white tracking-tight">${result.estimate_details.total.toFixed(2)}</div>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">Breakdown</p>
                          <p className="text-xs text-emerald-400">{result.estimate_details.breakdown}</p>
                        </div>
                      </div>
                    </div>
                  )}

                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;
