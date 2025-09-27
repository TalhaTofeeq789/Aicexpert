// store.ts

import { configureStore, combineReducers } from '@reduxjs/toolkit';
import themeReducer from '../theme/reducer'; // Import your slice reducers here

// Define RootState
export type RootState = ReturnType<typeof rootReducer>;

// Combine all reducers into rootReducer
const rootReducer = combineReducers({
  theme: themeReducer,
});

// Configure the Redux store
const store = configureStore({
  reducer: rootReducer,
});

export default store;
