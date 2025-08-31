// I'm learning React and JavaScript, so I add simple comments to help me understand :)

// Import React to use JSX syntax
import React from 'react';

// Import the CSS file that styles this component
import './EditExpenseModal.css'; 

// This function is my React component
function EditExpenseModal() {
  return (
    // This is the dark background behind the white modal box
    <div className="modal-overlay">
      
      {/* This is the white popup box in the center */}
      <div className="modal">

        {/* This is the top part of the modal (title and close button) */}
        <div className="modal-header">
          <h2>Add Expense Item</h2>
          {/* This button closes the modal (just shows an X for now) */}
          <button className="close-button">&times;</button>
        </div>

        {/* This is the main body of the modal - the form area */}
        <div className="modal-body">

          {/* First row – Title input */}
          <div className="row">
            <div className="field">
              <label>Title</label>
              {/* Input for the name of the expense (like 'Pizza') */}
              <input type="text" placeholder="Pizza with friends" />
            </div>
          </div>

          {/* Second row – Date input */}
          <div className="row">
            <div className="field">
              <label>Date</label>
              {/* Input for date (user can't type, only select) */}
              <input
                type="date"
                className="date-input"
                max={new Date().toISOString().split("T")[0]} // today's date
                onKeyDown={(e) => e.preventDefault()} // block typing
              />
            </div>
          </div>

          {/* Third row – Amount and Currency */}
          <div className="row">

            {/* Input for amount – allows only numbers */}
            <div className="field">
              <label>Amount</label>
              <input
                type="number"
                placeholder="60.00"
                min={0}
                onKeyDown={(e) => {
                  // Only allow numbers and a few special keys
                  if (
                    !/[0-9.]/.test(e.key) &&
                    e.key !== "Backspace" &&
                    e.key !== "Tab" &&
                    e.key !== "ArrowLeft" &&
                    e.key !== "ArrowRight" &&
                    e.key !== "Delete" &&
                    e.key !== "."
                  ) {
                    e.preventDefault(); // block other keys
                  }
                }}
              />
            </div>

            {/* Dropdown to choose currency */}
            <div className="field">
              <label>Currency</label>
              <select>
                <option value="USD">USD</option>
                <option value="ILS">ILS</option>
              </select>
            </div>

          </div>

          {/* Add button – now using a CSS class instead of inline style */}
          <div className="button-container">
            <button className="add-button">Add</button>
          </div>

        </div> {/* end of modal-body */}

      </div> {/* end of modal */}

    </div> // end of modal-overlay
  );
}

// Export this component so I can use it in other parts of the app
export default EditExpenseModal;
