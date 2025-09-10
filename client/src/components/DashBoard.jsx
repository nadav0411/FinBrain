import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';
import MonthPickerModal from './MonthPickerModal';

const Dashboard = () => {
  const [showMonthPicker, setShowMonthPicker] = useState(false);
  const [selectedGraph, setSelectedGraph] = useState("bar");
  const [selectedCurrency, setSelectedCurrency] = useState("ILS");
  const [selectedMonths, setSelectedMonths] = useState([]);
  const [showEmoji, setShowEmoji] = useState(false);

  const prevValuesRef = useRef({});

  // Fetch data
  const fetchDashboardData = async () => {
    try {
      const params = new URLSearchParams();
      params.append("chart", selectedGraph);
      params.append("currency", selectedCurrency);
      selectedMonths.forEach(({ year, monthIndex }) => {
        const paddedMonth = String(monthIndex + 1).padStart(2, "0");
        params.append("months", `${year}-${paddedMonth}`);
      });

      const res = await fetch(`${import.meta.env.VITE_API_URL}/get_expenses?${params.toString()}`, {
        method: "GET"
      });

      if (!res.ok) throw new Error("Failed to fetch expenses");
      const data = await res.json();
      console.log("Fetched data:", data);
    } catch (err) {
      console.error("Error fetching expenses:", err);
    }
  };

  const dashboardRef = useRef(null);
  useEffect(() => {
    const handleClick = () => {
      const prev = prevValuesRef.current;
      const changed =
        prev.chart !== selectedGraph ||
        prev.currency !== selectedCurrency ||
        JSON.stringify(prev.months) !== JSON.stringify(selectedMonths);

      if (changed) {
        prevValuesRef.current = {
          chart: selectedGraph,
          currency: selectedCurrency,
          months: selectedMonths
        };
        fetchDashboardData();
      }
    };

    const node = dashboardRef.current;
    if (node) node.addEventListener("click", handleClick);
    return () => {
      if (node) node.removeEventListener("click", handleClick);
    };
  }, [selectedGraph, selectedCurrency, selectedMonths]);

  const handleCurrencyToggle = () => {
    setSelectedCurrency((prev) => (prev === "ILS" ? "USD" : "ILS"));
    setShowEmoji(true);
    setTimeout(() => setShowEmoji(false), 800); // Emoji disappears after 0.8 sec
  };

  return (
    <div className="dashboard-container" ref={dashboardRef}>
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title-group">
          <h1 className="dashboard-title">Dashboard</h1>
        </div>

        <div className="dashboard-buttons">
          <button
            className="dashboard-button"
            onClick={() => setShowMonthPicker(true)}
          >
            📅 Select Date Range
          </button>

          <button
            className="dashboard-button"
            onClick={() => setSelectedGraph((prev) => prev === "bar" ? "pie" : "bar")}
          >
            📊 {selectedGraph === "bar" ? "Bar Graph" : "Pie Chart"}
          </button>

          <button
            className="dashboard-button currency-button"
            onClick={handleCurrencyToggle}
          >
            💵 {selectedCurrency} ({selectedCurrency === "ILS" ? "₪" : "$"})
            {showEmoji && <span className="currency-emoji">💱</span>}
          </button>
        </div>
      </div>

      {/* Month Picker Modal */}
      {showMonthPicker && (
        <MonthPickerModal
          onClose={() => setShowMonthPicker(false)}
          onApply={(months) => setSelectedMonths(months)}
        />
      )}

      {/* Chart Section */}
      <div className="bar-chart-section">
        <h2 className="bar-chart-title">Expenses by Category</h2>
        <div className="bar-chart">
          {/* Chart would go here */}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
