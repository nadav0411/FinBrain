import React from 'react';
import './MainScreen.css';

function MainScreen() {
  return (
    <div className="main-container">
      <aside className="sidebar">
        <div className="logo">💰 FinBrain</div>
        <nav className="menu">
          <a href="#" className="menu-item active">📊 Dashboard</a>
          <a href="#" className="menu-item">💸 All Expenses</a>
          <a href="#" className="menu-item">⚙️ Settings</a>
          <a href="#" className="menu-item">🚪 Logout</a>
        </nav>
      </aside>

      <main className="content">
        <h1>Welcome to FinBrain 🎉</h1>
        <p>This is your main dashboard.</p>
        {/* פה נטען את הרכיבים הפנימיים לפי ניווט */}
      </main>
    </div>
  );
}

export default MainScreen;
