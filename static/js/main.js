/**
 * Main JavaScript file for Ansible Playbook Generator
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle form submission
    const generateForm = document.getElementById('generate-form');
    if (generateForm) {
        generateForm.addEventListener('submit', function() {
            const submitButton = document.getElementById('generate-btn');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
            }
        });
    }

    // Handle file navigation
    const fileLinks = document.querySelectorAll('[data-bs-toggle="list"]');
    if (fileLinks.length > 0) {
        fileLinks.forEach(function(fileLink) {
            fileLink.addEventListener('shown.bs.tab', function(event) {
                // Re-highlight the code in the newly shown tab
                const tabId = event.target.getAttribute('href');
                const codeBlock = document.querySelector(tabId + ' pre code');
                if (codeBlock && hljs) {
                    hljs.highlightElement(codeBlock);
                }
            });
        });
    }

    // Initialize syntax highlighting
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach(function(block) {
            hljs.highlightElement(block);
        });
    }

    // Copy code to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-code-btn');
    if (copyButtons.length > 0) {
        copyButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const codeBlock = this.closest('.code-container').querySelector('code');
                const textToCopy = codeBlock.textContent;
                
                navigator.clipboard.writeText(textToCopy).then(function() {
                    // Success feedback
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    button.classList.add('btn-success');
                    button.classList.remove('btn-outline-secondary');
                    
                    setTimeout(function() {
                        button.innerHTML = originalText;
                        button.classList.remove('btn-success');
                        button.classList.add('btn-outline-secondary');
                    }, 2000);
                }).catch(function(err) {
                    console.error('Could not copy text: ', err);
                });
            });
        });
    }
});
