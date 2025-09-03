import React, { useState } from 'react';
import './AllExpenses.css';
import AddExpenseModal from './AddExpenseModal';


function AllExpenses() {
  const [showPopup, setShowPopup] = useState(false);

  return (
    <div className="expenses-container">
      <div className="expenses-header">
        <button className="new-expense-button" onClick={() => setShowPopup(true)}>✨ New Expense</button>
        <div className="controls">
          <span className="filter-btn">🔍 Filters</span>
          <span className="sort-btn">↕ Sort</span>
        </div>
      </div>

      <table className="expenses-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Amount</th>
            <th>Project</th>
            <th>Category</th>
            <th>Date</th>
            <th>Status</th>
            <th></th> {/* לשלוש הנקודות */}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Stock Images</td>
            <td>$25.00</td>
            <td>📱 App Development</td>
            <td>Other Expenses</td>
            <td>11/18/22</td>
            <td>Reimbursed</td>
            <td>⋯</td>
          </tr>
          <tr>
            <td>Software subscription</td>
            <td>$50.00</td>
            <td>📱 App Development</td>
            <td>Software</td>
            <td>11/06/22</td>
            <td>Unbilled</td>
            <td>⋯</td>
          </tr>
        </tbody>
      </table>

      {showPopup && <AddExpenseModal onClose={() => setShowPopup(false)} />}
    </div>
  );
}

export default AllExpenses;
