import React, { useState } from 'react';
import './MainScreen.css';
import AllExpenses from './AllExpenses';
import logo from '../assets/logo.png'; // ודא שזה הנתיב הנכון

function MainScreen() {
  const [view, setView] = useState('dashboard');

  // כותרת בראש המסך לפי המסך הנבחר
  const getPageTitle = () => {
    switch (view) {
      case 'expenses': return 'Expenses';
      case 'incomes': return 'Incomes';
      case 'coming': return 'Coming Soon';
      case 'settings': return 'Settings';
      default: return 'Dashboard';
    }
  };

  // תוכן המסך המרכזי לפי view
  const renderContent = () => {
    switch (view) {
      case 'expenses':
        return <AllExpenses />;
      case 'incomes':
        return <h1>💵 All Incomes Page</h1>;
      case 'coming':
        return <h1>🛠️ Coming Soon</h1>;
      case 'settings':
        return <h1>⚙️ Settings Page</h1>;
      default:
        return (
          <>
            <h1>📊 Dashboard</h1>
            <p>Welcome to FinBrain 🎉</p>
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
          <button className={`menu-item ${view === 'incomes' ? 'active' : ''}`} onClick={() => setView('incomes')}>
            💰 All Incomes
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
        </div>
        <div className="page-body">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default MainScreen;
