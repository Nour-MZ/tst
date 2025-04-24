document.addEventListener('DOMContentLoaded', function() {
  // Form submission
  const answerForm = document.getElementById('answerForm');
  const submitBtn = document.getElementById('submitBtn');
  
  if (submitBtn) {
    submitBtn.addEventListener('click', function() {
      answerForm.submit();
    });
  }
  
  // Cancel button
  const cancelBtn = document.getElementById('cancelBtn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', function() {
      if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
        window.location.href = document.querySelector('.back-button').getAttribute('href');
      }
    });
  }
  
  // Save as draft functionality
  const draftBtn = document.getElementById('draftBtn');
  const saveAsDraftBtn = document.getElementById('saveAsDraftBtn');
  
  const saveDraft = function() {
    const answerText = document.getElementById('answer').value;
    
    if (answerText.trim() !== '') {
      // Save to localStorage
      const questionId = window.location.pathname.split('/').pop();
      localStorage.setItem(`draft_answer_${questionId}`, answerText);
      
      alert('Draft saved successfully!');
    } else {
      alert('Please enter some text before saving as draft.');
    }
  };
  
  if (draftBtn) {
    draftBtn.addEventListener('click', saveDraft);
  }
  
  if (saveAsDraftBtn) {
    saveAsDraftBtn.addEventListener('click', saveDraft);
  }
  
  // Load draft if exists
  const loadDraft = function() {
    const questionId = window.location.pathname.split('/').pop();
    const draftText = localStorage.getItem(`draft_answer_${questionId}`);
    
    if (draftText) {
      const answerTextarea = document.getElementById('answer');
      answerTextarea.value = draftText;
      
      // Show notification
      const formGroup = answerTextarea.closest('.form-group');
      const draftNotice = document.createElement('div');
      draftNotice.className = 'draft-notice';
      draftNotice.innerHTML = '<i class="fas fa-info-circle"></i> A draft has been loaded. You can continue editing or submit your answer.';
      draftNotice.style.backgroundColor = 'var(--info-light)';
      draftNotice.style.color = 'var(--info-color)';
      draftNotice.style.padding = '0.75rem';
      draftNotice.style.borderRadius = 'var(--border-radius)';
      draftNotice.style.marginBottom = '1rem';
      draftNotice.style.display = 'flex';
      draftNotice.style.alignItems = 'center';
      draftNotice.style.gap = '0.5rem';
      
      formGroup.insertBefore(draftNotice, answerTextarea);
    }
  };
  
  loadDraft();
  
  // Clear draft on successful submission
  answerForm.addEventListener('submit', function() {
    const questionId = window.location.pathname.split('/').pop();
    localStorage.removeItem(`draft_answer_${questionId}`);
  });
});