/* FinBrain Project - DashBoard.jsx - MIT License (c) 2025 Nadav Eshed */


import React, { useState, useEffect, useRef } from 'react';
import './DashBoard.css';
import MonthPickerModal from './MonthPickerModal';

const Dashboard = () => {
  /* =========================
     STATE (data that can change)
     ========================= */

  // Modals (popup windows) visibility
  const [showMonthPicker, setShowMonthPicker] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // User settings
  const [selectedCurrency, setSelectedCurrency] = useState("ILS");
  const [selectedMonths, setSelectedMonths] = useState(() => {
    // Run only once when the component is first loaded
    const now = new Date();
    return [{ year: now.getFullYear(), monthIndex: now.getMonth() }];
  });

  // Chart data and UI state
  const [activePrimaryButton, setActivePrimaryButton] = useState('bar');
  const [chartData, setChartData] = useState([]);
  const [total, setTotal] = useState(0);
  const [monthlyComparisonData, setMonthlyComparisonData] = useState(null);

  // Selected categories for comparison
  const [selectedCompareCategories, setSelectedCompareCategories] = useState(() => new Set());
  const [previousCompareCategories, setPreviousCompareCategories] = useState(() => new Set());

  // Emoji animation when currency changes
  const [showEmoji, setShowEmoji] = useState(false);

  /* =========================
     REFS (values that don't re-render)
     ========================= */
  const barButtonRef = useRef(null);
  const compareButtonRef = useRef(null);
  const isMountedRef = useRef(true); // track if component is still mounted
  const prevValuesRef = useRef({});  // store previous currency/months

  /* =========================
     CONSTANTS
     ========================= */
  const categories = [
    "Food & Drinks",
    "Housing & Bills",
    "Transportation",
    "Education & Personal Growth",
    "Health & Essentials",
    "Leisure & Gifts",
    "Other"
  ];

  const CHART_TYPE = "category_breakdown";
  const barColors = ['blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'teal'];
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  /* =========================
     API CALLS
     ========================= */

  // General function to fetch data from the server
  const fetchChartData = async ({ chartName, categoriesList }, onData) => {
    const requestCurrency = selectedCurrency;
    const requestSelectedMonths = JSON.parse(JSON.stringify(selectedMonths));

    try {
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return;

      // Build query string
      const params = new URLSearchParams();
      params.append("chart", chartName);
      params.append("currency", requestCurrency);

      // Convert month objects into "YYYY-MM"
      requestSelectedMonths.forEach(({ year, monthIndex }) => {
        const paddedMonth = String(monthIndex + 1).padStart(2, "0");
        params.append("months", `${year}-${paddedMonth}`);
      });

      // Handle categories
      if (chartName === 'category_breakdown') {
        params.append("categories", "All");
      } else if (chartName === 'monthly_comparison' && Array.isArray(categoriesList)) {
        categoriesList.forEach((c) => params.append('categories', c));
      }

      // Fetch data
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/expenses_for_dashboard?${params.toString()}`,
        {
          method: "GET",
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        }
      );

      if (!response.ok) throw new Error("Failed to fetch expenses");
      const data = await response.json();

      // Update only if settings didn’t change while loading
      const currencyMatches = selectedCurrency === requestCurrency;
      const monthsMatch = JSON.stringify(selectedMonths) === JSON.stringify(requestSelectedMonths);

      if (!isMountedRef.current) return; // component was unmounted
      if (currencyMatches && monthsMatch && onData) onData(data);

    } catch (error) {
      console.error("Error fetching expenses:", error);
    }
  };

  // Fetch data for the category breakdown chart
  const fetchDashboardData = async () => {
    await fetchChartData({ chartName: CHART_TYPE }, (data) => {
      const serverData = data.data || [];

      // Ensure all categories exist (fill missing with 0)
      const completeData = categories.map(category => {
        const existing = serverData.find(item => item.category === category);
        return existing || { category, amount: 0, percentage: 0 };
      });

      setChartData(completeData);
      setTotal(completeData.reduce((sum, item) => sum + item.amount, 0));
    });
  };

  // Fetch data for monthly comparison chart
  const fetchMonthlyComparison = async (categoryList) => {
    await fetchChartData({ chartName: 'monthly_comparison', categoriesList: categoryList }, (data) => {
      setMonthlyComparisonData(data);
      const sumTotal = (data?.data || []).reduce((acc, item) => acc + (item?.amount || 0), 0);
      setTotal(sumTotal);
    });
  };

  /* =========================
     EFFECTS
     ========================= */

  // Reload charts when currency or months change
  useEffect(() => {
    const prev = prevValuesRef.current;
    const currencyChanged = prev.currency !== selectedCurrency;
    const monthsChanged = JSON.stringify(prev.months) !== JSON.stringify(selectedMonths);

    if (currencyChanged || monthsChanged) {
      prevValuesRef.current = { currency: selectedCurrency, months: selectedMonths };
      fetchDashboardData();

      if (activePrimaryButton === 'compare' && previousCompareCategories.size > 0) {
        fetchMonthlyComparison(Array.from(previousCompareCategories));
      }
    }
  }, [selectedCurrency, selectedMonths]);

  // When unmounted, mark as not mounted
  useEffect(() => {
    return () => { isMountedRef.current = false; };
  }, []);

  /* =========================
     EVENT HANDLERS
     ========================= */

  // Toggle between ILS and USD
  const handleCurrencyToggle = () => {
    setSelectedCurrency((prev) => (prev === "ILS" ? "USD" : "ILS"));
    setShowEmoji(true);
    setTimeout(() => setShowEmoji(false), 800);
  };

  const currencySymbol = selectedCurrency === "ILS" ? "₪" : "$";

  // Toggle category selection for comparison
  const toggleCompareCategory = (category) => {
    setSelectedCompareCategories(prev => {
      const next = new Set(prev);
      next.has(category) ? next.delete(category) : next.add(category);
      return next;
    });
  };

  // Check if current selection is different from saved one
  const hasSelectionChanged = () => {
    if (selectedCompareCategories.size !== previousCompareCategories.size) return true;
    for (const c of selectedCompareCategories) {
      if (!previousCompareCategories.has(c)) return true;
    }
    return false;
  };

  // Apply category comparison
  const handleApplyCompare = () => {
    if (!hasSelectionChanged()) {
      setShowCompareModal(false);
      return;
    }
    setPreviousCompareCategories(new Set(selectedCompareCategories));
    setShowCompareModal(false);

    // Focus the button again
    if (compareButtonRef.current) {
      setTimeout(() => compareButtonRef.current.focus(), 0);
    }

    setActivePrimaryButton('compare');
    const picked = Array.from(selectedCompareCategories);
    if (picked.length > 0) fetchMonthlyComparison(picked);
  };

  const barCount = monthlyComparisonData?.data?.length || 0;

  useEffect(() => {
    document.documentElement.style.setProperty('--bar-count', barCount);
  }, [barCount]);

  /* =========================
     RENDER
     ========================= */
  return (
    <div className="dashboard-container">
      {/* Header with total expenses and buttons */}
      <div className="dashboard-header">
        <div className="dashboard-title-group">
          {/* Show total amount */}
          <div className="total-display">
            <div className="total-label">Total Expenses</div>
            <div className="total-amount">
              <span className="currency-symbol">{currencySymbol}</span>
              <span className="amount-value">{total.toFixed(2)}</span>
            </div>
          </div>

          {/* Show selected months */}
          <div className="date-display">
            {selectedMonths.map(({ year, monthIndex }, idx) => (
              <span key={idx} className="date-item">
                {monthNames[monthIndex]} {year}
                {idx < selectedMonths.length - 1 && <span className="date-separator">, </span>}
              </span>
            ))}
          </div>
        </div>

        {/* Control buttons */}
        <div className="dashboard-buttons">
          <button className="dashboard-button" onClick={() => setShowMonthPicker(true)}>
            📅 Select Date Range
          </button>

          <button
            ref={compareButtonRef}
            className={`dashboard-button ${activePrimaryButton === 'compare' ? 'active' : ''}`}
            onClick={() => {
              setSelectedCompareCategories(new Set(previousCompareCategories));
              setShowCompareModal(true);
            }}
          >
            📈 Monthly Comparison
          </button>

          <button
            ref={barButtonRef}
            className={`dashboard-button ${activePrimaryButton === 'bar' ? 'active' : ''}`}
            onClick={() => {
              setSelectedCompareCategories(new Set());
              setPreviousCompareCategories(new Set());
              setActivePrimaryButton('bar');
              fetchDashboardData();
              if (barButtonRef.current) barButtonRef.current.focus();
            }}
          >
            🧩 Category Breakdown
          </button>

          <button className="dashboard-button currency-button" onClick={handleCurrencyToggle}>
            💵 {selectedCurrency} ({currencySymbol})
            {showEmoji && <span className="currency-emoji">💱</span>}
          </button>
        </div>
      </div>

      {/* Month picker modal */}
      {showMonthPicker && (
        <MonthPickerModal
          onClose={() => setShowMonthPicker(false)}
          onApply={(months) => setSelectedMonths(months)}
        />
      )}

      {/* Compare categories modal */}
      {showCompareModal && (
        <div className="modal-overlay" onClick={() => setShowCompareModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Choose Categories to Compare</h3>
              <button className="modal-close" onClick={() => setShowCompareModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="category-grid">
                {categories.map((c) => (
                  <button
                    key={c}
                    className={`category-tile ${selectedCompareCategories.has(c) ? 'current' : ''}`}
                    onClick={() => toggleCompareCategory(c)}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-button" onClick={() => setShowCompareModal(false)}>Cancel</button>
              <button
                className={`modal-button ${!hasSelectionChanged() ? 'disabled' : ''}`}
                onClick={handleApplyCompare}
                disabled={!hasSelectionChanged()}
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chart area */}
      <div className="bar-chart-section">
        {activePrimaryButton === 'bar' ? (
          /* Category breakdown */
          <div className="bar-chart">
            {chartData.map((item, index) => {
              const percent = item.percentage || 0;
              const colorClass = barColors[index % barColors.length];

              return (
                <div key={index} className="bar-row">
                  <div className="bar-info">
                    <span>{item.category}</span>
                    <span>
                      <span className={`amount text-${colorClass}`}>
                        {currencySymbol}{item.amount.toFixed(2)}
                      </span>
                      <span className="separator">•</span>
                      <span className={`percentage text-${colorClass}`}>
                        {percent.toFixed(1)}%
                      </span>
                    </span>
                  </div>
                  <div className="bar-wrapper">
                    <div
                      className={`bar ${colorClass}`}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Monthly comparison */
          <div className="monthly-comparison-chart">
            {monthlyComparisonData?.data?.length > 0 ? (
              <div className="comparison-bars">
                {monthlyComparisonData.data
                  .sort((a, b) => new Date(a.month) - new Date(b.month))
                  .map((monthData, index) => {
                    const monthDate = new Date(monthData.month + '-01');
                    const monthName = monthNames[monthDate.getMonth()];
                    const year = monthDate.getFullYear();
                    const totalAmount = monthData.amount;
                    const percent = monthData.percentage || 0;
                    const colorClass = barColors[index % barColors.length];

                    return (
                      <div key={monthData.month} className="comparison-bar-row">
                        <div className="comparison-bar-wrapper">
                          <div
                            className={`comparison-bar ${colorClass}`}
                            style={{ height: `${percent}%` }}
                          />
                        </div>
                        <div className="comparison-bar-info">
                          <span className="month-label">{monthName} {year}</span>
                          <span className="month-amount">
                            {currencySymbol}{totalAmount.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    );
                  })}
              </div>
            ) : (
              <div className="no-data-message">
                <p>No monthly comparison data available. Please select categories to compare.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;