import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';
import MonthPickerModal from './MonthPickerModal';

const Dashboard = () => {
  const [showMonthPicker, setShowMonthPicker] = useState(false);
  const selectedGraph = "bar";
  const [selectedCurrency, setSelectedCurrency] = useState("ILS");
  const [selectedMonths, setSelectedMonths] = useState(() => {
    const now = new Date();
    return [{ year: now.getFullYear(), monthIndex: now.getMonth() }];
  });

  const [showEmoji, setShowEmoji] = useState(false);
  const [chartData, setChartData] = useState([
    { category: "Food & Drinks", amount: 0, percentage: 0 },
    { category: "Housing & Bills", amount: 0, percentage: 0 },
    { category: "Transportation", amount: 0, percentage: 0 },
    { category: "Education & Personal Growth", amount: 0, percentage: 0 },
    { category: "Health & Essentials", amount: 0, percentage: 0 },
    { category: "Leisure & Gifts", amount: 0, percentage: 0 },
    { category: "Other", amount: 0, percentage: 0 }
  ]);
  const [total, setTotal] = useState(0);
  const prevValuesRef = useRef({});

  // צבעים לסרגלים
  const barColors = ['blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'teal'];
  
  // כל הקטגוריות שצריכות להופיע
  const allCategories = [
    "Food & Drinks",
    "Housing & Bills", 
    "Transportation",
    "Education & Personal Growth",
    "Health & Essentials",
    "Leisure & Gifts",
    "Other"
  ];

  // שליפת נתונים מהשרת
  const fetchDashboardData = async () => {
    try {
      const sessionId = localStorage.getItem('session_id');
      if (!sessionId) return;

      const params = new URLSearchParams();
      params.append("chart", selectedGraph);
      params.append("currency", selectedCurrency);
      selectedMonths.forEach(({ year, monthIndex }) => {
        const paddedMonth = String(monthIndex + 1).padStart(2, "0");
        params.append("months", `${year}-${paddedMonth}`);
      });

      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/expenses_for_dashboard?${params.toString()}`,
        {
          method: "GET",
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        }
      );

      if (!res.ok) throw new Error("Failed to fetch expenses");

      const data = await res.json();
      const serverData = data.data || [];
      
      // יצירת נתונים עם כל הקטגוריות, גם אלה עם 0
      const completeData = allCategories.map(category => {
        const existingItem = serverData.find(item => item.category === category);
        return existingItem || {
          category: category,
          amount: 0,
          percentage: 0
        };
      });
      
      console.log('Server data:', serverData);
      console.log('Complete data:', completeData);
      setChartData(completeData);
      setTotal(completeData.reduce((sum, item) => sum + item.amount, 0));
    } catch (err) {
      console.error("Error fetching expenses:", err);
    }
  };

  // שליפה אוטומטית כשהמשתמש משנה מטבע/חודש
  useEffect(() => {
    const prev = prevValuesRef.current;
    const changed =
      prev.currency !== selectedCurrency ||
      JSON.stringify(prev.months) !== JSON.stringify(selectedMonths);

    if (changed) {
      prevValuesRef.current = {
        currency: selectedCurrency,
        months: selectedMonths
      };
      fetchDashboardData();
    }
  }, [selectedCurrency, selectedMonths]);

  // החלפת מטבע
  const handleCurrencyToggle = () => {
    setSelectedCurrency((prev) => (prev === "ILS" ? "USD" : "ILS"));
    setShowEmoji(true);
    setTimeout(() => setShowEmoji(false), 800);
  };

  const currencySymbol = selectedCurrency === "ILS" ? "₪" : "$";

  return (
    <div className="dashboard-container">
      {/* כותרת */}
      <div className="dashboard-header">
        <div className="dashboard-title-group">
          <div className="total-display">
            <div className="total-label">Total Expenses</div>
            <div className="total-amount">
              <span className="currency-symbol">{currencySymbol}</span>
              <span className="amount-value">{total.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="date-display">
            {selectedMonths.map(({ year, monthIndex }, idx) => {
              const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
              return (
                <span key={idx} className="date-item">
                  {monthNames[monthIndex]} {year}
                  {idx < selectedMonths.length - 1 && <span className="date-separator">, </span>}
                </span>
              );
            })}
          </div>
        </div>

        <div className="dashboard-buttons">
          <button className="dashboard-button" onClick={() => setShowMonthPicker(true)}>
            📅 Select Date Range
          </button>

          <button className="dashboard-button">
            📊 Bar Graph
          </button>

          <button className="dashboard-button currency-button" onClick={handleCurrencyToggle}>
            💵 {selectedCurrency} ({currencySymbol})
            {showEmoji && <span className="currency-emoji">💱</span>}
          </button>
        </div>
      </div>

      {/* בחירת חודשים */}
      {showMonthPicker && (
        <MonthPickerModal
          onClose={() => setShowMonthPicker(false)}
          onApply={(months) => setSelectedMonths(months)}
        />
      )}

      {/* גרף בר */}
      <div className="bar-chart-section">
        <div className="bar-chart">
          {chartData.map((item, index) => {
            const percent = total > 0 ? (item.amount / total) * 100 : 0;
            const colorClass = barColors[index % barColors.length];
            return (
              <div key={index} className="bar-row">
                <div className="bar-info">
                  <span>{item.category}</span>
                  <span>{currencySymbol}{item.amount.toFixed(2)} • {item.percentage}%</span>
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
      </div>
    </div>
  );
};

export default Dashboard;
