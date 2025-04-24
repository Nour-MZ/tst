document.addEventListener("DOMContentLoaded", () => {
    const postJobForm = document.getElementById("postJobForm")
    const saveAsDraftBtn = document.getElementById("saveAsDraft")
    const jobAlert = document.getElementById("jobAlert")
  
    if (postJobForm) {
      // Post job form submission
      postJobForm.addEventListener("submit", (e) => {
        e.preventDefault()
  
        // Basic validation
        if (!validateForm()) {
          return
        }
  
        // Get form data
        const formData = new FormData(postJobForm)
        const jobData = {
          status: "active",
        }
  
        for (const [key, value] of formData.entries()) {
          jobData[key] = value
        }
  
        // In a real app, you would send this data to your backend
        console.log("Job posted:", jobData)
  
        // Show success message
        showAlert("success", "Job posted successfully!")
  
        // Reset form
        postJobForm.reset()
      })
  
      // Save as draft
      if (saveAsDraftBtn) {
        saveAsDraftBtn.addEventListener("click", () => {
          // Get form data
          const formData = new FormData(postJobForm)
          const jobData = {
            status: "draft",
          }
  
          for (const [key, value] of formData.entries()) {
            jobData[key] = value
          }
  
          // In a real app, you would send this data to your backend
          console.log("Job saved as draft:", jobData)
  
          // Show success message
          showAlert("success", "Job saved as draft!")
        })
      }
    }
  
    function validateForm() {
      // Check required fields
      const requiredFields = postJobForm.querySelectorAll("[required]")
      let isValid = true
  
      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          field.classList.add("error")
          isValid = false
        } else {
          field.classList.remove("error")
        }
      })
  
      if (!isValid) {
        showAlert("error", "Please fill in all required fields")
        return false
      }
  
      // Validate salary range
      const salaryMin = document.getElementById("salaryMin").value
      const salaryMax = document.getElementById("salaryMax").value
  
      if (salaryMin && salaryMax && Number.parseInt(salaryMin) > Number.parseInt(salaryMax)) {
        showAlert("error", "Minimum salary cannot be greater than maximum salary")
        return false
      }
  
      return true
    }
  
    function showAlert(type, message) {
      jobAlert.textContent = message
      jobAlert.className = type === "success" ? "alert alert-success" : "alert alert-danger"
    }
  })
  