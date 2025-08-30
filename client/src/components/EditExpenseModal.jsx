import React from 'react';
import './EditExpenseModal.css'; // ניצור את זה עוד רגע

function EditExpenseModal() {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Add Expense Item</h2>
          <button className="close-button">&times;</button>
        </div>

        <div className="modal-body">
          <div className="row">
            <div className="field">
              <label>Title</label>
              <input type="text" placeholder="Pizza with friends" />
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Date</label>
              <input type="date" className="date-input" max={new Date().toISOString().split("T")[0]} onKeyDown={(e) => e.preventDefault()}/>
            </div>
          </div>

          <div className="row">
            <div className="field">
              <label>Amount</label>
              <input type="number" placeholder="60.00" min={0} onKeyDown={(e) => {
                if (!/[0-9.]/.test(e.key) && e.key !== "Backspace" && e.key !== "Tab" && e.key !== "ArrowLeft" && e.key !== "ArrowRight" && e.key !== "Delete" && e.key !== "." ) {
                  e.preventDefault(); } }} />
            </div>
            <div className="field">
              <label>Currency</label>
              <select>
                <option value="USD">USD</option>
                <option value="ILS">ILS</option>
              </select>
            </div>
          </div>

          <div style={{ textAlign: 'right', marginTop: '16px' }}>
          <button className="add-button">Add</button>
        </div>
      </div>

      </div>
    </div>
  );
}

export default EditExpenseModal;
