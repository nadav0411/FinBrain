import React, { useState, useEffect } from 'react';
import './AllExpenses.css';
import AddExpenseModal from './AddExpenseModal';
import CalendarModal from './CalendarModal';

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function AllExpenses() {
  const today = new Date();

  // State management for UI controls and data
  const [showPopup, setShowPopup] = useState(false);           // Controls AddExpenseModal visibility
  const [calendarOpen, setCalendarOpen] = useState(false);     // Controls CalendarModal visibility
  const [month, setMonth] = useState(today.getMonth() + 1);    // Current selected month (1-12)
  const [year, setYear] = useState(today.getFullYear());       // Current selected year
  const [expenses, setExpenses] = useState([]);                // Array of expenses for current month/year
  const [refreshKey, setRefreshKey] = useState(0);             // Used to trigger data refresh
  const [activeMenu, setActiveMenu] = useState(null);          // Tracks which expense menu is open

  // Year range constraints for navigation
  const MIN_YEAR = 2015;
  const MAX_YEAR = 2027;

  // Fetches expenses from the server for the current month/year
  const fetchExpenses = async () => {
    try {
      const sessionId = localStorage.getItem('session_id');
      const res = await fetch(`${import.meta.env.VITE_API_URL}/get_expenses?month=${month}&year=${year}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });

      if (!res.ok) {
        throw new Error('Failed to fetch expenses');
      }

      const data = await res.json();
      setExpenses(data.expenses || []);
    } catch (err) {
      console.error('Error fetching expenses:', err);
    }
  };

  // Automatically fetch expenses when month, year, or refreshKey changes
  useEffect(() => {
    fetchExpenses();
  }, [month, year, refreshKey]);

  // Close dropdown menu when clicking outside of it
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (activeMenu && !event.target.closest('.menu-container')) {
        setActiveMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeMenu]);

  // Navigation functions for month/year selection
  const handlePrevMonth = () => {
    if (month === 1) {
      if (year > MIN_YEAR) {
        setMonth(12);
        setYear(year - 1);
      }
    } else {
      setMonth(month - 1);
    }
  };

  const handleNextMonth = () => {
    if (month === 12) {
      if (year < MAX_YEAR) {
        setMonth(1);
        setYear(year + 1);
      }
    } else {
      setMonth(month + 1);
    }
  };

  // Returns formatted month and year string for display
  const getMonthName = () => {
    return `${monthNames[month - 1]} ${year}`;
  };

  // Handles date selection from calendar modal
  const handleDatePick = (pickedMonth, pickedYear) => {
    if (pickedYear === year && pickedMonth === month) {
      setRefreshKey(prev => prev + 1); // Refresh data if same month/year selected
    } else if (pickedYear >= MIN_YEAR && pickedYear <= MAX_YEAR) {
      setMonth(pickedMonth);
      setYear(pickedYear);
    }
  };

  // Closes add expense modal and refreshes the expenses list
  const handleAddExpenseClose = () => {
    setShowPopup(false);
    setRefreshKey(prev => prev + 1);
  };

  // Converts category names to valid CSS class names
  const cleanCategoryClassName = (category) => {
    return category
      .toLowerCase()
      .replace(/&/g, 'and')
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9\-]/g, '');
  };

  // Toggles the dropdown menu for a specific expense
  const handleMenuToggle = (expenseId) => {
    setActiveMenu(activeMenu === expenseId ? null : expenseId);
  };

  // Placeholder for change category functionality (not yet implemented)
  const handleChangeCategory = (expense) => {
    console.log('Change category for expense:', expense);
    setActiveMenu(null);
  };

  // Deletes an expense after user confirmation
  const handleDeleteExpense = async (expense) => {
    if (window.confirm(`Are you sure you want to delete "${expense.title}"?`)) {
      try {
        const sessionId = localStorage.getItem('session_id');
        const res = await fetch(`${import.meta.env.VITE_API_URL}/delete_expense`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          },
          body: JSON.stringify({ serial_number: expense.serial_number })
        });

        if (res.ok) {
          setRefreshKey(prev => prev + 1); // Refresh the expenses list
        } else {
          alert('Failed to delete expense');
        }
      } catch (err) {
        console.error('Error deleting expense:', err);
        alert('Error deleting expense');
      }
    }
    setActiveMenu(null);
  };

  return (
    <div className="expenses-container">
      {/* Header with new expense button and filter controls */}
      <div className="expenses-header">
        <button className="new-expense-button" onClick={() => setShowPopup(true)}>✨ New Expense</button>
        <div className="controls">
          <span className="filter-btn">🔍 Filters</span>
          <span className="sort-btn">↕ Sort</span>
        </div>
      </div>

      {/* Month/year navigation controls */}
      <div className="month-picker">
        <button className="arrow-button" onClick={handlePrevMonth}>◀</button>

        <div className="month-display" onClick={() => setCalendarOpen(true)}>
          <span>{getMonthName()}</span>
          <span className="calendar-icon" title="Pick a month">📅</span>
        </div>

        <button className="arrow-button" onClick={handleNextMonth}>▶</button>
      </div>

      {/* Calendar modal for date selection */}
      {calendarOpen && (
        <CalendarModal
          onClose={() => setCalendarOpen(false)}
          onPickDate={handleDatePick}
        />
      )}

      {/* Scrollable table container */}
      <div className="expenses-table-wrapper">
        <table className="expenses-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Date</th>
              <th>Category</th>
              <th>Amount (USD)</th>
              <th>Amount (ILS)</th>
            </tr>
          </thead>
          <tbody>
            {expenses.length > 0 ? (
              expenses.map((exp) => (
                <tr key={exp.serial_number}>
                  <td>{exp.title}</td>
                  <td>{exp.date}</td>
                  <td className={`category-${cleanCategoryClassName(exp.category)}`}>
                    {exp.category}
                  </td>
                  <td className="amount-cell">${exp.amount_usd.toFixed(2)}</td>
                  <td className="amount-cell">₪{exp.amount_ils.toFixed(2)}</td>
                  <td className="actions-cell">
                    {/* Dropdown menu for each expense */}
                    <div className="menu-container">
                      <button 
                        className={`menu-button ${activeMenu === exp.serial_number ? 'active' : ''}`}
                        onClick={() => handleMenuToggle(exp.serial_number)}
                      >
                        ⋯
                      </button>
                      <div className={`menu-dropdown ${activeMenu === exp.serial_number ? 'open' : ''}`}>
                        <button 
                          className="menu-item" 
                          onClick={() => handleChangeCategory(exp)}
                        >
                          🏷️ Change Category
                        </button>
                        <button 
                          className="menu-item delete-item" 
                          onClick={() => handleDeleteExpense(exp)}
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '20px' }}>
                  No expenses found for {getMonthName()}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add expense modal */}
      {showPopup && <AddExpenseModal onClose={handleAddExpenseClose} />}
    </div>
  );
}

export default AllExpenses;
