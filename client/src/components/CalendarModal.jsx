/* FinBrain Project - CalendarModal.jsx - MIT License (c) 2025 Nadav Eshed */


import React, { useState } from 'react';
import './CalendarModal.css';

/**
 * CalendarModal - A popup window to select month and year
 *
 * Props:
 * - onClose: Closes the modal
 * - onPickDate: Called with selected month (1-12) and year
 */
function CalendarModal({ onClose, onPickDate }) {
  // Month names to show on buttons
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  // Create array of years: [2015, ..., 2027]
  const years = Array.from({ length: 13 }, (_, index) => 2015 + index);

  // React state hooks to store user selection
  const [selectedMonth, setSelectedMonth] = useState(null); // string like "Jan"
  const [selectedYear, setSelectedYear] = useState(null);   // number like 2024

  /**
   * When user clicks "Select" button
   * → send selected month & year to parent
   * → close the modal
   */
  const handleSelect = () => {
    if (selectedMonth && selectedYear) {
      const monthNumber = months.indexOf(selectedMonth) + 1; // "Jan" → 1
      onPickDate(monthNumber, selectedYear);
      onClose();
    }
  };

  return (
    // Covers full screen with semi-dark background
    <div className="modal-overlay" onClick={onClose}>
      
      {/* The modal itself (centered box) */}
      <div
        className="modal calendar-modal"
        onClick={(e) => e.stopPropagation()} // Prevents closing when clicking inside modal
      >

        {/* Top bar: title + close button */}
        <div className="modal-header">
          <h2>Select Month & Year</h2>
          <button className="close-button" onClick={onClose}>
            &times;
          </button>
        </div>

        {/* Main content area */}
        <div className="calendar-content">

          {/* MONTH BUTTONS */}
          <div className="months-grid">
            {months.map((month) => (
              <button
                key={month}
                className={`month-btn ${selectedMonth === month ? 'selected' : ''}`}
                onClick={() => setSelectedMonth(month)}
              >
                {month}
              </button>
            ))}
          </div>

          {/* YEAR BUTTONS */}
          <div className="years-grid">
            {years.map((year) => (
              <button
                key={year}
                className={`year-btn ${selectedYear === year ? 'selected' : ''}`}
                onClick={() => setSelectedYear(year)}
              >
                {year}
              </button>
            ))}
          </div>

          {/* FOOTER SECTION: selected info + action button */}
          <div className="calendar-footer">

            {/* Show selected values */}
            {selectedMonth && selectedYear && (
              <div className="selected-info">
                📅 Selected: <strong>{selectedMonth} {selectedYear}</strong>
              </div>
            )}

            {/* "Select" button – only works when both selected */}
            <button
              className="add-button"
              onClick={handleSelect}
              disabled={!selectedMonth || !selectedYear} // Grayed out if missing
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
