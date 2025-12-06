// ===== RFP-specific JavaScript =====

// RFP creation and management functionality
class RFPManager {
    constructor() {
        this.currentStep = 1;
        this.rfpData = {};
        this.requirements = [];
    }

    // Initialize RFP creation
    init() {
        this.setupEventListeners();
        this.loadSavedDraft();
    }

    setupEventListeners() {
        // Natural language input auto-resize
        const naturalInput = document.getElementById('natural-input');
        if (naturalInput) {
            naturalInput.addEventListener('input', this.debounce(() => {
                this.autoResizeTextarea(naturalInput);
            }, 300));
        }

        // Form validation
        const rfpForm = document.getElementById('rfp-form');
        if (rfpForm) {
            rfpForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveRFP();
            });
        }

        // Requirement management
        this.setupRequirementListeners();
    }

    setupRequirementListeners() {
        // Add requirement button
        const addBtn = document.querySelector('[onclick="addRequirement()"]');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addRequirement());
        }

        // Auto-save draft
        const form = document.getElementById('rfp-form');
        if (form) {
            form.addEventListener('input', this.debounce(() => {
                this.saveDraft();
            }, 1000));
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    // Generate RFP from natural language
    async generateFromNaturalLanguage(text) {
        if (!text.trim()) {
            App.showToast('Please enter a procurement description', 'error');
            return;
        }

        App.showLoading();

        try {
            const response = await App.API.post('/api/rfp/create', {
                description: text
            });

            if (response.success) {
                this.rfpData = response.rfp;
                this.populateForm(response.ai_parsed);
                this.showStep(2);
                App.showToast('RFP generated successfully!', 'success');
            }
        } catch (error) {
            App.showToast('Error generating RFP: ' + error.message, 'error');
            this.showStep(1);
        } finally {
            App.hideLoading();
        }
    }

    populateForm(parsedData) {
        // Populate basic fields
        document.getElementById('rfp-title').value = parsedData.title || '';
        document.getElementById('rfp-budget').value = parsedData.budget || 0;
        document.getElementById('rfp-deadline').value = parsedData.deadline || '';
        document.getElementById('rfp-description').value = this.rfpData.description || '';
        document.getElementById('payment-terms').value = parsedData.payment_terms || '';
        document.getElementById('warranty-terms').value = parsedData.warranty || '';
        document.getElementById('special-conditions').value = parsedData.special_conditions || '';

        // Populate requirements
        this.populateRequirements(parsedData.items || []);
    }

    populateRequirements(items) {
        const tbody = document.getElementById('requirements-tbody');
        tbody.innerHTML = '';

        items.forEach(item => {
            this.addRequirementRow(item.name || '', item.quantity || 1, item.specs || '');
        });
    }

    addRequirement() {
        this.addRequirementRow('', 1, '');
    }

    addRequirementRow(name = '', quantity = 1, specs = '') {
        const tbody = document.getElementById('requirements-tbody');
        const row = document.createElement('tr');
        const rowId = Date.now();
        
        row.innerHTML = `
            <td><input type="text" class="item-name" value="${name}" placeholder="Item name" required data-row-id="${rowId}"></td>
            <td><input type="number" class="item-quantity" value="${quantity}" min="1" placeholder="Qty" required data-row-id="${rowId}"></td>
            <td><input type="text" class="item-specs" value="${specs}" placeholder="Specifications" data-row-id="${rowId}"></td>
            <td>
                <button type="button" class="btn btn-sm btn-danger" onclick="rfpManager.removeRequirement(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
        
        // Add event listeners for auto-save
        row.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => this.saveDraft());
        });
    }

    removeRequirement(button) {
        const row = button.closest('tr');
        row.remove();
        this.saveDraft();
    }

    collectRequirements() {
        const rows = document.querySelectorAll('#requirements-tbody tr');
        const requirements = [];

        rows.forEach(row => {
            const name = row.querySelector('.item-name').value.trim();
            const quantity = parseInt(row.querySelector('.item-quantity').value);
            const specs = row.querySelector('.item-specs').value.trim();

            if (name && quantity > 0) {
                requirements.push({ name, quantity, specs });
            }
        });

        return requirements;
    }

    // Save RFP
    async saveRFP() {
        const form = document.getElementById('rfp-form');
        
        if (!App.validateRequired(form)) {
            App.showToast('Please fill in all required fields', 'error');
            return;
        }

        const requirements = this.collectRequirements();
        if (requirements.length === 0) {
            App.showToast('Please add at least one requirement', 'error');
            return;
        }

        const rfpData = {
            title: document.getElementById('rfp-title').value,
            budget: parseFloat(document.getElementById('rfp-budget').value),
            deadline: document.getElementById('rfp-deadline').value,
            description: document.getElementById('rfp-description').value,
            requirements: requirements,
            terms: {
                payment_terms: document.getElementById('payment-terms').value,
                warranty: document.getElementById('warranty-terms').value,
                special_conditions: document.getElementById('special-conditions').value
            }
        };

        App.showLoading();

        try {
            const response = await App.API.post('/api/rfp/create', {
                description: rfpData.description,
                ...rfpData
            });

            if (response.success) {
                App.showToast('RFP saved successfully!', 'success');
                this.clearDraft();
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1500);
            }
        } catch (error) {
            App.showToast('Error saving RFP: ' + error.message, 'error');
        } finally {
            App.hideLoading();
        }
    }

    // Draft management
    saveDraft() {
        const formData = {
            title: document.getElementById('rfp-title').value,
            budget: document.getElementById('rfp-budget').value,
            deadline: document.getElementById('rfp-deadline').value,
            description: document.getElementById('rfp-description').value,
            payment_terms: document.getElementById('payment-terms').value,
            warranty_terms: document.getElementById('warranty-terms').value,
            special_conditions: document.getElementById('special-conditions').value,
            requirements: this.collectRequirements()
        };

        App.setLocalStorage('rfp_draft', formData);
        App.setLocalStorage('rfp_draft_timestamp', Date.now());
    }

    loadSavedDraft() {
        const draft = App.getLocalStorage('rfp_draft');
        const timestamp = App.getLocalStorage('rfp_draft_timestamp');
        
        if (draft && timestamp) {
            const hoursOld = (Date.now() - timestamp) / (1000 * 60 * 60);
            
            if (hoursOld < 24) { // Only load if less than 24 hours old
                this.populateDraft(draft);
                App.showToast('Draft restored from previous session', 'info');
            } else {
                this.clearDraft();
            }
        }
    }

    populateDraft(draft) {
        document.getElementById('rfp-title').value = draft.title || '';
        document.getElementById('rfp-budget').value = draft.budget || '';
        document.getElementById('rfp-deadline').value = draft.deadline || '';
        document.getElementById('rfp-description').value = draft.description || '';
        document.getElementById('payment-terms').value = draft.payment_terms || '';
        document.getElementById('warranty-terms').value = draft.warranty_terms || '';
        document.getElementById('special-conditions').value = draft.special_conditions || '';
        
        this.populateRequirements(draft.requirements || []);
    }

    clearDraft() {
        App.removeLocalStorage('rfp_draft');
        App.removeLocalStorage('rfp_draft_timestamp');
    }

    showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.step').forEach(step => {
            step.classList.add('hidden');
        });

        // Show current step
        document.getElementById(`step-${stepNumber}`).classList.remove('hidden');
        this.currentStep = stepNumber;
    }

    debounce(func, wait) {
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
}

// Initialize RFP Manager
const rfpManager = new RFPManager();

// Global functions for inline event handlers
window.generateRFP = function() {
    const input = document.getElementById('natural-input');
    if (input) {
        rfpManager.generateFromNaturalLanguage(input.value);
    }
};

window.addRequirement = function() {
    rfpManager.addRequirement();
};

window.setExample = function(type) {
    const examples = {
        laptops: "I need 20 laptops with 16GB RAM, Intel i7 processors, and 15 monitors 27-inch 4K displays. Budget $50,000. Delivery in 30 days. Payment net 30. 1 year warranty needed.",
        furniture: "We need office furniture for 50 employees: 50 desks, 50 ergonomic chairs, 10 meeting room tables, and storage cabinets. Budget $25,000. Delivery within 45 days. Payment terms 50% upfront, 50% on delivery.",
        software: "Looking for Microsoft Office 365 licenses for 100 users, plus Adobe Creative Cloud for 10 designers. Annual budget $15,000. Need implementation within 2 weeks. Payment annually.",
        infrastructure: "Need to upgrade our server infrastructure: 3 high-performance servers, 2 backup systems, network switches, and UPS systems. Budget $75,000. Installation within 60 days. 3-year warranty required."
    };

    const input = document.getElementById('natural-input');
    if (input && examples[type]) {
        input.value = examples[type];
        rfpManager.autoResizeTextarea(input);
    }
};

window.goBack = function() {
    rfpManager.showStep(1);
};

window.saveRFP = function() {
    rfpManager.saveRFP();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    rfpManager.init();
});
