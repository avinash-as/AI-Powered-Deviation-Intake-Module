import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { analyzeFile, analyzeText, applyAi } from '../features/deviation/deviationSlice.js'

export default function AiPanel() {
  const dispatch = useDispatch()
  const { aiResult, aiLoading, error } = useSelector((s) => s.deviation)
  const [text, setText] = useState('')

  const onAnalyze = () => dispatch(analyzeText(text))
  const onFile = (e) => {
    const f = e.target.files?.[0]
    if (f) dispatch(analyzeFile(f))
  }
  const loadSample = async () => {
    const sample = `Subject: Temperature excursion in drying stage — Batch API-2026-042\nDate: 2026-09-20\nReported by: R. Sharma (Production)\nProduct: Atorvastatin API, Batch API-2026-042, drying stage in Reactor R-204.\nApproved range: 60-65 C. Observed: 78 C for ~40 minutes.\nImmediate action: Batch put ON HOLD, QA notified, dryer log collected.\nLikely cause: steam valve malfunction.`
    setText(sample)
  }

  return (
    <div className="card">
      <h2>AI Assistant <span className="hint">— paste email / upload doc, then Apply to form</span></h2>
      <label>Paste deviation text / email<textarea rows={8} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste deviation email or document text here…" /></label>
      <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
        <button className="btn btn-secondary" disabled={aiLoading || text.length < 10} onClick={onAnalyze}>
          {aiLoading ? 'Analyzing…' : 'Analyze with AI'}
        </button>
        <label className="btn" style={{ background: '#e2e8f0' }}>Upload .txt/.pdf
          <input type="file" accept=".txt,.md,.eml,.log,.pdf" hidden onChange={onFile} />
        </label>
        <button className="btn" onClick={loadSample}>Load sample</button>
      </div>
      <div className="hint" style={{ marginTop: 6 }}>Per assignment: fill the left form via this AI panel (Analyze → Apply), don't type it manually.</div>
      {error && <div className="error">{String(error)}</div>}
      {aiResult && (
        <div className="ai-box">
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
            <span className={`badge badge-${aiResult.severity}`}>{aiResult.severity}</span>
            <span className="hint">provider: {aiResult.provider} · confidence {Math.round((aiResult.ai_confidence || 0) * 100)}%</span>
          </div>
          <div className="kv">
            <b>Impact</b><span>{aiResult.impact_assessment}</span>
            <b>Reason</b><span>{aiResult.ai_reason}</span>
            <b>Title</b><span>{aiResult.extracted?.title}</span>
            <b>Batch</b><span>{aiResult.extracted?.batch_no}</span>
            <b>Spec vs Observed</b><span>{aiResult.extracted?.specification_limit} → {aiResult.extracted?.observed_value}</span>
            <b>Type</b><span>{aiResult.extracted?.deviation_type}</span>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 10 }} onClick={() => dispatch(applyAi())}>
            Apply to Log Deviation form →
          </button>
        </div>
      )}
    </div>
  )
}
