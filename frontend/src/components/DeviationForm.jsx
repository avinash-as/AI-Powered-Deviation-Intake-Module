import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { saveDeviation, updateField, resetForm, fetchDeviations } from '../features/deviation/deviationSlice.js'

const fields = [
  ['title', 'Deviation title *'],
  ['product', 'Product'],
  ['batch_no', 'Batch No.'],
  ['stage', 'Process stage'],
  ['equipment', 'Equipment'],
  ['date_observed', 'Date observed'],
  ['observed_by', 'Observed / Reported by'],
  ['department', 'Department'],
  ['specification_limit', 'Approved specification / range'],
  ['observed_value', 'Observed value'],
]

export default function DeviationForm() {
  const dispatch = useDispatch()
  const { form, saveState, savedItem, error } = useSelector((s) => s.deviation)

  const set = (e) => dispatch(updateField({ name: e.target.name, value: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))

  const onSave = async () => {
    const res = await dispatch(saveDeviation(form))
    if (res.meta.requestStatus === 'fulfilled') dispatch(fetchDeviations())
  }

  return (
    <div className="card">
      <h2>Log Deviation <span className="hint">— review AI output, edit if needed, then Save</span></h2>
      <div className="grid2">
        {fields.map(([name, label]) => (
          <label key={name}>{label}
            <input name={name} value={form[name] || ''} onChange={set} placeholder={label} type={name === 'date_observed' ? 'date' : 'text'} />
          </label>
        ))}
        <label>Deviation type
          <select name="deviation_type" value={form.deviation_type} onChange={set}>
            {['Process', 'Equipment', 'Material', 'Documentation', 'Environmental', 'Other'].map((o) => <option key={o}>{o}</option>)}
          </select>
        </label>
        <label>Severity (AI-assisted)
          <select name="severity" value={form.severity} onChange={set}>
            {['Minor', 'Major', 'Critical'].map((o) => <option key={o}>{o}</option>)}
          </select>
        </label>
      </div>
      <div style={{ display: 'grid', gap: 10, marginTop: 10 }}>
        <label>Description / event details<textarea name="description" rows={4} value={form.description} onChange={set} /></label>
        <label>Impact assessment (AI-assisted)<textarea name="impact_assessment" rows={3} value={form.impact_assessment} onChange={set} /></label>
        <div className="grid2">
          <label>Probable cause<textarea name="probable_cause" rows={2} value={form.probable_cause} onChange={set} /></label>
          <label>Immediate action / containment<textarea name="immediate_action" rows={2} value={form.immediate_action} onChange={set} /></label>
        </div>
        <label style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" name="capa_required" checked={!!form.capa_required} onChange={set} /> CAPA required
        </label>
        {form.ai_reason && <div className="hint">AI reason: {form.ai_reason} (confidence {Math.round((form.ai_confidence || 0) * 100)}%)</div>}
      </div>
      <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
        <button className="btn btn-primary" disabled={saveState === 'saving'} onClick={onSave}>
          {saveState === 'saving' ? 'Saving…' : 'Review & Save deviation'}
        </button>
        <button className="btn" onClick={() => dispatch(resetForm())}>Clear</button>
      </div>
      {saveState === 'saved' && savedItem && <div className="saved">Saved as <b>{savedItem.deviation_id}</b>. You can show this ID in your demo video as proof of end-to-end save.</div>}
      {saveState === 'error' && <div className="error">{error}</div>}
    </div>
  )
}
