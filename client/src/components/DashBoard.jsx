/* DashBoard.jsx */


import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';
import MonthPickerModal from './MonthPickerModal';

const Dashboard = () => {
  // State management - these control what the user sees and interacts with
  const [showMonthPicker, setShowMonthPicker] = useState(false); // Controls if month picker modal is visible
  const [selectedCurrency, setSelectedCurrency] = useState("ILS"); // Current currency (ILS or USD)
  const [selectedMonths, setSelectedMonths] = useState(() => {
    // Initialize with current month - this function runs only once when component mounts
    const now = new Date();
    return [{ year: now.getFullYear(), monthIndex: now.getMonth() }];
  });

  const [showEmoji, setShowEmoji] = useState(false); // Controls currency change animation
  const [showCompareModal, setShowCompareModal] = useState(false); // Controls Compare Graph modal
  const [selectedCompareCategories, setSelectedCompareCategories] = useState(() => new Set());
  const barButtonRef = useRef(null);
  const compareButtonRef = useRef(null);
  const [activePrimaryButton, setActivePrimaryButton] = useState('bar'); // 'bar' | 'compare'
  // Predefined expense categories - these match what the backend expects
  const categories = [
    "Food & Drinks",
    "Housing & Bills", 
    "Transportation",
    "Education & Personal Growth",
    "Health & Essentials",
    "Leisure & Gifts",
    "Other"
  ];
  
  // Chart data state - starts with all categories at 0 amount
  const [chartData, setChartData] = useState(
    categories.map(category => ({ category, amount: 0 }))
  );
  const [total, setTotal] = useState(0); // Sum of all expenses
  const prevValuesRef = useRef({}); // Tracks previous values to detect changes

  // Constants - values that don't change during the component's lifecycle
  const CHART_TYPE = "category_breakdown"; // Type of chart to display
  const barColors = ['blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'teal']; // Colors for each category bar
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]; // Month names for display

  // Function to fetch expense data from the server
  const fetchDashboardData = async () => {
    try {
      // Get user's session ID from browser storage to authenticate the request
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return; // Exit if user not logged in

      // Build query parameters for the API request
      const params = new URLSearchParams();
      params.append("chart", CHART_TYPE);
      params.append("currency", selectedCurrency);
      // Convert selected months to YYYY-MM format for the API
      selectedMonths.forEach(({ year, monthIndex }) => {
        const paddedMonth = String(monthIndex + 1).padStart(2, "0"); // Add leading zero if needed
        params.append("months", `${year}-${paddedMonth}`);
      });

      // Make API call to get expense data
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/expenses_for_dashboard?${params.toString()}`,
        {
          method: "GET",
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId // Send session ID for authentication
          }
        }
      );

      if (!res.ok) throw new Error("Failed to fetch expenses");

      const data = await res.json();
      const serverData = data.data || [];
      
      // Create complete data set - ensure ALL categories are present, even with 0 amounts
      const completeData = categories.map(category => {
        const existingItem = serverData.find(item => item.category === category);
        return existingItem || {
          category: category,
          amount: 0 // Default to 0 if no data for this category
        };
      });
      
      // Update the component state with new data
      setChartData(completeData);
      setTotal(completeData.reduce((sum, item) => sum + item.amount, 0)); // Calculate total expenses
    } catch (err) {
      console.error("Error fetching expenses:", err);
    }
  };

  // Auto-fetch data when user changes currency or selected months
  useEffect(() => {
    const prev = prevValuesRef.current;
    // Check if currency or months have changed since last render
    const changed =
      prev.currency !== selectedCurrency ||
      JSON.stringify(prev.months) !== JSON.stringify(selectedMonths);

    if (changed) {
      // Update the reference with current values
      prevValuesRef.current = {
        currency: selectedCurrency,
        months: selectedMonths
      };
      fetchDashboardData(); // Fetch new data from server
    }
  }, [selectedCurrency, selectedMonths]); // This effect runs when these values change

  // Function to toggle between currencies (ILS ↔ USD)
  const handleCurrencyToggle = () => {
    setSelectedCurrency((prev) => (prev === "ILS" ? "USD" : "ILS"));
    setShowEmoji(true); // Show animation emoji
    setTimeout(() => setShowEmoji(false), 800); // Hide emoji after 800ms
  };

  // Get the correct currency symbol for display
  const currencySymbol = selectedCurrency === "ILS" ? "₪" : "$";

  const allCategories = categories; // alias for readability in modal

  const toggleCompareCategory = (category) => {
    setSelectedCompareCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category); else next.add(category);
      return next;
    });
  };

  const handleApplyCompare = () => {
    // Keep the chosen categories for later compare graph use
    setShowCompareModal(false);
    if (compareButtonRef.current) {
      // Delay focus until after modal unmounts
      setTimeout(() => compareButtonRef.current && compareButtonRef.current.focus(), 0);
    }
    setActivePrimaryButton('compare');
  };

  return (
    <div className="dashboard-container">
      {/* Main header section with total expenses and controls */}
      <div className="dashboard-header">
        <div className="dashboard-title-group">
          {/* Display total expenses with currency symbol */}
          <div className="total-display">
            <div className="total-label">Total Expenses</div>
            <div className="total-amount">
              <span className="currency-symbol">{currencySymbol}</span>
              <span className="amount-value">{total.toFixed(2)}</span>
            </div>
          </div>
          
          {/* Display selected months in readable format */}
          <div className="date-display">
            {selectedMonths.map(({ year, monthIndex }, idx) => (
              <span key={idx} className="date-item">
                {monthNames[monthIndex]} {year}
                {idx < selectedMonths.length - 1 && <span className="date-separator">, </span>}
              </span>
            ))}
          </div>
        </div>

        {/* Control buttons for user interactions */}
        <div className="dashboard-buttons">
          <button className="dashboard-button" onClick={() => setShowMonthPicker(true)}>
            📅 Select Date Range
          </button>

          <button
            ref={compareButtonRef}
            className={`dashboard-button ${activePrimaryButton === 'compare' ? 'active' : ''}`}
            onClick={() => { setShowCompareModal(true); }}
          >
            📈 Monthly Comparison
          </button>

          <button
            ref={barButtonRef}
            className={`dashboard-button ${activePrimaryButton === 'bar' ? 'active' : ''}`}
            onClick={() => { setActivePrimaryButton('bar'); if (barButtonRef.current) barButtonRef.current.focus(); }}
          >
            🧩 Category Breakdown
          </button>

          {/* Currency toggle button with animation */}
          <button className="dashboard-button currency-button" onClick={handleCurrencyToggle}>
            💵 {selectedCurrency} ({currencySymbol})
            {showEmoji && <span className="currency-emoji">💱</span>}
          </button>
        </div>
      </div>

      {/* Month picker modal - only shows when user clicks the date button */}
      {showMonthPicker && (
        <MonthPickerModal
          onClose={() => setShowMonthPicker(false)}
          onApply={(months) => setSelectedMonths(months)}
        />
      )}

      {showCompareModal && (
        <div className="modal-overlay" onClick={() => setShowCompareModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Choose Categories to Compare</h3>
              <button className="modal-close" onClick={() => setShowCompareModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="category-grid">
                {allCategories.map((cat) => (
                  <button
                    key={cat}
                    className={`category-tile ${selectedCompareCategories.has(cat) ? 'current' : ''}`}
                    onClick={() => toggleCompareCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-button" onClick={() => setShowCompareModal(false)}>Cancel</button>
              <button
                className="modal-button"
                onClick={handleApplyCompare}
                disabled={selectedCompareCategories.size === 0}
                aria-disabled={selectedCompareCategories.size === 0}
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bar chart visualization section */}
      <div className="bar-chart-section">
        <div className="bar-chart">
          {chartData.map((item, index) => {
            // Calculate percentage of total for this category
            const percent = total > 0 ? (item.amount / total) * 100 : 0;
            // Assign a color to each category (cycles through the color array)
            const colorClass = barColors[index % barColors.length];
            return (
              <div key={index} className="bar-row">
                {/* Category info row with name, amount, and percentage */}
                <div className="bar-info">
                  <span>{item.category}</span>
                  <span>
                    <span className={`amount text-${colorClass}`}>{currencySymbol}{item.amount.toFixed(2)}</span>
                    <span className="separator">•</span>
                    <span className={`percentage text-${colorClass}`}>{percent.toFixed(1)}%</span>
                  </span>
                </div>
                {/* Visual bar that grows based on percentage */}
                <div className="bar-wrapper">
                  <div
                    className={`bar ${colorClass}`}
                    style={{ width: `${percent}%` }} // CSS width controls bar length
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
