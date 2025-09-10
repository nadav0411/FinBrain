import React, { useState, useEffect } from 'react';
import './AllExpenses.css';
import AddExpenseModal from './AddExpenseModal';
import CalendarModal from './CalendarModal';

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function AllExpenses() {
  const today = new Date();

  const [showPopup, setShowPopup] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [year, setYear] = useState(today.getFullYear());
  const [expenses, setExpenses] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  const MIN_YEAR = 2015;
  const MAX_YEAR = 2027;

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

  useEffect(() => {
    fetchExpenses();
  }, [month, year, refreshKey]);

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

  const getMonthName = () => {
    return `${monthNames[month - 1]} ${year}`;
  };

  const handleDatePick = (pickedMonth, pickedYear) => {
    if (pickedYear === year && pickedMonth === month) {
      setRefreshKey(prev => prev + 1);
    } else if (pickedYear >= MIN_YEAR && pickedYear <= MAX_YEAR) {
      setMonth(pickedMonth);
      setYear(pickedYear);
    }
  };

  const handleAddExpenseClose = () => {
    setShowPopup(false);
    setRefreshKey(prev => prev + 1);
  };

  const cleanCategoryClassName = (category) => {
    return category
      .toLowerCase()
      .replace(/&/g, 'and')
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9\-]/g, '');
  };

  return (
    <div className="expenses-container">
      <div className="expenses-header">
        <button className="new-expense-button" onClick={() => setShowPopup(true)}>✨ New Expense</button>
        <div className="controls">
          <span className="filter-btn">🔍 Filters</span>
          <span className="sort-btn">↕ Sort</span>
        </div>
      </div>

      <div className="month-picker">
        <button className="arrow-button" onClick={handlePrevMonth}>◀</button>

        <div className="month-display" onClick={() => setCalendarOpen(true)}>
          <span>{getMonthName()}</span>
          <span className="calendar-icon" title="Pick a month">📅</span>
        </div>

        <button className="arrow-button" onClick={handleNextMonth}>▶</button>
      </div>

      {calendarOpen && (
        <CalendarModal
          onClose={() => setCalendarOpen(false)}
          onPickDate={handleDatePick}
        />
      )}

      {/* 🛠️ עטפנו את הטבלה בקונטיינר עם גלילה */}
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
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>
                  No expenses found for {getMonthName()}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showPopup && <AddExpenseModal onClose={handleAddExpenseClose} />}
    </div>
  );
}

export default AllExpenses;
