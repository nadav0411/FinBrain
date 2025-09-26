/* AllExpenses.jsx Nadav */

// Import React hooks and components we need
import React, { useState, useEffect, useRef } from 'react';
import './AllExpenses.css';
import AddExpenseModal from './AddExpenseModal';
import CalendarModal from './CalendarModal';

// Array of month names for display (used in navigation)
const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function AllExpenses() {
  // Get today's date to set initial month/year
  const today = new Date();

  /* ===== STATE ===== */
  // useState is a React hook that lets us store data that can change
  // When this data changes, React automatically re-renders the component
  
  // Modal states - control which popup windows are open
  const [showPopup, setShowPopup] = useState(false);           // Add expense modal
  const [calendarOpen, setCalendarOpen] = useState(false);     // Calendar picker modal
  const [categoryModalOpen, setCategoryModalOpen] = useState(false); // Category change modal
  
  // Date navigation states - track which month/year user is viewing
  const [month, setMonth] = useState(today.getMonth() + 1);    // Current month (1-12)
  const [year, setYear] = useState(today.getFullYear());       // Current year
  const [refreshKey, setRefreshKey] = useState(0);             // Force data refresh when changed
  
  // Data state - holds the actual expense data from server
  const [expenses, setExpenses] = useState([]);                // List of expenses for current month
  
  // Menu states - control which dropdown menus are open
  const [activeMenu, setActiveMenu] = useState(null);          // Which expense's menu is open
  const [sortMenuOpen, setSortMenuOpen] = useState(false);     // Sort dropdown
  const [filterMenuOpen, setFilterMenuOpen] = useState(false); // Filter dropdown
  
  // Sort states - control how expenses are sorted
  const [sortBy, setSortBy] = useState('date');                // What to sort by (date/title/amount/category)
  const [sortOrder, setSortOrder] = useState('desc');          // Sort direction (asc/desc)
  
  // Filter states - control which expenses are shown
  const [selectedCategories, setSelectedCategories] = useState(new Set()); // Selected categories
  const [amountRange, setAmountRange] = useState({ min: '', max: '' });    // USD amount range
  const [amountRangeIls, setAmountRangeIls] = useState({ min: '', max: '' }); // ILS amount range
  
  // Category modal states - handle changing expense categories
  const [categoryModalExpense, setCategoryModalExpense] = useState(null); // Expense being edited
  const [isUpdatingCategory, setIsUpdatingCategory] = useState(false); // Prevents double-clicks

  // useRef creates a reference that persists between renders (doesn't cause re-render when changed)
  const isMountedRef = useRef(true); // Helps us know if component is still mounted
  
  // Constants - values that don't change
  const MIN_YEAR = 2015; // Earliest year user can navigate to
  const MAX_YEAR = 2027; // Latest year user can navigate to

  /* ===== FETCH DATA ===== */
  // This function gets expenses from the server
  const fetchExpenses = async () => {
    // Save current month/year when we start the request
    // This prevents race conditions if user changes month while request is in flight
    const requestMonth = month;
    const requestYear = year;
    
    try {
      // Get user's session ID from browser storage
      const sessionId = localStorage.getItem('session_id');
      
      // Make API request to get expenses for specific month/year
      const res = await fetch(`${import.meta.env.VITE_API_URL}/get_expenses?month=${requestMonth}&year=${requestYear}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Session-ID': sessionId }
      });
      
      // Check if request was successful
      if (!res.ok) throw new Error('Failed to fetch');
      
      // Convert response to JavaScript object
      const data = await res.json();
      
      // Only update if component is still mounted AND user is still viewing same month/year
      if (isMountedRef.current && month === requestMonth && year === requestYear) {
        setExpenses(data.expenses || []); // Update the expenses list
      }
    } catch (err) {
      console.error('Error fetching expenses:', err);
    }
  };

  /* ===== EFFECTS ===== */
  // useEffect is a React hook that runs code when component mounts or when dependencies change
  
  // Effect 1: Fetch expenses when month, year, or refreshKey changes
  // This automatically loads new data when user navigates to different months
  useEffect(() => { fetchExpenses(); }, [month, year, refreshKey]);
  
  // Effect 2: Cleanup when component unmounts
  // This prevents memory leaks by marking the component as unmounted
  useEffect(() => () => { isMountedRef.current = false; }, []);
  
  // Effect 3: Close dropdowns when clicking outside
  // This provides good user experience by closing menus when user clicks elsewhere
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Close expense action menu if clicking outside
      if (activeMenu && !event.target.closest('.menu-container')) setActiveMenu(null);
      // Close sort dropdown if clicking outside
      if (sortMenuOpen && !event.target.closest('.sort-menu-container')) setSortMenuOpen(false);
      // Close filter dropdown if clicking outside
      if (filterMenuOpen && !event.target.closest('.filter-menu-container')) setFilterMenuOpen(false);
    };
    
    // Add event listener to document
    document.addEventListener('mousedown', handleClickOutside);
    
    // Cleanup: Remove event listener when component unmounts
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [activeMenu, sortMenuOpen, filterMenuOpen]);

  /* ===== CATEGORIES ===== */
  // useMemo prevents recalculating this every time the component renders
  // It only recalculates when 'expenses' changes
  const categoryOptions = React.useMemo(() => {
    const unique = new Set(); // Set automatically removes duplicates
    expenses.forEach(e => { if (e?.category) unique.add(e.category); });
    return Array.from(unique).sort((a, b) => a.localeCompare(b)); // Sort alphabetically
  }, [expenses]);

  // Standard list of all possible expense categories
  const allCategories = ['Food & Drinks', 'Housing & Bills', 'Transportation', 'Education & Personal Growth', 'Health & Essentials', 'Leisure & Gifts', 'Other'];

  /* ===== SORT ===== */
  // This function sorts expenses based on current sort settings
  const getSortedExpenses = (list = expenses) => {
    const data = [...list]; // Create a copy to avoid modifying original array
    const direction = sortOrder === 'asc' ? 1 : -1; // 1 for ascending, -1 for descending
    
    data.sort((a, b) => {
      let left, right; // Values to compare
      
      // Get the values to compare based on sort field
      if (sortBy === 'title') {
        left = (a.title || '').toLowerCase(); // Convert to lowercase for case-insensitive sorting
        right = (b.title || '').toLowerCase();
      } else if (sortBy === 'amount') {
        left = Number(a.amount_usd) || 0; // Convert to number, default to 0 if invalid
        right = Number(b.amount_usd) || 0;
      } else if (sortBy === 'category') {
        left = (a.category || '').toLowerCase();
        right = (b.category || '').toLowerCase();
      } else {
        // Default: sort by date (newest first by default)
        left = new Date(a.date).getTime() || 0; // Convert date to timestamp
        right = new Date(b.date).getTime() || 0;
      }
      
      // Compare the values
      if (left < right) return -1 * direction;
      if (left > right) return 1 * direction;
      
      // If values are equal, use date as tie-breaker
      const aTime = new Date(a.date).getTime() || 0;
      const bTime = new Date(b.date).getTime() || 0;
      return (bTime - aTime) * (direction === 1 ? -1 : 1);
    });
    return data;
  };

  /* ===== FILTER ===== */
  // This function filters expenses based on current filter settings
  const getFilteredExpenses = () => {
    let data = [...expenses]; // Start with a copy of all expenses
    
    // Filter by selected categories (if any categories are selected)
    if (selectedCategories.size > 0) {
      data = data.filter(exp => selectedCategories.has(exp.category));
    }
    
    // Filter by USD amount range
    const minUsd = amountRange.min !== '' ? parseFloat(amountRange.min) : null;
    const maxUsd = amountRange.max !== '' ? parseFloat(amountRange.max) : null;
    if (minUsd !== null) data = data.filter(exp => (Number(exp.amount_usd) || 0) >= minUsd);
    if (maxUsd !== null) data = data.filter(exp => (Number(exp.amount_usd) || 0) <= maxUsd);
    
    // Filter by ILS amount range
    const minIls = amountRangeIls.min !== '' ? parseFloat(amountRangeIls.min) : null;
    const maxIls = amountRangeIls.max !== '' ? parseFloat(amountRangeIls.max) : null;
    if (minIls !== null) data = data.filter(exp => (Number(exp.amount_ils) || 0) >= minIls);
    if (maxIls !== null) data = data.filter(exp => (Number(exp.amount_ils) || 0) <= maxIls);
    
    return data;
  };

  // Toggle a category in the filter selection (add if not selected, remove if selected)
  const toggleCategory = (category) => {
    setSelectedCategories(prev => {
      const next = new Set(prev); // Create a copy of the Set
      next.has(category) ? next.delete(category) : next.add(category); // Toggle the category
      return next;
    });
  };

  // Clear all active filters
  const clearFilters = () => {
    setSelectedCategories(new Set()); // Clear selected categories
    setAmountRange({ min: '', max: '' }); // Clear USD range
    setAmountRangeIls({ min: '', max: '' }); // Clear ILS range
  };

  // Count how many filters are currently active (for badge display)
  const activeFilterCount = selectedCategories.size + (amountRange.min !== '' ? 1 : 0) + (amountRange.max !== '' ? 1 : 0) + (amountRangeIls.min !== '' ? 1 : 0) + (amountRangeIls.max !== '' ? 1 : 0);

  // Apply new sort settings and close the sort menu
  const applySort = (field, order) => {
    setSortBy(field); // Set what to sort by
    setSortOrder(order); // Set sort direction
    setSortMenuOpen(false); // Close the dropdown
  };

  /* ===== NAVIGATION ===== */
  // Navigate to the previous month
  const handlePrevMonth = () => {
    if (month === 1 && year > MIN_YEAR) { 
      setMonth(12); setYear(year - 1); // Go to December of previous year
    } else if (month > 1) {
      setMonth(month - 1); // Go to previous month
    }
  };

  // Navigate to the next month
  const handleNextMonth = () => {
    if (month === 12 && year < MAX_YEAR) { 
      setMonth(1); setYear(year + 1); // Go to January of next year
    } else if (month < 12) {
      setMonth(month + 1); // Go to next month
    }
  };

  // Get formatted month and year string for display
  const getMonthName = () => `${monthNames[month - 1]} ${year}`;

  // Handle date selection from calendar modal
  const handleDatePick = (pickedMonth, pickedYear) => {
    if (pickedYear === year && pickedMonth === month) {
      setRefreshKey(prev => prev + 1); // Refresh data if same month/year selected
    } else if (pickedYear >= MIN_YEAR && pickedYear <= MAX_YEAR) {
      setMonth(pickedMonth); setYear(pickedYear); // Navigate to selected month/year
    }
  };

  /* ===== EXPENSE HANDLING ===== */
  // Close the add expense modal
  const handleAddExpenseClose = () => setShowPopup(false);

  // Handle successful expense addition
  const handleExpenseAdded = (expenseDate) => {
    if (!isMountedRef.current) return; // Don't update if component is unmounted
    try {
      if (expenseDate.includes('-')) {
        // Parse date in YYYY-MM-DD format
        const [yearStr, monthStr] = expenseDate.split('-');
        const expenseYear = parseInt(yearStr, 10);
        const expenseMonth = parseInt(monthStr, 10);
        // Only refresh if the new expense is in the currently viewed month/year
        if (expenseMonth === month && expenseYear === year) {
          setRefreshKey(prev => prev + 1);
        }
      } else {
        setRefreshKey(prev => prev + 1); // Fallback: refresh data
      }
    } catch { setRefreshKey(prev => prev + 1); } // Fallback: refresh data
  };

  // Convert category names to valid CSS class names (remove special characters)
  const cleanCategoryClassName = (category) => category.toLowerCase().replace(/&/g, 'and').replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

  // Toggle the dropdown menu for a specific expense
  const handleMenuToggle = (id) => setActiveMenu(activeMenu === id ? null : id);

  // Open the category change modal for a specific expense
  const handleChangeCategory = (expense) => {
    setCategoryModalExpense(expense); // Set which expense to edit
    setCategoryModalOpen(true); // Open the modal
  };

  // Close the category modal and reset related state
  const closeCategoryModal = () => {
    setActiveMenu(null); // Close any open menus
    setCategoryModalOpen(false); // Close the modal
    setCategoryModalExpense(null); // Clear the expense being edited
  };

  // Update an expense's category on the server
  const applyCategoryChange = async (expense, newCategory) => {
    // Skip update in demo mode
    if (localStorage.getItem('is_demo_user') === 'true') {
      closeCategoryModal();
      return;
    }
    
    // Don't update if already updating, no category selected, or same category
    if (isUpdatingCategory || !newCategory || newCategory === expense.category) {
      closeCategoryModal();
      return;
    }
    
    setIsUpdatingCategory(true); // Prevent multiple simultaneous updates
    try {
      const sessionId = localStorage.getItem('session_id');
      const res = await fetch(`${import.meta.env.VITE_API_URL}/update_expense_category`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Session-ID': sessionId },
        body: JSON.stringify({ serial_number: expense.serial_number, current_category: expense.category, new_category: newCategory })
      });
      
      if (res.ok) {
        const body = await res.json().catch(() => ({}));
        if (body?.message || body?.success) setRefreshKey(prev => prev + 1); // Refresh data
      } else {
        alert('Failed to update category');
      }
    } catch (err) {
      console.error('Error updating category:', err);
      alert('Error updating category');
    } finally {
      setIsUpdatingCategory(false); // Reset updating flag
      closeCategoryModal(); // Close the modal
    }
  };

  // Delete an expense from the server
  const handleDeleteExpense = async (expense) => {
    // Skip delete in demo mode
    if (localStorage.getItem('is_demo_user') === 'true') {
      setActiveMenu(null);
      return;
    }
    
    try {
      const sessionId = localStorage.getItem('session_id');
      const res = await fetch(`${import.meta.env.VITE_API_URL}/delete_expense`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Session-ID': sessionId },
        body: JSON.stringify({ serial_number: expense.serial_number })
      });
      
      if (res.ok) {
        const body = await res.json().catch(() => ({}));
        if (body?.message === 'Expense deleted') {
          setRefreshKey(prev => prev + 1); // Refresh the expenses list
        } else {
          alert(body?.message || 'Failed to delete expense');
        }
      } else {
        const body = await res.json().catch(() => ({}));
        alert(body?.message || 'Failed to delete expense');
      }
    } catch (err) {
      console.error('Error deleting expense:', err);
      alert('Error deleting expense');
    } finally {
      setActiveMenu(null); // Close the menu
    }
  };

  /* ===== RENDER ===== */
  // This is what gets displayed on the screen
  return (
    <div className="expenses-container">
      {/* Header section with new expense button and filter controls */}
      <div className="expenses-header">
        <button className="new-expense-button" onClick={() => setShowPopup(true)}>✨ New Expense</button>
        <div className="controls">
          <div className="filter-menu-container" style={{ position: 'relative', display: 'inline-block' }}>
            <button className="filter-btn" onClick={() => setFilterMenuOpen(v => !v)} title="Filter options">
              🔍 Filters
              {activeFilterCount > 0 && <span className="filter-badge" aria-label={`${activeFilterCount} active filters`}>{activeFilterCount}</span>}
            </button>
            <div className={`menu-dropdown ${filterMenuOpen ? 'open' : ''}`}>
              <div className="filter-section">
                <div className="filter-section-title">Categories</div>
                {categoryOptions.length === 0 ? (
                  <div className="filter-empty">No categories yet</div>
                ) : (
                  categoryOptions.map((cat) => (
                    <label key={cat} className="filter-row">
                      <input type="checkbox" checked={selectedCategories.has(cat)} onChange={() => toggleCategory(cat)} />
                      <span className="filter-row-label">{cat}</span>
                    </label>
                  ))
                )}
              </div>
              <hr />
              <div className="filter-section">
                <div className="filter-section-title">Amount (USD)</div>
                <div className="filter-row">
                  <input className="filter-input filter-input--small" type="number" placeholder="Min" value={amountRange.min} onChange={(e) => setAmountRange(prev => ({ ...prev, min: e.target.value }))} />
                  <input className="filter-input filter-input--small" type="number" placeholder="Max" value={amountRange.max} onChange={(e) => setAmountRange(prev => ({ ...prev, max: e.target.value }))} />
                </div>
              </div>
              <div className="filter-section">
                <div className="filter-section-title">Amount (ILS)</div>
                <div className="filter-row">
                  <input className="filter-input filter-input--small" type="number" placeholder="Min" value={amountRangeIls.min} onChange={(e) => setAmountRangeIls(prev => ({ ...prev, min: e.target.value }))} />
                  <input className="filter-input filter-input--small" type="number" placeholder="Max" value={amountRangeIls.max} onChange={(e) => setAmountRangeIls(prev => ({ ...prev, max: e.target.value }))} />
                </div>
              </div>
              <div className="filter-actions">
                <button className="menu-item" onClick={clearFilters}>Clear</button>
                <button className="menu-item" onClick={() => setFilterMenuOpen(false)}>Done</button>
              </div>
            </div>
          </div>
          <div className="sort-menu-container" style={{ position: 'relative', display: 'inline-block' }}>
            <button className="sort-btn" onClick={() => setSortMenuOpen(v => !v)} title="Sort options">
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

      <div className="month-picker">
        <button className="arrow-button" onClick={handlePrevMonth}>◀</button>
        <div className="month-display" onClick={() => setCalendarOpen(true)}>
          <span>{getMonthName()}</span>
          <span className="calendar-icon" title="Pick a month">📅</span>
        </div>
        <button className="arrow-button" onClick={handleNextMonth}>▶</button>
      </div>

      {calendarOpen && <CalendarModal onClose={() => setCalendarOpen(false)} onPickDate={handleDatePick} />}

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
                  <td className={`category-${cleanCategoryClassName(exp.category)}`}>{exp.category}</td>
                  <td className="amount-cell">${exp.amount_usd.toFixed(2)}</td>
                  <td className="amount-cell">₪{exp.amount_ils.toFixed(2)}</td>
                  <td className="actions-cell">
                    <div className="menu-container">
                      <button className={`menu-button ${activeMenu === exp.serial_number ? 'active' : ''}`} onClick={() => handleMenuToggle(exp.serial_number)}>⋯</button>
                      <div className={`menu-dropdown ${activeMenu === exp.serial_number ? 'open' : ''}`}>
                        <button className="menu-item" onClick={() => handleChangeCategory(exp)}>🏷️ Change Category</button>
                        <button className="menu-item delete-item" onClick={() => handleDeleteExpense(exp)}>🗑️ Delete</button>
                      </div>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '20px' }}>No expenses found for {getMonthName()}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showPopup && <AddExpenseModal onClose={handleAddExpenseClose} onExpenseAdded={handleExpenseAdded} />}

      {categoryModalOpen && categoryModalExpense && (
        <div className="modal-overlay" onClick={closeCategoryModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Change Category</h3>
              <button className="modal-close" onClick={closeCategoryModal}>✕</button>
            </div>
            <div className="modal-body">
              <div className="category-grid">
                {allCategories.map((cat) => (
                  <button key={cat} className={`category-tile ${cat === categoryModalExpense.category ? 'current' : ''}`} onClick={() => applyCategoryChange(categoryModalExpense, cat)} disabled={isUpdatingCategory}>
                    {cat}
                  </button>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-button" onClick={closeCategoryModal}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AllExpenses;