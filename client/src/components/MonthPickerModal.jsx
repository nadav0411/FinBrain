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

  // Toggle month selection (no popup when exceeding 12; Apply will be disabled)
  const toggleMonth = (year, monthIndex) => {
    const key = `${year}-${monthIndex}`;
    const updated = new Set(selected);
    
    if (updated.has(key)) {
      updated.delete(key); // Remove if already selected
    } else {
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
              <span className="selection-count" style={{ color: selected.size > 12 ? '#b91c1c' : undefined }}>
                {selected.size}/12 months selected
              </span>
              {selected.size > 12 && (
                <div className="selected-preview" style={{ color: '#b91c1c' }}>
                  Reduce selection to 12 months or fewer to apply.
                </div>
              )}
              {/* Show selected months preview when any are selected */}
              {selected.size > 0 && (
                <div className="selected-preview">
                  📅 <strong>Selected:</strong> {formatSelectedText().join(' • ')}
                </div>
              )}
            </div>
            {/* Apply button is always visible but disabled when none or over limit */}
            <button
              className="apply-button"
              onClick={handleApply}
              disabled={selected.size === 0 || selected.size > 12}
              aria-disabled={selected.size === 0 || selected.size > 12}
              title={selected.size > 12 ? 'Select up to 12 months' : undefined}
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MonthPickerModal;
