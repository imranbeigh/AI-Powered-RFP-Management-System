// ===== Proposals Management JavaScript =====

// Proposals management functionality
class ProposalsManager {
    constructor() {
        this.rfps = [];
        this.proposals = [];
        this.selectedRFP = null;
        this.comparisonData = null;
    }

    // Initialize proposals management
    init() {
        this.setupEventListeners();
        this.loadRFPs();
        
        // Check for URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const rfpId = urlParams.get('rfp_id');
        if (rfpId) {
            setTimeout(() => {
                document.getElementById('rfp-select').value = rfpId;
                this.loadProposals();
            }, 500);
        }
    }

    setupEventListeners() {
        // RFP selection
        const rfpSelect = document.getElementById('rfp-select');
        if (rfpSelect) {
            rfpSelect.addEventListener('change', () => {
                this.loadProposals();
            });
        }
    }

    // Load RFPs from API
    async loadRFPs() {
        try {
            const response = await App.API.get('/api/rfp/list');
            
            if (response.success) {
                this.rfps = response.rfps.filter(rfp => rfp.status === 'sent');
                this.populateRFPSelect();
            }
        } catch (error) {
            App.showToast('Error loading RFPs: ' + error.message, 'error');
        }
    }

    populateRFPSelect() {
        const select = document.getElementById('rfp-select');
        if (!select) return;

        if (this.rfps.length === 0) {
            select.innerHTML = '<option value="">No sent RFPs available</option>';
            return;
        }

        select.innerHTML = '<option value="">Choose an RFP...</option>' +
            this.rfps.map(rfp => `
                <option value="${rfp.id}">
                    ${rfp.title} - ${rfp.proposals_count} proposals - $${rfp.budget.toLocaleString()}
                </option>
            `).join('');
    }

    // Load proposals for selected RFP
    async loadProposals() {
        const rfpId = document.getElementById('rfp-select').value;
        
        if (!rfpId) {
            this.showEmptyState();
            return;
        }

        this.selectedRFP = this.rfps.find(rfp => rfp.id == rfpId);
        if (!this.selectedRFP) return;

        App.showLoading();

        try {
            const response = await App.API.get(`/api/rfp/${rfpId}/proposals`);
            
            if (response.success) {
                this.proposals = response.proposals;
                this.displayProposals();
            }
        } catch (error) {
            App.showToast('Error loading proposals: ' + error.message, 'error');
            this.showEmptyState();
        } finally {
            App.hideLoading();
        }
    }

    displayProposals() {
        document.getElementById('empty-state').classList.add('hidden');
        document.getElementById('proposals-content').classList.remove('hidden');

        if (this.proposals.length === 0) {
            this.showNoProposalsState();
            return;
        }

        // Show detailed proposals
        this.showDetailedProposals();
        
        // Show comparison table
        this.showComparisonTable();
    }

    showEmptyState() {
        document.getElementById('empty-state').classList.remove('hidden');
        document.getElementById('proposals-content').classList.add('hidden');
    }

    showNoProposalsState() {
        const detailedSection = document.getElementById('detailed-proposals');
        if (detailedSection) {
            detailedSection.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>No Proposals Received</h3>
                    <p>No vendors have responded to this RFP yet</p>
                    <button class="btn btn-outline" onclick="proposalsManager.checkEmails()">
                        <i class="fas fa-sync"></i> Check for New Emails
                    </button>
                </div>
            `;
        }

        // Hide other sections
        document.getElementById('proposals-comparison').classList.add('hidden');
        document.getElementById('ai-recommendation').classList.add('hidden');
    }

    showDetailedProposals() {
        const container = document.getElementById('proposals-grid');
        if (!container) return;

        container.innerHTML = this.proposals.map(proposal => this.createProposalCard(proposal)).join('');
    }

    createProposalCard(proposal) {
        const hasScore = proposal.ai_score !== null && proposal.ai_score !== undefined;
        
        return `
            <div class="proposal-card ${hasScore ? 'scored' : ''}">
                <div class="proposal-header">
                    <div class="vendor-info">
                        <h3>${proposal.vendor.name}</h3>
                        <p>${proposal.vendor.company || 'No company'}</p>
                    </div>
                    ${hasScore ? `
                        <div class="ai-score-badge">
                            <i class="fas fa-star"></i>
                            <span>${proposal.ai_score.toFixed(1)}</span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="proposal-pricing">
                    <div class="price-main">
                        <span class="price-label">Total Price</span>
                        <span class="price-value">$${App.formatCurrency(proposal.total_price).replace('$', '')}</span>
                    </div>
                    <div class="price-details">
                        ${proposal.parsed_data.items ? proposal.parsed_data.items.map(item => `
                            <div class="item-price">
                                <span>${item.name} x${item.quantity}</span>
                                <span>$${App.formatCurrency(item.total_price).replace('$', '')}</span>
                            </div>
                        `).join('') : ''}
                    </div>
                </div>
                
                <div class="proposal-details">
                    <div class="detail-item">
                        <i class="fas fa-truck"></i>
                        <span>Delivery: ${proposal.delivery_time || 'Not specified'}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-shield-alt"></i>
                        <span>Warranty: ${proposal.warranty || 'Not specified'}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-credit-card"></i>
                        <span>Payment: ${proposal.parsed_data.payment_terms || 'Not specified'}</span>
                    </div>
                </div>
                
                <div class="proposal-actions">
                    <button class="btn btn-sm btn-outline" onclick="proposalsManager.viewProposalDetails(${proposal.id})">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                    ${proposal.ai_notes ? `
                        <button class="btn btn-sm btn-primary" onclick="proposalsManager.viewAINotes(${proposal.id})">
                            <i class="fas fa-robot"></i> AI Analysis
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    showComparisonTable() {
        const tbody = document.getElementById('comparison-tbody');
        if (!tbody) return;

        tbody.innerHTML = this.proposals.map(proposal => this.createComparisonRow(proposal)).join('');

        document.getElementById('proposals-comparison').classList.remove('hidden');
    }

    createComparisonRow(proposal) {
        const hasScore = proposal.ai_score !== null && proposal.ai_score !== undefined;
        const budgetDiff = this.selectedRFP.budget ? proposal.total_price - this.selectedRFP.budget : 0;
        
        return `
            <tr>
                <td>
                    <div class="vendor-cell">
                        <strong>${proposal.vendor.name}</strong>
                        <small>${proposal.vendor.company || ''}</small>
                    </div>
                </td>
                <td>
                    <div class="price-cell">
                        <strong>$${App.formatCurrency(proposal.total_price).replace('$', '')}</strong>
                        <span class="price-diff">
                            ${this.selectedRFP.budget ? 
                                (budgetDiff <= 0 ? 
                                    `<span class="under-budget">Under budget</span>` : 
                                    `<span class="over-budget">$${App.formatCurrency(Math.abs(budgetDiff)).replace('$', '')} over</span>`) : 
                                ''}
                        </span>
                    </div>
                </td>
                <td>${proposal.delivery_time || 'Not specified'}</td>
                <td>${proposal.warranty || 'Not specified'}</td>
                <td>
                    ${hasScore ? 
                        `<div class="score-cell">
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${proposal.ai_score}%"></div>
                            </div>
                            <span>${proposal.ai_score.toFixed(1)}</span>
                        </div>` : 
                        '<span class="no-score">Not scored</span>'
                    }
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline" onclick="proposalsManager.viewProposalDetails(${proposal.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    // AI comparison functionality
    async compareProposals() {
        if (!this.selectedRFP || this.proposals.length === 0) {
            App.showToast('No proposals available for comparison', 'error');
            return;
        }

        App.showLoading();

        try {
            const response = await App.API.post('/api/proposal/compare', {
                rfp_id: this.selectedRFP.id
            });

            if (response.success) {
                this.comparisonData = response.comparison;
                this.displayAIRecommendation();
                App.showToast('AI comparison completed!', 'success');
                
                // Reload proposals to get updated scores
                this.loadProposals();
            }
        } catch (error) {
            App.showToast('Error comparing proposals: ' + error.message, 'error');
        } finally {
            App.hideLoading();
        }
    }

    displayAIRecommendation() {
        if (!this.comparisonData) return;

        const recommendation = this.comparisonData.recommendation;
        
        // Update recommendation card
        document.getElementById('confidence-score').textContent = `${(recommendation.confidence * 100).toFixed(0)}%`;
        document.getElementById('winner-name').textContent = recommendation.best_vendor_name;
        
        // Find winner proposal
        const winnerProposal = this.proposals.find(p => p.vendor.id === recommendation.best_vendor_id);
        if (winnerProposal) {
            document.getElementById('winner-company').textContent = winnerProposal.vendor.company || '';
            document.getElementById('winner-price').textContent = `$${App.formatCurrency(winnerProposal.total_price).replace('$', '')}`;
            document.getElementById('winner-delivery').textContent = winnerProposal.delivery_time || 'Not specified';
            document.getElementById('winner-score').textContent = winnerProposal.ai_score ? 
                `${winnerProposal.ai_score.toFixed(1)}/100` : 'Not scored';
        }
        
        document.getElementById('recommendation-reasoning').textContent = recommendation.reasoning;
        
        // Display key factors
        const factorsContainer = document.getElementById('key-factors-list');
        if (factorsContainer) {
            factorsContainer.innerHTML = recommendation.key_factors.map(factor => `
                <div class="factor-item">
                    <i class="fas fa-check-circle"></i>
                    <span>${factor}</span>
                </div>
            `).join('');
        }

        document.getElementById('ai-recommendation').classList.remove('hidden');
    }

    // View proposal details
    viewProposalDetails(proposalId) {
        const proposal = this.proposals.find(p => p.id === proposalId);
        if (!proposal) return;

        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('proposal-detail-content');
        
        modalTitle.textContent = `Proposal - ${proposal.vendor.name}`;
        
        modalContent.innerHTML = `
            <div class="proposal-detail">
                <div class="detail-section">
                    <h3>Vendor Information</h3>
                    <div class="vendor-details">
                        <p><strong>Name:</strong> ${proposal.vendor.name}</p>
                        <p><strong>Company:</strong> ${proposal.vendor.company || 'Not specified'}</p>
                        <p><strong>Email:</strong> ${proposal.vendor.email}</p>
                        <p><strong>Phone:</strong> ${proposal.vendor.phone || 'Not specified'}</p>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Pricing Details</h3>
                    <div class="pricing-details">
                        <p><strong>Total Price:</strong> $${App.formatCurrency(proposal.total_price).replace('$', '')}</p>
                        ${proposal.parsed_data.items ? `
                            <div class="items-breakdown">
                                <h4>Items Breakdown:</h4>
                                <table class="items-table">
                                    <thead>
                                        <tr>
                                            <th>Item</th>
                                            <th>Quantity</th>
                                            <th>Unit Price</th>
                                            <th>Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${proposal.parsed_data.items.map(item => `
                                            <tr>
                                                <td>${item.name}</td>
                                                <td>${item.quantity}</td>
                                                <td>$${App.formatCurrency(item.unit_price).replace('$', '')}</td>
                                                <td>$${App.formatCurrency(item.total_price).replace('$', '')}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Terms and Conditions</h3>
                    <div class="terms-details">
                        <p><strong>Delivery Time:</strong> ${proposal.delivery_time || 'Not specified'}</p>
                        <p><strong>Warranty:</strong> ${proposal.warranty || 'Not specified'}</p>
                        <p><strong>Payment Terms:</strong> ${proposal.parsed_data.payment_terms || 'Not specified'}</p>
                        ${proposal.parsed_data.special_notes ? `
                            <p><strong>Special Notes:</strong> ${proposal.parsed_data.special_notes}</p>
                        ` : ''}
                    </div>
                </div>
                
                ${proposal.ai_score ? `
                    <div class="detail-section">
                        <h3>AI Analysis</h3>
                        <div class="ai-analysis-details">
                            <p><strong>AI Score:</strong> ${proposal.ai_score.toFixed(1)}/100</p>
                            ${proposal.ai_notes ? `
                                <p><strong>AI Notes:</strong> ${proposal.ai_notes}</p>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                <div class="detail-section">
                    <h3>Original Email Content</h3>
                    <div class="email-content">
                        <pre>${proposal.original_email_content}</pre>
                    </div>
                </div>
            </div>
        `;

        App.openModal('proposal-modal');
    }

    viewAINotes(proposalId) {
        const proposal = this.proposals.find(p => p.id === proposalId);
        if (!proposal || !proposal.ai_notes) return;

        App.showToast(`AI Analysis: ${proposal.ai_notes}`, 'info', 5000);
    }

    closeProposalModal() {
        App.closeModal('proposal-modal');
    }

    // Check for new emails
    async checkEmails() {
        App.showLoading();
        
        try {
            const response = await App.API.post('/api/email/check');
            
            if (response.success) {
                App.showToast(`Processed ${response.processed_emails} new emails`, 'success');
                this.loadProposals();
            }
        } catch (error) {
            App.showToast('Error checking emails: ' + error.message, 'error');
        } finally {
            App.hideLoading();
        }
    }
}

// Initialize Proposals Manager
const proposalsManager = new ProposalsManager();

// Global functions for inline event handlers
window.compareProposals = function() {
    proposalsManager.compareProposals();
};

window.viewProposalDetails = function(proposalId) {
    proposalsManager.viewProposalDetails(proposalId);
};

window.viewAINotes = function(proposalId) {
    proposalsManager.viewAINotes(proposalId);
};

window.closeProposalModal = function() {
    proposalsManager.closeProposalModal();
};

window.checkEmails = function() {
    proposalsManager.checkEmails();
};

window.loadProposals = function() {
    proposalsManager.loadProposals();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    proposalsManager.init();
});
