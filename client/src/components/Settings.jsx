/* FinBrain Project - Settings.jsx - MIT License (c) 2025 Nadav Eshed */


// Import React library (needed for all React components)
import React from 'react';
// Import CSS styles for this component
import './Settings.css';

/**
 * Settings Component
 * 
 * A simple placeholder that shows a "Coming Soon" message
 * when users try to access the settings page.
 */
function Settings() {
  return (
    <div className="settings-wrapper">
      {/* Decorative background element (purely visual) */}
      <div className="settings-decor" aria-hidden="true" role="presentation" />
      
      {/* Main settings card container */}
      <div className="settings-card">
        {/* Badge to indicate the feature is not ready */}
        <span className="soon-pill">Coming Soon</span>
        
        {/* Icon container with gear symbol */}
        <div className="icon-container">
          <div className="settings-icon" aria-hidden="true" role="presentation">
            ⚙️
          </div>
        </div>
        
        {/* Main title */}
        <h3 className="settings-title">Settings</h3>
        
        {/* Subtitle text */}
        <p className="settings-subtitle">We're crafting a better experience</p>
        
        {/* Divider line (decorative) */}
        <div className="shine-divider" aria-hidden="true" role="presentation" />
        
        {/* Friendly thank-you note */}
        <div className="gentle-note">Thanks for your patience ✨</div>
      </div>
    </div>
  );
}

// Export so it can be used in other files
export default Settings;