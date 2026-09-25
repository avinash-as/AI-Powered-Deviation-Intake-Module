import { configureStore } from '@reduxjs/toolkit'
import deviationReducer from '../features/deviation/deviationSlice.js'

export const store = configureStore({
  reducer: { deviation: deviationReducer }
})
