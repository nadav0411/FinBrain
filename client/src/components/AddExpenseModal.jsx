import React, { useState } from 'react';
import './AddExpenseModal.css';


function AddExpenseModal({ onClose }) {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const today = new Date().toISOString().split("T")[0];        // תאריך נוכחי בפורמט YYYY-MM-DD
  const minDate = "2015-01-01";                                 // תאריך מינימלי

  const handleSubmit = async () => {
    if (!title || !date || !amount || !currency) {
      setError("Please fill in all fields.");
      return;
    }

    const expenseData = { title, date, amount, currency };
    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/add_expense`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': localStorage.getItem('session_id')
        },
        body: JSON.stringify(expenseData),
      });

      if (response.ok) {
        console.log("Expense added!");
        onClose();
      } else {
        const err = await response.text();
        console.error("Failed to add expense:", err);
        setError("Server error. Try again.");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Connection error.");
    } finally {
      setLoading(false);
    }
  };

  const handleTitleChange = (e) => {
    const regex = /^[A-Za-z0-9\s]*$/;
    if (regex.test(e.target.value)) {
      setTitle(e.target.value);
      setError('');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Expense Item</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}

          <div className="row">
            <div className="field">
              <label>Title</label>
              <input
                type="text"
                placeholder="Pizza with friends"
                value={title}
                onChange={handleTitleChange}
              />
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Date</label>
              <input
                type="date"
                className="date-input"
                value={date}
                min={minDate}
                max={today}
                onKeyDown={(e) => e.preventDefault()}
                onChange={(e) => {
                  setDate(e.target.value);
                  setError('');
                }}
              />
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Amount</label>
              <input
                type="number"
                placeholder="60.00"
                min={0}
                value={amount}
                onChange={(e) => {
                  setAmount(e.target.value);
                  setError('');
                }}
                onKeyDown={(e) => {
                  if (
                    !/[0-9.]/.test(e.key) &&
                    !["Backspace", "Tab", "ArrowLeft", "ArrowRight", "Delete"].includes(e.key)
                  ) {
                    e.preventDefault();
                  }
                }}
              />
            </div>

            <div className="field">
              <label>Currency</label>
              <select
                value={currency}
                onChange={(e) => {
                  setCurrency(e.target.value);
                  setError('');
                }}
              >
                <option value="USD">USD</option>
                <option value="ILS">ILS</option>
              </select>
            </div>
          </div>

          <div className="button-container">
            <button className="add-button" onClick={handleSubmit} disabled={loading}>
              {loading ? (
                <div className="loading-dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </div>
              ) : (
                "Add"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddExpenseModal;
