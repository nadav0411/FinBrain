/* MonthPickerModal.jsx */

import React, { useState } from 'react';
import './MonthPickerModal.css';

// Month abbreviations for display
const months = [
  "Jan", "Feb", "Mar", "Apr",
  "May", "Jun", "Jul", "Aug",
  "Sep", "Oct", "Nov", "Dec"
];

// Year range constraints for the picker
const MIN_YEAR = 2015;
const MAX_YEAR = 2027;

function MonthPickerModal({ onClose, onApply }) {
  // State for current year being viewed and selected months
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [selected, setSelected] = useState(new Set());

  // Toggle month selection with 15 month limit
  const toggleMonth = (year, monthIndex) => {
    const key = `${year}-${monthIndex}`;
    const updated = new Set(selected);
    
    if (updated.has(key)) {
      updated.delete(key); // Remove if already selected
    } else {
      if (updated.size >= 15) {
        alert('Maximum 15 months can be selected');
        return;
      }
      updated.add(key); // Add if not selected and under limit
    }
    
    setSelected(updated);
  };

  // Check if a specific month is selected
  const isSelected = (year, monthIndex) =>
    selected.has(`${year}-${monthIndex}`);

  // Format selected months for display preview
  const formatSelectedText = () => {
    const sorted = Array.from(selected).sort((a, b) => {
      const [aY, aM] = a.split('-').map(Number);
      const [bY, bM] = b.split('-').map(Number);
      return aY === bY ? aM - bM : aY - bY; // Sort by year, then month
    });

    return sorted.map((key) => {
      const [year, monthIndex] = key.split('-').map(Number);
      return `${months[monthIndex]} ${year}`;
    });
  };

  // Convert selection to structured data for parent component
  const getStructuredSelection = () => {
    return Array.from(selected).map((key) => {
      const [year, monthIndex] = key.split('-').map(Number);
      return { year, monthIndex };
    });
  };

  // Handle apply button - pass data to parent and close modal
  const handleApply = () => {
    const result = getStructuredSelection();
    if (onApply) onApply(result);
    onClose();
  };

  // Navigate between years with boundary checks
  const changeYear = (dir) => {
    setCurrentYear((prev) => {
      const next = dir === 'prev' ? prev - 1 : prev + 1;
      return Math.max(MIN_YEAR, Math.min(MAX_YEAR, next));
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal calendar-modal" onClick={(e) => e.stopPropagation()}>
        {/* Modal header with title and close button */}
        <div className="modal-header">
          <h2>Select Months</h2>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>

        <div className="calendar-content">
          {/* Year navigation controls */}
          <div className="year-nav">
            <button onClick={() => changeYear('prev')} disabled={currentYear === MIN_YEAR}>◀</button>
            <span>{currentYear}</span>
            <button onClick={() => changeYear('next')} disabled={currentYear === MAX_YEAR}>▶</button>
          </div>

          {/* Grid of month buttons for current year */}
          <div className="months-grid">
            {months.map((m, idx) => (
              <button
                key={idx}
                className={`month-btn ${isSelected(currentYear, idx) ? 'selected' : ''}`}
                onClick={() => toggleMonth(currentYear, idx)}
              >
                {m}
              </button>
            ))}
          </div>

          {/* Footer with selection info and apply button */}
          <div className="calendar-footer">
            <div className="selection-info">
              <span className="selection-count">
                {selected.size}/15 months selected
              </span>
              {/* Show selected months preview when any are selected */}
              {selected.size > 0 && (
                <div className="selected-preview">
                  📅 <strong>Selected:</strong> {formatSelectedText().join(' • ')}
                </div>
              )}
            </div>
            {/* Apply button only shows when months are selected */}
            {selected.size > 0 && (
              <button className="apply-button" onClick={handleApply}>
                Apply
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MonthPickerModal;
