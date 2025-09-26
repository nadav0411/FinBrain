import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Find the HTML element with id="root" and render our React app inside it
// This connects our React app to the HTML page
createRoot(document.getElementById('root')).render(
  <App />
)
