import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Global error handler to catch unhandled errors
window.addEventListener('error', (event) => {
  fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { 
    method: 'POST', 
    headers: { 'Content-Type': 'application/json' }, 
    body: JSON.stringify({ 
      location: 'main.tsx:error', 
      message: 'Global error caught', 
      data: { 
        errorMessage: event.message, 
        errorStack: event.error?.stack,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }, 
      timestamp: Date.now(), 
      runId: 'post-fix', 
      hypothesisId: 'I' 
    }) 
  }).catch(() => {});
  console.error('Global error:', event);
});

window.addEventListener('unhandledrejection', (event) => {
  fetch('http://127.0.0.1:7245/ingest/ca570fb1-81be-4a7a-b963-2da680c5e0a2', { 
    method: 'POST', 
    headers: { 'Content-Type': 'application/json' }, 
    body: JSON.stringify({ 
      location: 'main.tsx:unhandledrejection', 
      message: 'Unhandled promise rejection', 
      data: { 
        reason: String(event.reason),
        errorStack: event.reason?.stack
      }, 
      timestamp: Date.now(), 
      runId: 'post-fix', 
      hypothesisId: 'I' 
    }) 
  }).catch(() => {});
  console.error('Unhandled rejection:', event.reason);
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
