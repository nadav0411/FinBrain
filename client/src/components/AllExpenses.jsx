/* AllExpenses.jsx */

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
  const [sortMenuOpen, setSortMenuOpen] = useState(false);     // Controls Sort menu visibility
  const [sortBy, setSortBy] = useState('date');                // Sort field: 'title' | 'amount' | 'category' | 'date'
  const [sortOrder, setSortOrder] = useState('desc');          // Sort order: 'asc' | 'desc'
  const [filterMenuOpen, setFilterMenuOpen] = useState(false); // Controls Filters menu visibility
  const [selectedCategories, setSelectedCategories] = useState(new Set()); // Active category filters
  const [amountRange, setAmountRange] = useState({ min: '', max: '' });    // Active amount range filters (USD)
  const [amountRangeIls, setAmountRangeIls] = useState({ min: '', max: '' }); // Active amount range filters (ILS)
  const [categoryPickerFor, setCategoryPickerFor] = useState(null); // Serial number currently showing category picker (inline)
  const [categoryModalOpen, setCategoryModalOpen] = useState(false); // Controls centered category modal visibility
  const [categoryModalExpense, setCategoryModalExpense] = useState(null); // Expense currently being edited
  const [isUpdatingCategory, setIsUpdatingCategory] = useState(false); // Prevents multiple category updates

  // Year range constraints for navigation
  const MIN_YEAR = 2015;
  const MAX_YEAR = 2027;

  // No local optimistic updates; rely on server confirmation and re-fetch

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
      // Close per-row action menu
      if (activeMenu && !event.target.closest('.menu-container')) {
        setActiveMenu(null);
      }
      // Close sort dropdown
      if (sortMenuOpen && !event.target.closest('.sort-menu-container')) {
        setSortMenuOpen(false);
      }
      // Close filter dropdown
      if (filterMenuOpen && !event.target.closest('.filter-menu-container')) {
        setFilterMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeMenu, sortMenuOpen, filterMenuOpen]);

  // Unique category options derived from the current expenses
  const categoryOptions = React.useMemo(() => {
    const unique = new Set();
    expenses.forEach(e => { if (e && e.category) unique.add(e.category); });
    return Array.from(unique).sort((a, b) => a.localeCompare(b));
  }, [expenses]);

  // Canonical list of categories used across the app
  const allCategories = [
    'Food & Drinks',
    'Housing & Bills',
    'Transportation',
    'Education & Personal Growth',
    'Health & Essentials',
    'Leisure & Gifts',
    'Other'
  ];

  // Returns a sorted copy of the expenses based on current sort settings
  const getSortedExpenses = (list = expenses) => {
    const data = [...list];
    const direction = sortOrder === 'asc' ? 1 : -1;

    data.sort((a, b) => {
      let left;
      let right;

      if (sortBy === 'title') {
        left = (a.title || '').toLowerCase();
        right = (b.title || '').toLowerCase();
      } else if (sortBy === 'amount') {
        left = Number(a.amount_usd) || 0; // Sort by USD amount
        right = Number(b.amount_usd) || 0;
      } else if (sortBy === 'category') {
        left = (a.category || '').toLowerCase();
        right = (b.category || '').toLowerCase();
      } else {
        // Default: sort by date (newest first by default)
        // Expecting YYYY-MM-DD or similar; fallback to 0 if invalid
        left = new Date(a.date).getTime() || 0;
        right = new Date(b.date).getTime() || 0;
      }

      if (left < right) return -1 * direction;
      if (left > right) return 1 * direction;
      // Tie-breaker on date (newer first when desc)
      const aTime = new Date(a.date).getTime() || 0;
      const bTime = new Date(b.date).getTime() || 0;
      return (bTime - aTime) * (direction === 1 ? -1 : 1);
    });

    return data;
  };

  // Returns a filtered copy of the expenses based on filter settings
  const getFilteredExpenses = () => {
    let data = [...expenses];

    // Filter by selected categories (if any)
    if (selectedCategories.size > 0) {
      data = data.filter((e) => selectedCategories.has(e.category));
    }

    // Filter by amount range (USD)
    const min = amountRange.min !== '' ? parseFloat(amountRange.min) : null;
    const max = amountRange.max !== '' ? parseFloat(amountRange.max) : null;
    if (min !== null) {
      data = data.filter((e) => (Number(e.amount_usd) || 0) >= min);
    }
    if (max !== null) {
      data = data.filter((e) => (Number(e.amount_usd) || 0) <= max);
    }

    // Filter by amount range (ILS)
    const minIls = amountRangeIls.min !== '' ? parseFloat(amountRangeIls.min) : null;
    const maxIls = amountRangeIls.max !== '' ? parseFloat(amountRangeIls.max) : null;
    if (minIls !== null) {
      data = data.filter((e) => (Number(e.amount_ils) || 0) >= minIls);
    }
    if (maxIls !== null) {
      data = data.filter((e) => (Number(e.amount_ils) || 0) <= maxIls);
    }

    return data;
  };

  // Toggle a category in the selected set
  const toggleCategory = (category) => {
    setSelectedCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category); else next.add(category);
      return next;
    });
  };

  // Clear all filters
  const clearFilters = () => {
    setSelectedCategories(new Set());
    setAmountRange({ min: '', max: '' });
    setAmountRangeIls({ min: '', max: '' });
  };

  // Count of active filters for badge display
  const activeFilterCount = (() => {
    let count = 0;
    count += selectedCategories.size;
    if (amountRange.min !== '') count += 1;
    if (amountRange.max !== '') count += 1;
    if (amountRangeIls.min !== '') count += 1;
    if (amountRangeIls.max !== '') count += 1;
    return count;
  })();

  // Helpers to change sort settings and close the dropdown
  const applySort = (field, order) => {
    setSortBy(field);
    setSortOrder(order);
    setSortMenuOpen(false);
  };

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

  // Change category: open inline picker within the row menu
  const handleChangeCategory = (expense) => {
    // Open centered modal for category selection
    setCategoryModalExpense(expense);
    setCategoryModalOpen(true);
  };

  // Apply category change and notify server
  const applyCategoryChange = async (expense, newCategory) => {
    // Prevent multiple simultaneous updates
    if (isUpdatingCategory) {
      return;
    }

    if (!newCategory || newCategory === expense.category) {
      setCategoryPickerFor(null);
      setActiveMenu(null);
      setCategoryModalOpen(false);
      setCategoryModalExpense(null);
      return;
    }

    setIsUpdatingCategory(true);
    try {
      const sessionId = localStorage.getItem('session_id');
      const res = await fetch(`${import.meta.env.VITE_API_URL}/update_expense_category`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({ 
          serial_number: expense.serial_number, 
          current_category: expense.category,
          new_category: newCategory 
        })
      });
      if (!res.ok) {
        alert('Failed to update category');
      } else {
        // Only when server confirms, trigger re-fetch so filters/sorting apply
        const body = await res.json().catch(() => ({}));
        if (body && (body.message || body.success)) {
          setRefreshKey(prev => prev + 1);
        }
      }
    } catch (err) {
      console.error('Error updating category:', err);
      alert('Error updating category');
    } finally {
      setIsUpdatingCategory(false);
      setCategoryPickerFor(null);
      setActiveMenu(null);
      setCategoryModalOpen(false);
      setCategoryModalExpense(null);
    }
  };

  // Deletes an expense directly
  const handleDeleteExpense = async (expense) => {
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
        const body = await res.json().catch(() => ({}));
        if (body && body.message === 'Expense deleted') {
          setRefreshKey(prev => prev + 1); // Re-fetch from server
        } else {
          alert(body.message || 'Failed to delete expense');
        }
      } else {
        const body = await res.json().catch(() => ({}));
        alert(body.message || 'Failed to delete expense');
      }
    } catch (err) {
      console.error('Error deleting expense:', err);
      alert('Error deleting expense');
    }
    setActiveMenu(null);
  };

  return (
    <div className="expenses-container">
      {/* Header with new expense button and filter controls */}
      <div className="expenses-header">
        <button className="new-expense-button" onClick={() => setShowPopup(true)}>✨ New Expense</button>
        <div className="controls">
          {/* Filters dropdown menu */}
          <div className="filter-menu-container" style={{ position: 'relative', display: 'inline-block' }}>
            <button
              className="filter-btn"
              onClick={() => setFilterMenuOpen((v) => !v)}
              title="Filter options"
            >
              🔍 Filters
              {activeFilterCount > 0 && (
                <span className="filter-badge" aria-label={`${activeFilterCount} active filters`}>{activeFilterCount}</span>
              )}
            </button>
            <div className={`menu-dropdown ${filterMenuOpen ? 'open' : ''}`}>
              {/* Categories */}
              <div className="filter-section">
                <div className="filter-section-title">Categories</div>
                {categoryOptions.length === 0 ? (
                  <div className="filter-empty">No categories yet</div>
                ) : (
                  categoryOptions.map((cat) => (
                    <label key={cat} className="filter-row">
                      <input
                        type="checkbox"
                        checked={selectedCategories.has(cat)}
                        onChange={() => toggleCategory(cat)}
                      />
                      <span className="filter-row-label">{cat}</span>
                    </label>
                  ))
                )}
              </div>
              <hr />
              {/* Amount range */}
              <div className="filter-section">
                <div className="filter-section-title">Amount (USD)</div>
                <div className="filter-row">
                  <input
                    className="filter-input filter-input--small"
                    type="number"
                    placeholder="Min"
                    value={amountRange.min}
                    onChange={(e) => setAmountRange(prev => ({ ...prev, min: e.target.value }))}
                    step="0.01"
                    min="0"
                  />
                  <input
                    className="filter-input filter-input--small"
                    type="number"
                    placeholder="Max"
                    value={amountRange.max}
                    onChange={(e) => setAmountRange(prev => ({ ...prev, max: e.target.value }))}
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
              <div className="filter-section">
                <div className="filter-section-title">Amount (ILS)</div>
                <div className="filter-row">
                  <input
                    className="filter-input filter-input--small"
                    type="number"
                    placeholder="Min"
                    value={amountRangeIls.min}
                    onChange={(e) => setAmountRangeIls(prev => ({ ...prev, min: e.target.value }))}
                    step="0.01"
                    min="0"
                  />
                  <input
                    className="filter-input filter-input--small"
                    type="number"
                    placeholder="Max"
                    value={amountRangeIls.max}
                    onChange={(e) => setAmountRangeIls(prev => ({ ...prev, max: e.target.value }))}
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
              <div className="filter-actions">
                <button className="menu-item" onClick={clearFilters}>Clear</button>
                <button className="menu-item" onClick={() => setFilterMenuOpen(false)}>Done</button>
              </div>
            </div>
          </div>
          {/* Sort dropdown menu */}
          <div className="sort-menu-container" style={{ position: 'relative', display: 'inline-block' }}>
            <button
              className="sort-btn"
              onClick={() => setSortMenuOpen((v) => !v)}
              title="Sort options"
            >
              ↕ Sort
              {sortBy === 'title' && `: Title ${sortOrder === 'asc' ? 'A→Z' : 'Z→A'}`}
              {sortBy === 'amount' && `: Amount ${sortOrder === 'asc' ? 'Low→High' : 'High→Low'}`}
              {sortBy === 'category' && `: Category ${sortOrder === 'asc' ? 'A→Z' : 'Z→A'}`}
              {sortBy === 'date' && `: Date ${sortOrder === 'asc' ? 'Old→New' : 'New→Old'}`}
            </button>
            <div className={`menu-dropdown ${sortMenuOpen ? 'open' : ''}`} style={{ right: 0 }}>
              <button className="menu-item" onClick={() => applySort('title', 'asc')}>Title A → Z</button>
              <button className="menu-item" onClick={() => applySort('title', 'desc')}>Title Z → A</button>
              <hr style={{ margin: '6px 0', opacity: 0.2 }} />
              <button className="menu-item" onClick={() => applySort('amount', 'asc')}>Amount Low → High</button>
              <button className="menu-item" onClick={() => applySort('amount', 'desc')}>Amount High → Low</button>
              <hr style={{ margin: '6px 0', opacity: 0.2 }} />
              <button className="menu-item" onClick={() => applySort('category', 'asc')}>Category A → Z</button>
              <button className="menu-item" onClick={() => applySort('category', 'desc')}>Category Z → A</button>
            </div>
          </div>
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
              getSortedExpenses(getFilteredExpenses()).map((exp) => (
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
                        {
                          <>
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
                          </>
                        }
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

      {/* Centered Category Selection Modal */}
      {categoryModalOpen && categoryModalExpense && (
        <div className="modal-overlay" onClick={() => { setCategoryModalOpen(false); setCategoryModalExpense(null); }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Change Category</h3>
              <button className="modal-close" onClick={() => { setCategoryModalOpen(false); setCategoryModalExpense(null); }}>✕</button>
            </div>
            <div className="modal-body">
              <div className="category-grid">
                {allCategories.map((cat) => (
                  <button
                    key={cat}
                    className={`category-tile ${cat === categoryModalExpense.category ? 'current' : ''}`}
                    onClick={() => applyCategoryChange(categoryModalExpense, cat)}
                    disabled={isUpdatingCategory}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-button" onClick={() => { setCategoryModalOpen(false); setCategoryModalExpense(null); }}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AllExpenses;
