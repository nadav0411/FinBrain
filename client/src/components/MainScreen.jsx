/* FinBrain Project - MainScreen.jsx - MIT License (c) 2025 Nadav Eshed */


import React, { useState } from 'react';
import './MainScreen.css';
import AllExpenses from './AllExpenses';
import logo from '../assets/logo.png'; 
import Dashboard from './DashBoard';
import Settings from './Settings';

/**
 * MainScreen Component - The main layout component that handles navigation between different views
 * This is a container component that manages the overall app structure with sidebar navigation
 */
function MainScreen() {
  // State to track which view/page is currently active
  // 'dashboard' is the default view when the component first loads
  const [view, setView] = useState('dashboard');

  /**
   * Helper function to get the page title based on current view
   * This keeps the header title in sync with the selected navigation item
   */
  const getPageTitle = () => {
    switch (view) {
      case 'expenses': return 'Expenses';
      case 'comingsoon': return 'Coming Soon';
      case 'settings': return 'Settings';
      default: return 'Dashboard';
    }
  };

  /**
   * Conditional rendering function that returns the appropriate component based on current view
   * This is a common React pattern for handling multiple views in a single component
   */
  const renderContent = () => {
    switch (view) {
      case 'expenses':
        return <AllExpenses />;
      case 'comingsoon':
        return (
          <div style={{
            background: '#ffffff',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.06)'
          }}>
            <h3 style={{ marginTop: 0 }}>🚧 Stay Tuned!</h3>
            <p style={{ margin: 0, color: '#475569' }}>
              Always working on something new. See my latest journey on LinkedIn — and feel free to reach out anytime via email or LinkedIn:
              <br />
              <a href="mailto:nadav0411@gmail.com">nadav0411@gmail.com</a>
              {' '}|{' '}
              <a href="https://www.linkedin.com/in/nadav-eshed-b32792363" target="_blank" rel="noopener noreferrer">
                www.linkedin.com/in/nadav-eshed-b32792363
              </a>
            </p>
          </div>
        );
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="main-container">
      {/* Sidebar navigation - contains logo and menu items */}
      <aside className="sidebar">
        <img src={logo} alt="Logo" className="sidebar-logo" />
        <nav className="menu">
          {/* Dynamic className with conditional 'active' class for visual feedback */}
          <button className={`menu-item ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
            📊 Dashboard
          </button>
          <button className={`menu-item ${view === 'expenses' ? 'active' : ''}`} onClick={() => setView('expenses')}>
            💸 All Expenses
          </button>
          <button className={`menu-item ${view === 'comingsoon' ? 'active' : ''}`} onClick={() => setView('comingsoon')}>
            🛠️ Coming Soon
          </button>
          <button className={`menu-item ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
            ⚙️ Settings
          </button>
          {/* Logout button */}
          <button
            className="menu-item"
            onClick={async () => {
              try {
                const sessionId = localStorage.getItem('session_id');
                if (sessionId) {
                  await fetch(`${import.meta.env.VITE_API_URL}/logout`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Session-ID': sessionId
                    }
                  });
                }
              } catch (e) {
                // Ignore logout API errors - proceed with local logout regardless
              } finally {
                localStorage.removeItem('session_id');
                localStorage.removeItem('user_name');
                localStorage.removeItem('is_demo_user');
                // Dispatch logout event to stop timers BEFORE reload
                window.dispatchEvent(new CustomEvent('userLoggedOut'));
                window.location.reload();
              }
            }}
          >
            🚪 Logout
          </button>
        </nav>
      </aside>

      {/* Main content area */}
      <main className="content">
        {localStorage.getItem('is_demo_user') === 'true' && (
          <div className="demo-banner" role="status" aria-live="polite">
            You are in Demo Mode — adding, changing, and deleting are disabled. To upgrade to the full version, please sign up and login.
          </div>
        )}
        <div className="page-header">
          <h2>{getPageTitle()}</h2>
          {/* Personalized welcome message using localStorage */}
          <div className="user-welcome">
            Welcome, <span className="user-name">{localStorage.getItem('user_name') || 'User'}</span><span className="user-punctuation">! 👋</span>
          </div>
        </div>
        {/* Dynamic content area that renders different components based on current view */}
        <div className="page-body">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default MainScreen;
