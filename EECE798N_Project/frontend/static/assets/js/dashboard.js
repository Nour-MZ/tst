document.addEventListener("DOMContentLoaded", () => {
  // Sidebar toggle functionality
  const sidebarToggle = document.getElementById("sidebarToggle")
  const sidebar = document.querySelector(".sidebar")
  const body = document.body

  sidebarToggle.addEventListener("click", () => {
    if (window.innerWidth < 769) {
      sidebar.classList.toggle("active")
    } else {
      body.classList.toggle("sidebar-collapsed")
    }
  })

  // Close sidebar when clicking outside on mobile
  document.addEventListener("click", (event) => {
    if (
      window.innerWidth < 769 &&
      !sidebar.contains(event.target) &&
      !sidebarToggle.contains(event.target) &&
      sidebar.classList.contains("active")
    ) {
      sidebar.classList.remove("active")
    }
  })

  // Handle window resize
  window.addEventListener("resize", () => {
    if (window.innerWidth >= 769) {
      sidebar.classList.remove("active")
    }
  })
})
