import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import DeviationForm from './components/DeviationForm.jsx'
import AiPanel from './components/AiPanel.jsx'
import { fetchDeviations } from './features/deviation/deviationSlice.js'

export default function App() {
  const dispatch = useDispatch()
  const list = useSelector((s) => s.deviation.list)

  useEffect(() => { dispatch(fetchDeviations()) }, [dispatch])

  return (
    <>
      <div className="header">
        <div>
          <h1 style={{ margin: 0 }}>Deviation Intake Module</h1>
          <div className="hint">API pharma · document/text → AI extraction → Log Deviation form → impact & severity → review → save</div>
        </div>
        <span className="badge badge-Major">AIVOA · AI Product Engineer</span>
      </div>
      <div className="layout">
        <DeviationForm />
        <AiPanel />
      </div>
      <div style={{ maxWidth: 1350, margin: '0 auto', padding: '0 16px 24px' }}>
        <div className="card">
          <h2>Logged deviations ({list.length})</h2>
          {list.length === 0 ? <div className="hint">No deviations saved yet — run Analyze → Apply → Save to create the first one.</div> : (
            <table className="list">
              <thead><tr><th>ID</th><th>Title</th><th>Batch</th><th>Type</th><th>Severity</th><th>Status</th></tr></thead>
              <tbody>
                {list.map((d) => (
                  <tr key={d.id}><td>{d.deviation_id}</td><td>{d.title}</td><td>{d.batch_no}</td><td>{d.deviation_type}</td>
                    <td><span className={`badge badge-${d.severity}`}>{d.severity}</span></td><td>{d.status}</td></tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  )
}
