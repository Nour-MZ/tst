document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const datePicker = document.getElementById('datePicker');
  const prevDayBtn = document.getElementById('prevDayBtn');
  const nextDayBtn = document.getElementById('nextDayBtn');
  const todayBtn = document.getElementById('todayBtn');
  
  // Helper function to format date as YYYY-MM-DD
  function formatDate(date) {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();
    
    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;
    
    return [year, month, day].join('-');
  }
  
  // Setup event listeners
  function setupEventListeners() {
    // Date picker change
    if (datePicker) {
      datePicker.addEventListener('change', function() {
        // Get the selected date
        const selectedDate = new Date(this.value);
        
        // Format the date as YYYY-MM-DD
        const formattedDate = formatDate(selectedDate);
        
        // Navigate to the selected date
        window.location.href = `${window.location.pathname}?date=${formattedDate}`;
      });
    }
    
    // Day navigation buttons
    if (prevDayBtn) {
      prevDayBtn.addEventListener('click', function() {
        // Get the current selected date
        const currentDate = new Date(datePicker.value);
        
        // Subtract 1 day to get the previous day
        const prevDay = new Date(currentDate.setDate(currentDate.getDate() - 1));
        
        // Format the date as YYYY-MM-DD
        const formattedDate = formatDate(prevDay);
        
        // Navigate to the previous day
        window.location.href = `${window.location.pathname}?date=${formattedDate}`;
      });
    }
    
    if (nextDayBtn) {
      nextDayBtn.addEventListener('click', function() {
        // Get the current selected date
        const currentDate = new Date(datePicker.value);
        
        // Add 1 day to get the next day
        const nextDay = new Date(currentDate.setDate(currentDate.getDate() + 1));
        
        // Format the date as YYYY-MM-DD
        const formattedDate = formatDate(nextDay);
        
        // Navigate to the next day
        window.location.href = `${window.location.pathname}?date=${formattedDate}`;
      });
    }
    
    // Today button
    if (todayBtn) {
      todayBtn.addEventListener('click', function() {
        window.location.href = window.location.pathname; // Today
      });
    }
  }

  // Initialize
  setupEventListeners();
});