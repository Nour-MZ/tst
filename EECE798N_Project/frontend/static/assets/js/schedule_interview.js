document.addEventListener("DOMContentLoaded", () => {
    // Initialize variables
    const currentDate = new Date();
    let meetings = meetingsData || []; // Use data from Flask or empty array if not available
  
    // DOM elements
    const meetingForm = document.getElementById("meeting-form");
    const calendarDays = document.getElementById("calendar-days");
    const currentMonthElement = document.getElementById("current-month");
    const prevMonthButton = document.getElementById("prev-month");
    const nextMonthButton = document.getElementById("next-month");
    const meetingsContainer = document.getElementById("meetings-container");
    const meetingModal = document.getElementById("meeting-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalContent = document.getElementById("modal-content");
    const closeModal = document.querySelector(".close-modal");
    const formTitle = document.getElementById("form-title");
  
    // Initialize the calendar
    updateCalendar();
  
    // Update meeting list
    updateMeetingList();
  
    // Event listeners
    prevMonthButton.addEventListener("click", () => changeMonth(-1));
    nextMonthButton.addEventListener("click", () => changeMonth(1));
    closeModal.addEventListener("click", () => (meetingModal.style.display = "none"));
  
    if (meetingForm) {
      meetingForm.addEventListener("submit", handleFormSubmit);
      meetingForm.addEventListener("reset", () => {
        // Reset the form to "new meeting" mode on cancel
        setTimeout(resetForm, 0);
      });
    }
  
    window.addEventListener("click", (event) => {
      if (event.target === meetingModal) {
        meetingModal.style.display = "none";
      }
    });
  
    // Functions
    function updateCalendar() {
      // Update the month display
      const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
      ];
      currentMonthElement.textContent = `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
  
      // Clear the calendar
      calendarDays.innerHTML = "";
  
      // Get the first day of the month
      const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  
      // Get the day of the week for the first day (0 = Sunday, 6 = Saturday)
      const firstDayIndex = firstDay.getDay();
  
      // Get the number of days in the month
      const daysInMonth = lastDay.getDate();
  
      // Get the number of days in the previous month
      const prevLastDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0);
      const prevDaysInMonth = prevLastDay.getDate();
  
      // Calculate the number of days to display from the previous month
      const prevDays = firstDayIndex;
  
      // Calculate the number of days to display from the next month
      const nextDays = 42 - (prevDays + daysInMonth); // 42 = 6 rows of 7 days
  
      // Create calendar days
  
      // Previous month days
      for (let i = prevDays - 1; i >= 0; i--) {
        const dayElement = createDayElement(prevDaysInMonth - i, "other-month");
        calendarDays.appendChild(dayElement);
      }
  
      // Current month days
      const today = new Date();
      for (let i = 1; i <= daysInMonth; i++) {
        const isToday =
          i === today.getDate() &&
          currentDate.getMonth() === today.getMonth() &&
          currentDate.getFullYear() === today.getFullYear();
  
        const dayElement = createDayElement(i, isToday ? "today" : "");
  
        // Add meeting indicators
        const meetingDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
        const dayMeetings = getMeetingsForDate(meetingDate);
  
        if (dayMeetings.length > 0) {
          const meetingsDiv = document.createElement("div");
          meetingsDiv.className = "day-meetings";
  
          dayMeetings.forEach((meeting) => {
            const meetingItem = document.createElement("div");
            meetingItem.className = "meeting-item";
            meetingItem.textContent = meeting.title;
            meetingItem.dataset.meetingId = meeting.id;
            meetingItem.addEventListener("click", (e) => {
              e.stopPropagation();
              showMeetingDetails(meeting);
            });
            meetingsDiv.appendChild(meetingItem);
          });
  
          dayElement.appendChild(meetingsDiv);
        }
  
        calendarDays.appendChild(dayElement);
      }
  
      // Next month days
      for (let i = 1; i <= nextDays; i++) {
        const dayElement = createDayElement(i, "other-month");
        calendarDays.appendChild(dayElement);
      }
    }
  
    function createDayElement(day, className) {
      const dayElement = document.createElement("div");
      dayElement.className = `calendar-day ${className}`;
  
      const dayNumber = document.createElement("div");
      dayNumber.className = "day-number";
      dayNumber.textContent = day;
  
      dayElement.appendChild(dayNumber);
      return dayElement;
    }
  
    function changeMonth(delta) {
      currentDate.setMonth(currentDate.getMonth() + delta);
      updateCalendar();
    }
  
    function formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    }
  
    function getMeetingsForDate(date) {
      const dateString = formatDate(date);
      return meetings.filter((meeting) => meeting.date === dateString);
    }
  
    function updateMeetingList() {
      meetingsContainer.innerHTML = "";
  
      // Sort meetings by date and time
      const sortedMeetings = [...meetings].sort((a, b) => {
        if (a.date !== b.date) {
          return new Date(a.date) - new Date(b.date);
        }
        return a.start_time.localeCompare(b.start_time);
      });
  
      // Filter to show only upcoming meetings
      const today = new Date();
      today.setHours(0, 0, 0, 0);
  
      const upcomingMeetings = sortedMeetings.filter((meeting) => {
        const meetingDate = new Date(meeting.date);
        return meetingDate >= today;
      });
  
      if (upcomingMeetings.length === 0) {
        const noMeetings = document.createElement("p");
        noMeetings.textContent = "No upcoming meetings scheduled.";
        meetingsContainer.appendChild(noMeetings);
        return;
      }
  
      upcomingMeetings.forEach((meeting) => {
        const meetingCard = document.createElement("div");
        meetingCard.className = "meeting-card";
        meetingCard.dataset.meetingId = meeting.id;
  
        // Format the date
        const meetingDate = new Date(meeting.date);
        const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
        const formattedDate = meetingDate.toLocaleDateString("en-US", options);
  
        // Determine if it's today, tomorrow, or another day
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
  
        let dateDisplay;
        if (meetingDate.getTime() === today.getTime()) {
          dateDisplay = "Today";
        } else if (meetingDate.getTime() === tomorrow.getTime()) {
          dateDisplay = "Tomorrow";
        } else {
          dateDisplay = formattedDate;
        }
  
        // Create meeting card content
        meetingCard.innerHTML = `
          <div class="meeting-time">${meeting.start_time} - ${meeting.end_time}</div>
          <div class="meeting-details">
              <h4>${meeting.title}</h4>
              <div class="meeting-meta">
                  <span class="meeting-date"><i class="fas fa-calendar-alt"></i> ${dateDisplay}</span>
                  ${meeting.applicant_name ? `<span class="meeting-applicant"><i class="fas fa-user"></i> ${meeting.applicant_name}</span>` : ""}
              </div>
          </div>
        `;
  
        meetingCard.addEventListener("click", () => showMeetingDetails(meeting));
  
        meetingsContainer.appendChild(meetingCard);
      });
    }
  
    function showMeetingDetails(meeting) {
      modalTitle.textContent = meeting.title;
  
      // Format the date
      const meetingDate = new Date(meeting.date);
      const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
      const formattedDate = meetingDate.toLocaleDateString("en-US", options);
  
      // Create modal content
      let modalHTML = `
        <div class="modal-meeting-details">
            <div class="detail-row">
                <span class="detail-label">Date:</span>
                <span class="detail-value">${formattedDate}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Time:</span>
                <span class="detail-value">${meeting.start_time} - ${meeting.end_time}</span>
            </div>`;
  
      if (meeting.applicant_name) {
        modalHTML += `
            <div class="detail-row">
                <span class="detail-label">Applicant:</span>
                <span class="detail-value">${meeting.applicant_name}</span>
            </div>`;
      }
  
      if (meeting.job_title) {
        modalHTML += `
            <div class="detail-row">
                <span class="detail-label">Position:</span>
                <span class="detail-value">${meeting.job_title}</span>
            </div>`;
      }
  
      modalHTML += `
        </div>
        <div class="modal-actions">
            <button class="btn-secondary" onclick="editMeeting(${meeting.id})">Edit Meeting</button>
        </div>
      `;
  
      modalContent.innerHTML = modalHTML;
      meetingModal.style.display = "block";
    }
  
    function handleFormSubmit(event) {
      // Form submission is handled by Flask
      // This function is kept for potential client-side validation
  
      // Get form data
      const formData = new FormData(meetingForm);
      const meetingData = {
        title: formData.get("title"),
        date: formData.get("date"),
        start_time: formData.get("start_time"),
        end_time: formData.get("end_time")
      };
  
      // Validate form data
      if (!validateMeetingData(meetingData)) {
        event.preventDefault(); // Prevent form submission if validation fails
        return false;
      }
  
      return true; // Allow form submission
    }
  
    function validateMeetingData(meetingData) {
      // Check if end time is after start time
      if (meetingData.start_time >= meetingData.end_time) {
        alert("End time must be after start time.");
        return false;
      }
  
      // Check for conflicts with existing meetings
      const meetingId = document.getElementById("meeting-id").value;
  
      const conflicts = meetings.filter((meeting) => {
        // Skip the current meeting when checking for conflicts (for edits)
        if (meetingId && meeting.id == meetingId) {
          return false;
        }
  
        if (meeting.date !== meetingData.date) {
          return false;
        }
  
        const newStart = meetingData.start_time;
        const newEnd = meetingData.end_time;
        const existingStart = meeting.start_time;
        const existingEnd = meeting.end_time;
  
        // Check if the new meeting overlaps with an existing meeting
        return newStart < existingEnd && newEnd > existingStart;
      });
  
      if (conflicts.length > 0) {
        alert("This meeting conflicts with an existing meeting. Please choose a different time.");
        return false;
      }
  
      return true;
    }
  
    function resetForm() {
      meetingForm.reset();
  
      // Reset the meeting ID and other hidden fields
      document.getElementById("meeting-id").value = "";
  
      // Reset the form title
      if (formTitle) {
        formTitle.textContent = "Schedule a New Meeting";
      }
  
      // Reset the submit button text
      const submitButton = meetingForm.querySelector('button[type="submit"]');
      if (submitButton && submitButton.dataset.originalText) {
        submitButton.textContent = submitButton.dataset.originalText;
      } else if (submitButton) {
        submitButton.textContent = "Schedule Meeting";
      }
    }
  
    // Edit meeting function
    window.editMeeting = (meetingId) => {
      const meeting = meetings.find((m) => m.id == meetingId);
      if (!meeting) return;
  
      // Update form action if applicant_id and job_id are available
      if (meeting.applicant_id && meeting.job_id) {
        document.getElementById("applicant-id").value = meeting.applicant_id;
        document.getElementById("job-id").value = meeting.job_id;
      }
  
      // Populate the form with meeting data
      document.getElementById("meeting-id").value = meetingId;
      document.getElementById("title").value = meeting.title;
      document.getElementById("date").value = meeting.date;
      document.getElementById("start-time").value = meeting.start_time;
      document.getElementById("end-time").value = meeting.end_time;
  
      // Update the form title
      if (formTitle) {
        formTitle.textContent = "Edit Meeting";
      }
  
      // Change the submit button text
      const submitButton = meetingForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.dataset.originalText = submitButton.textContent;
        submitButton.textContent = "Update Meeting";
      }
  
      // Scroll to the form
      document.getElementById("schedule").scrollIntoView({ behavior: "smooth" });
  
      // Close the modal
      meetingModal.style.display = "none";
    };
  });
  // In your schedule_interview.js, update the editMeeting function:
window.editMeeting = function(meetingId) {
    const meeting = meetings.find(m => m.id == meetingId);
    if (!meeting) return;

    // Populate the form
    document.getElementById("meeting-id").value = meeting.id;
    document.getElementById("title").value = meeting.meeting_title;
    document.getElementById("date").value = meeting.meeting_date;
    document.getElementById("start-time").value = meeting.start_time;
    document.getElementById("end-time").value = meeting.end_time;

    // Update UI
    document.getElementById("form-title").textContent = "Edit Meeting";
    document.querySelector("#meeting-form button[type='submit']").textContent = "Update Meeting";

    // Scroll to form
    document.getElementById("schedule").scrollIntoView({ behavior: "smooth" });
    meetingModal.style.display = "none";
};

// Add reset function
window.resetForm = function() {
    document.getElementById("meeting-form").reset();
    document.getElementById("meeting-id").value = "";
    document.getElementById("form-title").textContent = "Schedule New Meeting";
    document.querySelector("#meeting-form button[type='submit']").textContent = "Schedule Meeting";
};