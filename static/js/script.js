/**
 * AI Email Generator - Main JavaScript File
 * Handles all client-side functionality
 */

// Global variables
let isProcessing = false;
let currentEditingEmail = null;
let fileDropzone = null;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI Email Generator - Initializing...');
    
    initializeApp();
    setupEventListeners();
    restoreFormData();
    
    console.log('✅ AI Email Generator - Ready!');
});

/**
 * Initialize main application components
 */
function initializeApp() {
    // Initialize Bootstrap components
    initializeTooltips();
    initializePopovers();
    
    // Initialize form components
    initializeEmailModeSwitch();
    initializeFileUpload();
    initializeFormValidation();
    
    // Initialize page-specific features
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('generate') || currentPage === '/') {
        initializeEmailPreview();
    }
    
    if (currentPage.includes('generate')) {
        initializeEmailActions();
    }
    
    // Auto-dismiss alerts after 8 seconds
    setTimeout(dismissAlerts, 8000);
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Global form submission handler
    document.addEventListener('submit', handleFormSubmission);
    
    // Global error handler
    window.addEventListener('error', handleGlobalError);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Handle browser back/forward
    window.addEventListener('popstate', handlePopState);
    
    // Auto-save form data
    document.addEventListener('input', debounce(autoSaveFormData, 1000));
    document.addEventListener('change', autoSaveFormData);
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            delay: { show: 500, hide: 100 }
        });
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            trigger: 'hover focus'
        });
    });
}

/**
 * Initialize email mode switching functionality
 */
function initializeEmailModeSwitch() {
    const singleMode = document.getElementById('single_mode');
    const bulkMode = document.getElementById('bulk_mode');
    const singleSection = document.getElementById('single_email_section');
    const bulkSection = document.getElementById('bulk_email_section');

    if (!singleMode || !bulkMode || !singleSection || !bulkSection) return;

    function toggleEmailMode() {
        const isAnimating = 'animating';
        
        if (singleMode.checked) {
            bulkSection.classList.add(isAnimating);
            slideUp(bulkSection, () => {
                bulkSection.style.display = 'none';
                bulkSection.classList.remove(isAnimating);
            });
            
            setTimeout(() => {
                singleSection.style.display = 'block';
                slideDown(singleSection);
            }, 150);
            
            // Update form validation
            setFieldRequired('single_email', true);
            setFieldRequired('bulk_file', false);
            
        } else if (bulkMode.checked) {
            singleSection.classList.add(isAnimating);
            slideUp(singleSection, () => {
                singleSection.style.display = 'none';
                singleSection.classList.remove(isAnimating);
            });
            
            setTimeout(() => {
                bulkSection.style.display = 'block';
                slideDown(bulkSection);
            }, 150);
            
            // Update form validation
            setFieldRequired('single_email', false);
            setFieldRequired('bulk_file', false); // Will be set by file upload validation
        }
    }

    // Event listeners
    singleMode.addEventListener('change', toggleEmailMode);
    bulkMode.addEventListener('change', toggleEmailMode);

    // Initialize
    toggleEmailMode();
}

/**
 * Initialize file upload functionality with drag & drop
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('bulk_file');
    const uploadArea = document.querySelector('.file-upload-area');
    
    if (!fileInput || !uploadArea) return;

    // Create file dropzone
    fileDropzone = new FileDropzone(uploadArea, fileInput, {
        acceptedTypes: ['.csv', '.xlsx', '.xls', '.txt'],
        maxSize: 16 * 1024 * 1024, // 16MB
        onFileSelect: handleFileSelection,
        onError: handleFileError
    });

    // Handle file input change
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            handleFileSelection(this.files[0]);
        }
    });
}

/**
 * File Dropzone Class
 */
class FileDropzone {
    constructor(dropArea, fileInput, options = {}) {
        this.dropArea = dropArea;
        this.fileInput = fileInput;
        this.options = {
            acceptedTypes: options.acceptedTypes || [],
            maxSize: options.maxSize || 10 * 1024 * 1024,
            onFileSelect: options.onFileSelect || (() => {}),
            onError: options.onError || (() => {})
        };
        
        this.setupDropzone();
    }
    
    setupDropzone() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, () => this.highlight(), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, () => this.unhighlight(), false);
        });
        
        // Handle dropped files
        this.dropArea.addEventListener('drop', (e) => this.handleDrop(e), false);
        
        // Handle click to open file dialog
        this.dropArea.addEventListener('click', () => this.fileInput.click());
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight() {
        this.dropArea.classList.add('dragover');
    }
    
    unhighlight() {
        this.dropArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            this.handleFiles(files);
        }
    }
    
    handleFiles(files) {
        const file = files[0]; // Only handle first file
        
        if (this.validateFile(file)) {
            this.fileInput.files = files;
            this.options.onFileSelect(file);
        }
    }
    
    validateFile(file) {
        // Check file type
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (this.options.acceptedTypes.length > 0 && !this.options.acceptedTypes.includes(extension)) {
            this.options.onError(`File type not supported. Please upload: ${this.options.acceptedTypes.join(', ')}`);
            return false;
        }
        
        // Check file size
        if (file.size > this.options.maxSize) {
            this.options.onError(`File too large. Maximum size: ${formatFileSize(this.options.maxSize)}`);
            return false;
        }
        
        return true;
    }
}

/**
 * Handle file selection
 */
function handleFileSelection(file) {
    const fileInfo = document.getElementById('file_info');
    
    if (fileInfo) {
        const fileSize = formatFileSize(file.size);
        const fileName = file.name;
        
        fileInfo.innerHTML = `
            <div class="alert alert-info d-flex align-items-center">
                <i class="fas fa-file-alt fa-2x me-3"></i>
                <div class="flex-grow-1">
                    <h6 class="mb-1">${escapeHtml(fileName)}</h6>
                    <small class="text-muted">Size: ${fileSize}</small>
                </div>
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="clearFileSelection()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        fileInfo.style.display = 'block';
        
        // Show success message
        showToast('File uploaded successfully!', 'success');
    }
}

/**
 * Handle file upload errors
 */
function handleFileError(message) {
    showToast(message, 'error');
}

/**
 * Clear file selection
 */
function clearFileSelection() {
    const fileInput = document.getElementById('bulk_file');
    const fileInfo = document.getElementById('file_info');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) {
        fileInfo.style.display = 'none';
        fileInfo.innerHTML = '';
    }
    
    showToast('File removed', 'info');
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = this.querySelector('.form-control:invalid, .form-select:invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                showToast('Please fill in all required fields correctly.', 'error');
            }
            
            this.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('was-validated')) {
                    if (this.checkValidity()) {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                    } else {
                        this.classList.remove('is-valid');
                        this.classList.add('is-invalid');
                    }
                }
            });
        });
    });
    
    // Custom email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('input', function() {
            const email = this.value.trim();
            if (email && !isValidEmail(email)) {
                this.setCustomValidity('Please enter a valid email address.');
            } else {
                this.setCustomValidity('');
            }
        });
    });
}

/**
 * Initialize email preview functionality
 */
function initializeEmailPreview() {
    // Auto-expand first email preview after delay
    setTimeout(() => {
        const firstCollapse = document.querySelector('.collapse');
        if (firstCollapse && !firstCollapse.classList.contains('show')) {
            const collapseInstance = new bootstrap.Collapse(firstCollapse, {
                show: true
            });
        }
    }, 500);
    
    // Add smooth transitions to all collapses
    const collapses = document.querySelectorAll('.collapse');
    collapses.forEach(collapse => {
        collapse.style.transition = 'all 0.3s ease';
    });
}

/**
 * Initialize email action buttons
 */
function initializeEmailActions() {
    // Send all confirmation
    const sendButtons = document.querySelectorAll('#sendAllBtn, #finalSendBtn');
    sendButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            showConfirmationModal();
        });
    });
}

/**
 * Show confirmation modal for sending emails
 */
function showConfirmationModal() {
    const emailCount = document.querySelectorAll('.email-card').length;
    const modal = document.getElementById('confirmSendModal');
    
    if (modal) {
        const countElement = modal.querySelector('#confirmEmailCount');
        if (countElement) {
            countElement.textContent = emailCount;
        }
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Handle confirmation
        const confirmBtn = modal.querySelector('#confirmSendBtn');
        if (confirmBtn) {
            confirmBtn.onclick = function() {
                modalInstance.hide();
                submitSendForm();
            };
        }
    } else {
        // Fallback to browser confirm
        const confirmed = confirm(`Are you sure you want to send ${emailCount} emails? This action cannot be undone.`);
        if (confirmed) {
            submitSendForm();
        }
    }
}

/**
 * Submit send form
 */
function submitSendForm() {
    const form = document.getElementById('sendAllForm');
    if (form) {
        showLoadingOverlay('Sending emails... This may take a few minutes.');
        form.submit();
    }
}

/**
 * Edit email functionality
 */
function editEmail(emailIndex) {
    const emailCard = document.querySelector(`#email-${emailIndex}`);
    if (!emailCard) return;
    
    const subject = emailCard.querySelector('.subject-display').textContent.trim();
    const bodyElement = emailCard.querySelector('.email-preview');
    const body = bodyElement.innerHTML;
    
    // Populate modal
    document.getElementById('editSubject').value = subject;
    document.getElementById('editBody').value = body;
    
    currentEditingEmail = emailIndex;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editEmailModal'));
    modal.show();
    
    // Focus on subject field
    setTimeout(() => {
        document.getElementById('editSubject').focus();
    }, 300);
}

/**
 * Save email edit
 */
function saveEmailEdit() {
    if (!currentEditingEmail) return;
    
    const newSubject = document.getElementById('editSubject').value.trim();
    const newBody = document.getElementById('editBody').value.trim();
    
    if (!newSubject) {
        showToast('Subject cannot be empty.', 'error');
        return;
    }
    
    if (!newBody) {
        showToast('Email body cannot be empty.', 'error');
        return;
    }
    
    // Update email display
    const emailCard = document.querySelector(`#email-${currentEditingEmail}`);
    if (emailCard) {
        emailCard.querySelector('.subject-display').textContent = newSubject;
        emailCard.querySelector('.email-preview').innerHTML = newBody;
        
        // Add edited indicator
        const header = emailCard.querySelector('.card-header h6');
        if (header && !header.textContent.includes('(Edited)')) {
            header.innerHTML += ' <span class="badge bg-warning text-dark">(Edited)</span>';
        }
    }
    
    // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editEmailModal'));
        modal.hide();
        
        showToast('Email updated successfully!', 'success');
        currentEditingEmail = null;
    }


/**
 * Copy email content to clipboard
 */
function copyEmail(emailIndex) {
    const emailCard = document.querySelector(`#email-${emailIndex}`);
    if (!emailCard) return;
    
    const subject = emailCard.querySelector('.subject-display').textContent.trim();
    const bodyElement = emailCard.querySelector('.email-preview');
    const body = bodyElement.textContent || bodyElement.innerText;
    
    const emailContent = `Subject: ${subject}\n\n${body}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(emailContent).then(() => {
            showToast('Email content copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(emailContent);
        });
    } else {
        fallbackCopyToClipboard(emailContent);
    }
}

/**
 * Fallback copy to clipboard for older browsers
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Email content copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy email content.', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Handle form submission with loading states
 */
function handleFormSubmission(event) {
    const form = event.target;
    
    if (form.id === 'emailGeneratorForm') {
        if (isProcessing) {
            event.preventDefault();
            return false;
        }
        
        // Additional validation for email generator form
        if (!validateEmailGeneratorForm(form)) {
            event.preventDefault();
            return false;
        }
        
        isProcessing = true;
        showLoadingState(form, 'Generating emails with AI...');
    }
    
    if (form.id === 'sendAllForm') {
        if (isProcessing) {
            event.preventDefault();
            return false;
        }
        
        isProcessing = true;
        showLoadingState(form, 'Sending emails through Gmail...');
    }
}

/**
 * Validate email generator form
 */
function validateEmailGeneratorForm(form) {
    const emailType = form.querySelector('select[name="email_type"]');
    const emailMode = form.querySelector('input[name="email_mode"]:checked');
    
    if (!emailType || !emailType.value) {
        showToast('Please select an email type.', 'error');
        emailType.focus();
        return false;
    }
    
    if (emailMode && emailMode.value === 'single') {
        const singleEmail = form.querySelector('input[name="single_email"]');
        if (!singleEmail || !singleEmail.value.trim()) {
            showToast('Please enter a recipient email address.', 'error');
            singleEmail.focus();
            return false;
        }
        
        if (!isValidEmail(singleEmail.value.trim())) {
            showToast('Please enter a valid email address.', 'error');
            singleEmail.focus();
            return false;
        }
    } else if (emailMode && emailMode.value === 'bulk') {
        const bulkFile = form.querySelector('input[name="bulk_file"]');
        if (!bulkFile || !bulkFile.files.length) {
            showToast('Please upload a file with email addresses.', 'error');
            document.querySelector('.file-upload-area').scrollIntoView({ behavior: 'smooth' });
            return false;
        }
        
        if (!isValidFileType(bulkFile.files[0])) {
            showToast('Please upload a valid file type (CSV, Excel, or TXT).', 'error');
            return false;
        }
    }
    
    return true;
}

/**
 * Show loading state for forms
 */
function showLoadingState(form, message = 'Processing...') {
    const submitButton = form.querySelector('button[type="submit"]');
    const generateBtn = form.querySelector('#generateBtn');
    const targetBtn = submitButton || generateBtn;
    
    if (targetBtn) {
        targetBtn.disabled = true;
        targetBtn.dataset.originalText = targetBtn.innerHTML;
        targetBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${message}
        `;
    }
    
    form.classList.add('loading');
    
    // Show loading overlay for long operations
    if (message.includes('Generating') || message.includes('Sending')) {
        setTimeout(() => {
            showLoadingOverlay(message);
        }, 2000);
    }
}

/**
 * Show loading overlay
 */
function showLoadingOverlay(message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        const messageElement = overlay.querySelector('p');
        if (messageElement) {
            messageElement.textContent = message;
        }
        overlay.style.display = 'flex';
    }
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Show toast notifications
 */
function showToast(message, type = 'info', duration = 5000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-notification align-items-center text-white bg-${getBootstrapColorClass(type)} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                ${escapeHtml(message)}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration
    });
    bsToast.show();
    
    // Clean up after toast is hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Handle keyboard shortcuts
 */
function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + Enter to submit active form
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm && !isProcessing) {
            event.preventDefault();
            activeForm.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
    
    // Escape to close modals and overlays
    if (event.key === 'Escape') {
        // Close loading overlay
        hideLoadingOverlay();
        
        // Close open modals
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modalInstance = bootstrap.Modal.getInstance(openModal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        // Close open toasts
        const openToasts = document.querySelectorAll('.toast.show');
        openToasts.forEach(toast => {
            const toastInstance = bootstrap.Toast.getInstance(toast);
            if (toastInstance) {
                toastInstance.hide();
            }
        });
    }
    
    // F5 or Ctrl+R to refresh (with confirmation if processing)
    if (event.key === 'F5' || ((event.ctrlKey || event.metaKey) && event.key === 'r')) {
        if (isProcessing) {
            event.preventDefault();
            const confirmRefresh = confirm('Are you sure you want to refresh? This will cancel the current operation.');
            if (confirmRefresh) {
                window.location.reload();
            }
        }
    }
}

/**
 * Handle global errors
 */
function handleGlobalError(event) {
    console.error('Global error:', event.error);
    
    // Don't show error toasts for network errors during development
    if (window.location.hostname === 'localhost' && event.error && event.error.message) {
        if (event.error.message.includes('Loading module') || 
            event.error.message.includes('Failed to fetch')) {
            return;
        }
    }
    
    showToast('An unexpected error occurred. Please refresh the page.', 'error');
}

/**
 * Handle browser navigation
 */
function handlePopState(event) {
    // Reset processing state on navigation
    isProcessing = false;
    hideLoadingOverlay();
    
    // Clear any form loading states
    const loadingForms = document.querySelectorAll('form.loading');
    loadingForms.forEach(form => {
        form.classList.remove('loading');
        const loadingBtn = form.querySelector('button[disabled][data-original-text]');
        if (loadingBtn) {
            loadingBtn.disabled = false;
            loadingBtn.innerHTML = loadingBtn.dataset.originalText;
            delete loadingBtn.dataset.originalText;
        }
    });
}

/**
 * Auto-save form data to localStorage
 */
function autoSaveFormData(event) {
    const form = event.target.closest('form');
    if (!form || form.id !== 'emailGeneratorForm') return;
    
    try {
        const formData = new FormData(form);
        const formObject = {};
        
        for (let [key, value] of formData.entries()) {
            if (key !== 'bulk_file') { // Don't save file uploads
                formObject[key] = value;
            }
        }
        
        localStorage.setItem('emailGeneratorFormData', JSON.stringify(formObject));
    } catch (error) {
        console.warn('Failed to auto-save form data:', error);
    }
}

/**
 * Restore form data from localStorage
 */
function restoreFormData() {
    try {
        const savedData = localStorage.getItem('emailGeneratorFormData');
        if (!savedData) return;
        
        const formData = JSON.parse(savedData);
        
        Object.keys(formData).forEach(key => {
            const field = document.querySelector(`[name="${key}"]`);
            if (field && field.type !== 'file') {
                if (field.type === 'radio' || field.type === 'checkbox') {
                    if (field.value === formData[key]) {
                        field.checked = true;
                        field.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                } else {
                    field.value = formData[key];
                }
            }
        });
        
        console.log('✅ Form data restored from localStorage');
    } catch (error) {
        console.warn('Failed to restore form data:', error);
        localStorage.removeItem('emailGeneratorFormData');
    }
}

/**
 * Clear saved form data
 */
function clearSavedFormData() {
    localStorage.removeItem('emailGeneratorFormData');
}

/**
 * Auto-dismiss alerts
 */
function dismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (alert.classList.contains('show')) {
            const alertInstance = bootstrap.Alert.getInstance(alert);
            if (alertInstance) {
                alertInstance.close();
            } else {
                alert.remove();
            }
        }
    });
}

// Utility Functions

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate file type
 */
function isValidFileType(file) {
    const allowedTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain'
    ];
    const allowedExtensions = ['csv', 'xls', 'xlsx', 'txt'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    return allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Set field required state
 */
function setFieldRequired(fieldName, required) {
    const field = document.querySelector(`[name="${fieldName}"]`);
    if (field) {
        field.required = required;
        
        // Update visual indication
        const label = document.querySelector(`label[for="${field.id}"], label`);
        if (label && label.textContent.includes(fieldName.replace('_', ' '))) {
            if (required && !label.textContent.includes('*')) {
                label.innerHTML += ' <span class="text-danger">*</span>';
            } else if (!required && label.textContent.includes('*')) {
                label.innerHTML = label.innerHTML.replace(' <span class="text-danger">*</span>', '');
            }
        }
    }
}

/**
 * Get Bootstrap color class for toast type
 */
function getBootstrapColorClass(type) {
    const colorMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return colorMap[type] || 'primary';
}

/**
 * Get Font Awesome icon for toast type
 */
function getToastIcon(type) {
    const iconMap = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return iconMap[type] || 'bell';
}

/**
 * Slide animation helpers
 */
function slideDown(element, callback) {
    element.style.height = 'auto';
    const height = element.scrollHeight;
    element.style.height = '0px';
    element.style.opacity = '0';
    element.style.overflow = 'hidden';
    element.style.transition = 'height 0.3s ease, opacity 0.3s ease';
    
    requestAnimationFrame(() => {
        element.style.height = height + 'px';
        element.style.opacity = '1';
    });
    
    setTimeout(() => {
        element.style.height = 'auto';
        element.style.overflow = '';
        element.style.transition = '';
        if (callback) callback();
    }, 300);
}

function slideUp(element, callback) {
    element.style.height = element.scrollHeight + 'px';
    element.style.opacity = '1';
    element.style.overflow = 'hidden';
    element.style.transition = 'height 0.3s ease, opacity 0.3s ease';
    
    requestAnimationFrame(() => {
        element.style.height = '0px';
        element.style.opacity = '0';
    });
    
    setTimeout(() => {
        element.style.overflow = '';
        element.style.transition = '';
        if (callback) callback();
    }, 300);
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Performance optimization - Intersection Observer for lazy loading
 */
function setupLazyLoading() {
    if (!window.IntersectionObserver) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const emailPreview = entry.target.querySelector('.email-preview');
                if (emailPreview && !emailPreview.dataset.loaded) {
                    // Simulate loading email content
                    emailPreview.dataset.loaded = 'true';
                    observer.unobserve(entry.target);
                }
            }
        });
    }, {
        rootMargin: '50px'
    });
    
    document.querySelectorAll('.email-card').forEach(card => {
        observer.observe(card);
    });
}

/**
 * Initialize lazy loading when on email generation page
 */
if (window.location.pathname.includes('generate')) {
    document.addEventListener('DOMContentLoaded', setupLazyLoading);
}

/**
 * Clear saved data on successful completion
 */
window.addEventListener('beforeunload', function() {
    if (window.location.pathname.includes('success')) {
        clearSavedFormData();
    }
});

/**
 * Add smooth scroll behavior to all anchor links
 */
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

/**
 * Initialize tooltips for dynamically created elements
 */
function initializeNewTooltips() {
    const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]:not(.tooltip-initialized)'));
    tooltips.forEach(function(tooltipTriggerEl) {
        tooltipTriggerEl.classList.add('tooltip-initialized');
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Periodically check for new tooltip elements
 */
setInterval(initializeNewTooltips, 2000);

console.log('📧 AI Email Generator JavaScript - Loaded Successfully! 🚀');

