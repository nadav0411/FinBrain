import React, { useState } from 'react';
import './MonthPickerModal.css';

const months = [
  "Jan", "Feb", "Mar", "Apr",
  "May", "Jun", "Jul", "Aug",
  "Sep", "Oct", "Nov", "Dec"
];

const MIN_YEAR = 2015;
const MAX_YEAR = 2027;

function MonthPickerModal({ onClose, onApply }) {
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [selected, setSelected] = useState(new Set());

  const toggleMonth = (year, monthIndex) => {
    const key = `${year}-${monthIndex}`;
    const updated = new Set(selected);
    
    if (updated.has(key)) {
      // If already selected, remove it
      updated.delete(key);
    } else {
      // If not selected, check if we can add it (max 15)
      if (updated.size >= 15) {
        alert('Maximum 15 months can be selected');
        return;
      }
      updated.add(key);
    }
    
    setSelected(updated);
  };

  const isSelected = (year, monthIndex) =>
    selected.has(`${year}-${monthIndex}`);

  const formatSelectedText = () => {
    const sorted = Array.from(selected).sort((a, b) => {
      const [aY, aM] = a.split('-').map(Number);
      const [bY, bM] = b.split('-').map(Number);
      return aY === bY ? aM - bM : aY - bY;
    });

    return sorted.map((key) => {
      const [year, monthIndex] = key.split('-').map(Number);
      return `${months[monthIndex]} ${year}`;
    });
  };

  const getStructuredSelection = () => {
    return Array.from(selected).map((key) => {
      const [year, monthIndex] = key.split('-').map(Number);
      return { year, monthIndex };
    });
  };

  const handleApply = () => {
    const result = getStructuredSelection();
    if (onApply) onApply(result);
    onClose();
  };

  const changeYear = (dir) => {
    setCurrentYear((prev) => {
      const next = dir === 'prev' ? prev - 1 : prev + 1;
      return Math.max(MIN_YEAR, Math.min(MAX_YEAR, next));
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal calendar-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Months</h2>
          <button className="close-button" onClick={onClose}>✖</button>
        </div>

        <div className="calendar-content">
          <div className="year-nav">
            <button onClick={() => changeYear('prev')} disabled={currentYear === MIN_YEAR}>◀</button>
            <span>{currentYear}</span>
            <button onClick={() => changeYear('next')} disabled={currentYear === MAX_YEAR}>▶</button>
          </div>

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

          <div className="calendar-footer">
            <div className="selection-info">
              <span className="selection-count">
                {selected.size}/15 months selected
              </span>
              {selected.size > 0 && (
                <div className="selected-preview">
                  📅 <strong>Selected:</strong> {formatSelectedText().join(' • ')}
                </div>
              )}
            </div>
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
