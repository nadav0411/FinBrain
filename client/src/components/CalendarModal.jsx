import React, { useState } from 'react';
import './CalendarModal.css';

function CalendarModal({ onClose, onPickDate }) {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const years = Array.from({ length: 13 }, (_, i) => 2015 + i); 

  const [selectedMonth, setSelectedMonth] = useState(null); 
  const [selectedYear, setSelectedYear] = useState(null);   

  // Function to convert month name to number (1–12)
  const getMonthIndex = (monthName) => months.indexOf(monthName) + 1;

  const handleSelect = () => {
    if (selectedMonth && selectedYear) {
      const monthNumber = getMonthIndex(selectedMonth); // Convert to number
      onPickDate(monthNumber, selectedYear); // Send to parent
      onClose(); 
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal calendar-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Month & Year</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="calendar-content">
          <div className="months-grid">
            {months.map((m) => (
              <button
                key={m}
                className={`month-btn ${selectedMonth === m ? 'selected' : ''}`}
                onClick={() => setSelectedMonth(m)}
              >
                {m}
              </button>
            ))}
          </div>

          <div className="years-grid">
            {years.map((y) => (
              <button
                key={y}
                className={`year-btn ${selectedYear === y ? 'selected' : ''}`}
                onClick={() => setSelectedYear(y)}
              >
                {y}
              </button>
            ))}
          </div>

          <div className="calendar-footer">
            {selectedMonth && selectedYear && (
              <div className="selected-info">
                📅 Selected: <strong>{selectedMonth} {selectedYear}</strong>
              </div>
            )}
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
