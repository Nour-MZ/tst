document.addEventListener("DOMContentLoaded", () => {
  const pdfForm = document.getElementById("pdfForm");
  const pdfFileInput = document.getElementById("pdfFile");
  const pdfAlert = document.getElementById("pdfAlert");
  const fileInfo = document.getElementById("fileInfo");
  const fileName = document.getElementById("fileName");
  const fileSize = document.getElementById("fileSize");
  const uploadButton = pdfForm?.querySelector("button[type='submit']");

  // Maximum file size in bytes (2MB)
  const MAX_FILE_SIZE = 2 * 1024 * 1024;

  if (pdfForm) {
      // File input change handler
      pdfFileInput.addEventListener("change", (e) => {
          resetUI();

          const file = e.target.files[0];
          if (!file) return;

          // Validate file type
          const isPDF = file.name.endsWith(".pdf") || file.type === "application/pdf";
          if (!isPDF) {
              showAlert("error", "Please upload a valid PDF file");
              return;
          }

          // Validate file size
          if (file.size > MAX_FILE_SIZE) {
              showAlert("error", `File size exceeds ${formatFileSize(MAX_FILE_SIZE)} limit`);
              return;
          }

          // Show file info
          fileInfo.classList.remove("hidden");
          fileName.textContent = file.name;
          fileSize.textContent = `(${formatFileSize(file.size)})`;

          showAlert("success", "PDF file is ready to be uploaded.");
      });

      // Form submission
      pdfForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          resetUI();

          const file = pdfFileInput.files[0];
          if (!file) {
              showAlert("error", "Please select a PDF file to upload");
              return;
          }

          // Show loading state
          uploadButton.disabled = true;
          uploadButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';

          try {
              const formData = new FormData();
              formData.append('file', file);  // Must match Flask's 'file' key

              const response = await fetch('/upload_cv', {
                  method: 'POST',
                  body: formData,
                  headers: {
                      'X-Requested-With': 'XMLHttpRequest' // Identify as AJAX request
                  }
              });

              if (response.redirected) {
                  // Handle Flask redirect for non-AJAX fallback
                  window.location.href = response.url;
                  return;
              }

              const result = await response.json();

              if (response.ok) {
                  showAlert("success", result.message || "CV uploaded successfully!");
                  // Optional: Clear the file input after successful upload
                  pdfFileInput.value = '';
                  fileInfo.classList.add("hidden");
              } else {
                  showAlert("error", result.error || "Upload failed. Please try again.");
              }
          } catch (error) {
              console.error("Upload error:", error);
              showAlert("error", "Network error. Please check your connection and try again.");
          } finally {
              // Reset button state
              uploadButton.disabled = false;
              uploadButton.innerHTML = '<i class="fas fa-upload"></i> Upload';
          }
      });
  }

  function resetUI() {
      pdfAlert.className = "alert hidden";
      pdfAlert.textContent = "";
  }

  function showAlert(type, message) {
      pdfAlert.textContent = message;
      pdfAlert.className = `alert alert-${type}`;
      pdfAlert.classList.remove("hidden");
      
      // Auto-hide success messages after 5 seconds
      if (type === "success") {
          setTimeout(() => {
              pdfAlert.classList.add("hidden");
          }, 5000);
      }
  }

  function formatFileSize(bytes) {
      if (bytes < 1024) return bytes + " bytes";
      else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
      else return (bytes / 1048576).toFixed(1) + " MB";
  }
});