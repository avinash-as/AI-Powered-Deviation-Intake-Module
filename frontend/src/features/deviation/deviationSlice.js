import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import axios from 'axios'

const emptyForm = {
  title: '', description: '', date_observed: '', observed_by: '', department: 'Production',
  product: '', batch_no: '', stage: '', equipment: '', specification_limit: '',
  observed_value: '', deviation_type: 'Process', severity: 'Minor',
  impact_assessment: '', probable_cause: '', immediate_action: '',
  capa_required: false, status: 'Logged', ai_reason: '', ai_confidence: 0
}

export const analyzeText = createAsyncThunk('deviation/analyzeText', async (text) => {
  const { data } = await axios.post('/api/ai/analyze', { text })
  return data
})

export const analyzeFile = createAsyncThunk('deviation/analyzeFile', async (file) => {
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await axios.post('/api/ai/analyze-file', fd)
  return data
})

export const saveDeviation = createAsyncThunk('deviation/save', async (form) => {
  const { data } = await axios.post('/api/deviations', form)
  return data
})

export const fetchDeviations = createAsyncThunk('deviation/fetch', async () => {
  const { data } = await axios.get('/api/deviations')
  return data
})

const slice = createSlice({
  name: 'deviation',
  initialState: {
    form: { ...emptyForm },
    aiResult: null,
    aiLoading: false,
    saveState: 'idle', // idle|saving|saved|error
    savedItem: null,
    list: [],
    error: null
  },
  reducers: {
    updateField(state, action) {
      const { name, value } = action.payload
      state.form[name] = value
      state.saveState = 'idle'
    },
    applyAi(state) {
      if (!state.aiResult) return
      const ex = state.aiResult.extracted || {}
      state.form = {
        ...state.form,
        ...ex,
        severity: state.aiResult.severity || ex.severity || 'Minor',
        impact_assessment: state.aiResult.impact_assessment || ex.impact_assessment || '',
        ai_reason: state.aiResult.ai_reason || '',
        ai_confidence: state.aiResult.ai_confidence || 0
      }
    },
    resetForm(state) {
      state.form = { ...emptyForm }
      state.saveState = 'idle'
      state.savedItem = null
    }
  },
  extraReducers: (b) => {
    b.addCase(analyzeText.pending, (s) => { s.aiLoading = true; s.error = null })
      .addCase(analyzeText.fulfilled, (s, a) => { s.aiLoading = false; s.aiResult = a.payload })
      .addCase(analyzeText.rejected, (s, a) => { s.aiLoading = false; s.error = a.error.message })
      .addCase(analyzeFile.pending, (s) => { s.aiLoading = true; s.error = null })
      .addCase(analyzeFile.fulfilled, (s, a) => { s.aiLoading = false; s.aiResult = a.payload })
      .addCase(analyzeFile.rejected, (s, a) => { s.aiLoading = false; s.error = 'File analysis failed: ' + a.error.message })
      .addCase(saveDeviation.pending, (s) => { s.saveState = 'saving'; s.error = null })
      .addCase(saveDeviation.fulfilled, (s, a) => { s.saveState = 'saved'; s.savedItem = a.payload })
      .addCase(saveDeviation.rejected, (s, a) => { s.saveState = 'error'; s.error = 'Save failed: ' + a.error.message })
      .addCase(fetchDeviations.fulfilled, (s, a) => { s.list = a.payload })
  }
})

export const { updateField, applyAi, resetForm } = slice.actions
export default slice.reducer
