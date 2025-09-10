import React, { useState } from 'react';
import './MainScreen.css';
import AllExpenses from './AllExpenses';
import logo from '../assets/logo.png'; 
import Dashboard from './DashBoard';

function MainScreen() {
  const [view, setView] = useState('dashboard');

  const getPageTitle = () => {
    switch (view) {
      case 'expenses': return 'Expenses';
      case 'coming': return 'Coming Soon';
      case 'settings': return 'Settings';
      default: return 'Dashboard';
    }
  };

  const renderContent = () => {
    switch (view) {
      case 'expenses':
        return <AllExpenses />;
      case 'coming':
        return <h1>🛠️ Coming Soon</h1>;
      case 'settings':
        return <h1>⚙️ Settings Page</h1>;
      default:
        return (
          <>
            <Dashboard />
          </>
        );
    }
  };

  return (
    <div className="main-container">
      <aside className="sidebar">
        <img src={logo} alt="Logo" className="sidebar-logo" />
        <nav className="menu">
          <button className={`menu-item ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
            📊 Dashboard
          </button>
          <button className={`menu-item ${view === 'expenses' ? 'active' : ''}`} onClick={() => setView('expenses')}>
            💸 All Expenses
          </button>
          <button className={`menu-item ${view === 'coming' ? 'active' : ''}`} onClick={() => setView('coming')}>
            🛠️ Coming Soon
          </button>
          <button className={`menu-item ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
            ⚙️ Settings
          </button>
          <button className="menu-item" onClick={() => window.location.reload()}>
            🚪 Logout
          </button>
        </nav>
      </aside>

      <main className="content">
        <div className="page-header">
          <h2>{getPageTitle()}</h2>
          <div className="user-welcome">
            Welcome, <span className="user-name">{localStorage.getItem('user_name') || 'User'}</span><span className="user-punctuation">! 👋</span>
          </div>
        </div>
        <div className="page-body">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default MainScreen;
