import React, { useState } from 'react'
import ChatWindow from './ChatWindow'
import Dashboard from './Dashboard'
import './index.css'

function App() {
  const [currentView, setCurrentView] = useState('chat');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Customer Support</h1>
        <p>Advanced Deep Learning NLP Integration</p>
        
        <div className="nav-toggle">
          <button 
            className={currentView === 'chat' ? 'active' : ''} 
            onClick={() => setCurrentView('chat')}
          >
            Live Chat
          </button>
          <button 
            className={currentView === 'dashboard' ? 'active' : ''} 
            onClick={() => setCurrentView('dashboard')}
          >
            Admin Dashboard
          </button>
        </div>
      </header>
      
      <main className="app-main">
        {currentView === 'chat' ? <ChatWindow /> : <Dashboard />}
      </main>
    </div>
  )
}

export default App
