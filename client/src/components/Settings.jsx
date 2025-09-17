/* Settings.jsx */

import React from 'react';
import './Settings.css';

function Settings() {
  return (
    <div className="settings-wrapper">
      <div className="settings-decor" aria-hidden />
      <div className="settings-card">
        <span className="soon-pill">Coming Soon</span>
        <div className="icon-container">
          <div className="settings-icon" aria-hidden>⚙️</div>
        </div>
        <h3 className="settings-title">Settings</h3>
        <p className="settings-subtitle">We’re crafting a better experience</p>
        <div className="shine-divider" aria-hidden />
        <div className="gentle-note">Thanks for your patience ✨</div>
      </div>
    </div>
  );
}

export default Settings;


