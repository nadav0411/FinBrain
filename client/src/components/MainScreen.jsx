/* MainScreen.jsx */

import React, { useState } from 'react';
import './MainScreen.css';
import AllExpenses from './AllExpenses';
import logo from '../assets/logo.png'; 
import Dashboard from './DashBoard';

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
      case 'settings':
        return <h1>⚙️ Settings Page</h1>;
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
          <button className={`menu-item ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
            ⚙️ Settings
          </button>
          {/* Logout button that refreshes the page to clear any stored data */}
          <button className="menu-item" onClick={() => window.location.reload()}>
            🚪 Logout
          </button>
        </nav>
      </aside>

      {/* Main content area */}
      <main className="content">
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
