// CalendarModal.jsx

import React, { useState } from 'react';
import './CalendarModal.css';

// CalendarModal component - A popup that lets users pick a month and year
function CalendarModal({ onClose, onPickDate }) {
  // Array of month names for display (shortened format)
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  
  // Generate years from 2015 to 2027 (13 years total) using Array.from
  const years = Array.from({ length: 13 }, (_, i) => 2015 + i);

  // State to track which month and year the user has selected
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [selectedYear, setSelectedYear] = useState(null);

  // Function that runs when user clicks "Select" button
  const handleSelect = () => {
    // Only proceed if both month and year are selected
    if (selectedMonth && selectedYear) {
      // Convert month name to number (Jan=1, Feb=2, etc.) and pass to parent component
      onPickDate(months.indexOf(selectedMonth) + 1, selectedYear);
      // Close the modal after selection
      onClose();
    }
  };

  return (
    // Dark overlay that covers the entire screen - clicking it closes the modal
    <div className="modal-overlay" onClick={onClose}>
      {/* Modal content container - stopPropagation prevents closing when clicking inside */}
      <div className="modal calendar-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header with title and close button */}
        <div className="modal-header">
          <h2>Select Month & Year</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="calendar-content">
          {/* Grid of month buttons - each month gets its own clickable button */}
          <div className="months-grid">
            {months.map((m) => (
              <button
                key={m}
                // Add 'selected' class if this month is currently selected
                className={`month-btn ${selectedMonth === m ? 'selected' : ''}`}
                onClick={() => setSelectedMonth(m)}
              >
                {m}
              </button>
            ))}
          </div>

          {/* Grid of year buttons - each year gets its own clickable button */}
          <div className="years-grid">
            {years.map((y) => (
              <button
                key={y}
                // Add 'selected' class if this year is currently selected
                className={`year-btn ${selectedYear === y ? 'selected' : ''}`}
                onClick={() => setSelectedYear(y)}
              >
                {y}
              </button>
            ))}
          </div>

          {/* Footer with selection preview and submit button */}
          <div className="calendar-footer">
            {/* Show selected month/year only if both are selected */}
            {selectedMonth && selectedYear && (
              <div className="selected-info">
                📅 Selected: <strong>{selectedMonth} {selectedYear}</strong>
              </div>
            )}
            {/* Submit button - disabled until both month and year are selected */}
            <button
              className="add-button"
              onClick={handleSelect}
              disabled={!selectedMonth || !selectedYear}
            >
              Select
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CalendarModal;
