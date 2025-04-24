document.addEventListener('DOMContentLoaded', function() {
    // Print functionality
    const printBtn = document.getElementById('printBtn');
    if (printBtn) {
      printBtn.addEventListener('click', function() {
        window.print();
      });
    }
    
    // Expand/collapse answers (optional feature)
    const questionSections = document.querySelectorAll('.question-section');
    questionSections.forEach(section => {
      const questionText = section.querySelector('.question-text');
      
      questionText.addEventListener('click', function() {
        const answerSection = section.nextElementSibling;
        if (answerSection && answerSection.classList.contains('answer-section')) {
          answerSection.classList.toggle('expanded');
        }
      });
    });
    
    // Highlight code blocks if any (optional feature)
    const codeBlocks = document.querySelectorAll('pre code');
    if (codeBlocks.length > 0 && typeof hljs !== 'undefined') {
      codeBlocks.forEach(block => {
        hljs.highlightBlock(block);
      });
    }
  });