/**
 * Hunter Pro CRM - Main JavaScript
 * Modern, responsive UI interactions
 */

// Global API configuration
const API_BASE = window.location.origin + '/api';

// Utility functions
const utils = {
    // Fetch wrapper with error handling
    async fetchAPI(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            this.showNotification('حدث خطأ في الاتصال بالخادم', 'error');
            throw error;
        }
    },
    
    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            backgroundColor: colors[type] || colors.info,
            color: 'white',
            borderRadius: '0.5rem',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
            zIndex: '9999',
            animation: 'slideIn 0.3s ease'
        });
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },
    
    // Format currency
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('ar-EG', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Format date
    formatDate(date, format = 'short') {
        const d = new Date(date);
        return new Intl.DateTimeFormat('ar-EG', {
            dateStyle: format
        }).format(d);
    },
    
    // Debounce function
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
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Customer management
const customerManager = {
    async list(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await utils.fetchAPI(`/customers?${query}`);
    },
    
    async get(id) {
        return await utils.fetchAPI(`/customers/${id}`);
    },
    
    async create(data) {
        return await utils.fetchAPI('/customers', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async update(id, data) {
        return await utils.fetchAPI(`/customers/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },
    
    async delete(id) {
        return await utils.fetchAPI(`/customers/${id}`, {
            method: 'DELETE'
        });
    },
    
    async getSentiment(id, days = 30) {
        return await utils.fetchAPI(`/customers/${id}/sentiment?days=${days}`);
    },
    
    async getInsights(id) {
        return await utils.fetchAPI(`/customers/${id}/insights`);
    }
};

// Deal management
const dealManager = {
    async create(data) {
        return await utils.fetchAPI('/deals', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async updateStage(id, stage, probability) {
        const params = new URLSearchParams({ stage });
        if (probability !== undefined) {
            params.append('probability', probability);
        }
        return await utils.fetchAPI(`/deals/${id}/stage?${params}`, {
            method: 'PATCH'
        });
    },
    
    async getPipelineStats() {
        return await utils.fetchAPI('/deals/pipeline/stats');
    },
    
    async getInsights(id) {
        return await utils.fetchAPI(`/deals/${id}/insights`);
    }
};

// AI service
const aiService = {
    async generate(prompt, options = {}) {
        return await utils.fetchAPI('/ai/generate', {
            method: 'POST',
            body: JSON.stringify({
                prompt,
                provider: options.provider,
                temperature: options.temperature || 0.7,
                max_tokens: options.max_tokens || 1000,
                system_prompt: options.system_prompt
            })
        });
    },
    
    async analyzeSentiment(text) {
        return await utils.fetchAPI('/ai/sentiment', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
    },
    
    async extractIntent(text) {
        return await utils.fetchAPI('/ai/intent', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
    },
    
    async generateResponse(customerMessage, context, tone = 'professional') {
        return await utils.fetchAPI('/ai/generate-response', {
            method: 'POST',
            body: JSON.stringify({
                customer_message: customerMessage,
                context,
                tone
            })
        });
    },
    
    async listProviders() {
        return await utils.fetchAPI('/ai/providers');
    }
};

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuButton = document.createElement('button');
    mobileMenuButton.className = 'mobile-menu-btn';
    mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
    mobileMenuButton.style.cssText = `
        display: none;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1000;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.75rem;
        color: var(--text-primary);
        cursor: pointer;
        font-size: 1.25rem;
    `;
    
    mobileMenuButton.addEventListener('click', () => {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('active');
    });
    
    document.body.appendChild(mobileMenuButton);
    
    // Show on mobile
    if (window.innerWidth <= 768) {
        mobileMenuButton.style.display = 'block';
    }
    
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 768) {
            mobileMenuButton.style.display = 'block';
        } else {
            mobileMenuButton.style.display = 'none';
            document.querySelector('.sidebar')?.classList.remove('active');
        }
    });
});

// Export to global scope
window.HunterPro = {
    utils,
    customerManager,
    dealManager,
    aiService
};

console.log('🚀 Hunter Pro CRM initialized');
console.log('📦 Available: HunterPro.utils, HunterPro.customerManager, HunterPro.dealManager, HunterPro.aiService');
