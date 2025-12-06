// ===== Vendor Management JavaScript =====

// Vendor management functionality
class VendorManager {
    constructor() {
        this.vendors = [];
        this.categories = [];
        this.currentView = 'grid';
        this.editingVendorId = null;
        this.deleteVendorId = null;
    }

    // Initialize vendor management
    init() {
        this.setupEventListeners();
        this.loadVendors();
        this.loadCategories();
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.filterVendors();
            }, 300));
        }

        // Category filter
        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                this.filterVendors();
            });
        }

        // Form submission
        const vendorForm = document.getElementById('vendor-form');
        if (vendorForm) {
            vendorForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveVendor();
            });
        }

        // View toggle
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toggleView(btn.dataset.view);
            });
        });
    }

    // Load vendors from API
    async loadVendors() {
        App.showLoading();

        try {
            const response = await App.API.get('/api/vendor/list');
            
            if (response.success) {
                this.vendors = response.vendors;
                this.renderVendors();
            }
        } catch (error) {
            App.showToast('Error loading vendors: ' + error.message, 'error');
        } finally {
            App.hideLoading();
        }
    }

    // Load categories from API
    async loadCategories() {
        try {
            const response = await App.API.get('/api/vendor/categories');
            
            if (response.success) {
                this.categories = response.categories;
                this.populateCategoryFilter();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    populateCategoryFilter() {
        const select = document.getElementById('category-filter');
        if (!select) return;

        // Clear existing options (except the first one)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }

        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    }

    // Render vendors based on current view
    renderVendors() {
        if (this.currentView === 'grid') {
            this.renderGridView();
        } else {
            this.renderTableView();
        }
    }

    renderGridView() {
        const container = document.getElementById('grid-view');
        if (!container) return;

        if (this.vendors.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-users"></i>
                    <h3>No vendors found</h3>
                    <p>Add your first vendor to get started</p>
                    <button class="btn btn-primary" onclick="vendorManager.openAddVendorModal()">
                        <i class="fas fa-plus"></i> Add Vendor
                    </button>
                </div>
            `;
            return;
        }

        container.innerHTML = this.vendors.map(vendor => this.createVendorCard(vendor)).join('');
    }

    renderTableView() {
        const tbody = document.getElementById('vendors-tbody');
        if (!tbody) return;

        if (this.vendors.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-row">No vendors found</td></tr>';
            return;
        }

        tbody.innerHTML = this.vendors.map(vendor => this.createVendorRow(vendor)).join('');
    }

    createVendorCard(vendor) {
        return `
            <div class="vendor-card">
                <div class="vendor-header">
                    <div class="vendor-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="vendor-info">
                        <h3>${vendor.name}</h3>
                        <p>${vendor.company || 'No company'}</p>
                    </div>
                    <div class="vendor-rating">
                        ${this.renderStars(vendor.rating)}
                    </div>
                </div>
                
                <div class="vendor-details">
                    <div class="detail-item">
                        <i class="fas fa-envelope"></i>
                        <span>${vendor.email}</span>
                    </div>
                    ${vendor.phone ? `
                        <div class="detail-item">
                            <i class="fas fa-phone"></i>
                            <span>${vendor.phone}</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="vendor-categories">
                    ${vendor.categories.map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                </div>
                
                <div class="vendor-actions">
                    <button class="btn btn-sm btn-outline" onclick="vendorManager.editVendor(${vendor.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="vendorManager.deleteVendor(${vendor.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }

    createVendorRow(vendor) {
        return `
            <tr>
                <td>
                    <div class="vendor-name-cell">
                        <strong>${vendor.name}</strong>
                    </div>
                </td>
                <td>${vendor.company || '-'}</td>
                <td>${vendor.email}</td>
                <td>${vendor.phone || '-'}</td>
                <td>
                    <div class="categories-cell">
                        ${vendor.categories.map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                    </div>
                </td>
                <td>${this.renderStars(vendor.rating)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline" onclick="vendorManager.editVendor(${vendor.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="vendorManager.deleteVendor(${vendor.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    renderStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;
        let stars = '';
        
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        for (let i = fullStars + (hasHalfStar ? 1 : 0); i < 5; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return `<div class="rating-stars">${stars}</div>`;
    }

    // Toggle between grid and table view
    toggleView(view) {
        this.currentView = view;
        
        // Update button states
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        // Toggle views
        document.getElementById('grid-view').classList.toggle('hidden', view !== 'grid');
        document.getElementById('table-view').classList.toggle('hidden', view !== 'table');
        
        this.renderVendors();
    }

    // Filter vendors based on search and category
    filterVendors() {
        const searchTerm = document.getElementById('search-input').value.toLowerCase();
        const categoryFilter = document.getElementById('category-filter').value;
        
        const filteredVendors = this.vendors.filter(vendor => {
            const matchesSearch = !searchTerm || 
                vendor.name.toLowerCase().includes(searchTerm) ||
                vendor.company.toLowerCase().includes(searchTerm) ||
                vendor.email.toLowerCase().includes(searchTerm);
            
            const matchesCategory = !categoryFilter || 
                vendor.categories.includes(categoryFilter);
            
            return matchesSearch && matchesCategory;
        });
        
        // Temporarily replace vendors for rendering
        const originalVendors = this.vendors;
        this.vendors = filteredVendors;
        this.renderVendors();
        this.vendors = originalVendors;
    }

    // Modal management
    openAddVendorModal() {
        this.editingVendorId = null;
        document.getElementById('modal-title').textContent = 'Add New Vendor';
        document.getElementById('vendor-form').reset();
        App.openModal('vendor-modal');
    }

    editVendor(vendorId) {
        const vendor = this.vendors.find(v => v.id === vendorId);
        if (!vendor) return;
        
        this.editingVendorId = vendorId;
        document.getElementById('modal-title').textContent = 'Edit Vendor';
        
        // Populate form
        document.getElementById('vendor-name').value = vendor.name;
        document.getElementById('vendor-company').value = vendor.company || '';
        document.getElementById('vendor-email').value = vendor.email;
        document.getElementById('vendor-phone').value = vendor.phone || '';
        document.getElementById('vendor-categories').value = vendor.categories.join(', ');
        document.getElementById('vendor-rating').value = vendor.rating;
        document.getElementById('vendor-notes').value = vendor.notes || '';
        
        App.openModal('vendor-modal');
    }

    closeVendorModal() {
        App.closeModal('vendor-modal');
        document.getElementById('vendor-form').reset();
        this.editingVendorId = null;
    }

    // Save vendor (create or update)
    async saveVendor() {
        const form = document.getElementById('vendor-form');
        
        if (!App.validateRequired(form)) {
            App.showToast('Please fill in all required fields', 'error');
            return;
        }

        // Validate email
        const email = document.getElementById('vendor-email').value;
        if (!App.validateEmail(email)) {
            App.showToast('Please enter a valid email address', 'error');
            return;
        }

        const formData = {
            name: document.getElementById('vendor-name').value,
            company: document.getElementById('vendor-company').value,
            email: email,
            phone: document.getElementById('vendor-phone').value,
            categories: document.getElementById('vendor-categories').value
                .split(',')
                .map(cat => cat.trim())
                .filter(cat => cat),
            rating: parseFloat(document.getElementById('vendor-rating').value),
            notes: document.getElementById('vendor-notes').value
        };

        App.showLoading();

        try {
            const url = this.editingVendorId ? `/api/vendor/${this.editingVendorId}` : '/api/vendor/add';
            const method = this.editingVendorId ? 'PUT' : 'POST';
            
            const response = await App.API.request(url, {
                method: method,
                body: JSON.stringify(formData)
            });

            if (response.success) {
                App.showToast(`Vendor ${this.editingVendorId ? 'updated' : 'added'} successfully!`, 'success');
                this.closeVendorModal();
                this.loadVendors();
                this.loadCategories(); // Refresh categories in case new ones were added
            }
        } catch (error) {
            App.showToast(`Error ${this.editingVendorId ? 'updating' : 'adding'} vendor: ` + error.message, 'error');
        } finally {
            App.hideLoading();
        }
    }

    // Delete vendor
    deleteVendor(vendorId) {
        const vendor = this.vendors.find(v => v.id === vendorId);
        if (!vendor) return;
        
        this.deleteVendorId = vendorId;
        document.getElementById('delete-vendor-name').textContent = vendor.name;
        App.openModal('delete-modal');
    }

    closeDeleteModal() {
        App.closeModal('delete-modal');
        this.deleteVendorId = null;
    }

    async confirmDelete() {
        if (!this.deleteVendorId) return;
        
        App.showLoading();

        try {
            const response = await App.API.delete(`/api/vendor/${this.deleteVendorId}`);
            
            if (response.success) {
                App.showToast('Vendor deleted successfully!', 'success');
                this.closeDeleteModal();
                this.loadVendors();
            }
        } catch (error) {
            App.showToast('Error deleting vendor: ' + error.message, 'error');
        } finally {
            App.hideLoading();
        }
    }

    // Utility functions
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

// Initialize Vendor Manager
const vendorManager = new VendorManager();

// Global functions for inline event handlers
window.openAddVendorModal = function() {
    vendorManager.openAddVendorModal();
};

window.editVendor = function(vendorId) {
    vendorManager.editVendor(vendorId);
};

window.deleteVendor = function(vendorId) {
    vendorManager.deleteVendor(vendorId);
};

window.closeVendorModal = function() {
    vendorManager.closeVendorModal();
};

window.closeDeleteModal = function() {
    vendorManager.closeDeleteModal();
};

window.confirmDelete = function() {
    vendorManager.confirmDelete();
};

window.toggleView = function(view) {
    vendorManager.toggleView(view);
};

window.loadVendors = function() {
    vendorManager.loadVendors();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    vendorManager.init();
});
