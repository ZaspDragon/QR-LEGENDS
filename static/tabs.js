/**
 * QR Legends Tab Management System
 * Handles hierarchical sidebar tabs with main departments and mini sub-tabs
 */

class TabsController {
    constructor() {
        this.tabs = [];
        this.homepage = 'dashboard';
        this.expandedSections = new Set();
        this.init();
    }

    async init() {
        await this.loadTabs();
        this.renderSidebar();
        this.setupEventListeners();
        this.setActiveTab();
    }

    async loadTabs() {
        try {
            // Try to load from API
            const response = await fetch('/api/user/tabs');
            const data = await response.json();
            
            if (data.success && data.tabs && data.tabs.length > 0) {
                this.tabs = data.tabs;
                this.homepage = data.homepage || 'dashboard';
                
                // Initialize expanded sections
                this.tabs.forEach(tab => {
                    if (tab.expanded) {
                        this.expandedSections.add(tab.id);
                    }
                });
            } else {
                // API returned empty or unsuccessful - load defaults
                this.loadDefaultTabs();
            }
            
            // Sync to localStorage for fast load
            localStorage.setItem('ql_tabs', JSON.stringify(this.tabs));
            localStorage.setItem('ql_homepage', this.homepage);
        } catch (error) {
            console.error('Error loading tabs:', error);
            // Fallback to localStorage
            this.loadFromLocalStorage();
        }
    }

    loadFromLocalStorage() {
        const savedTabs = localStorage.getItem('ql_tabs');
        const savedHomepage = localStorage.getItem('ql_homepage');
        
        if (savedTabs) {
            this.tabs = JSON.parse(savedTabs);
        } else {
            // No data found - load defaults
            this.loadDefaultTabs();
        }
        if (savedHomepage) {
            this.homepage = savedHomepage;
        }
    }
    
    loadDefaultTabs() {
        // Default hierarchical tab structure
        this.tabs = [
            {
                id: 'dashboard',
                label: 'Dashboard',
                icon: '🏠',
                order: 0,
                type: 'main',
                route: '/main_dashboard'
            },
            {
                id: 'warehouse',
                label: 'Warehouse',
                icon: '📦',
                order: 1,
                type: 'main',
                expanded: false,
                children: [
                    {id: 'receiving', label: 'Receiving', icon: '📥', route: '/receiving'},
                    {id: 'putaway', label: 'Put Away', icon: '🧱', route: '/putaway'},
                    {id: 'picking', label: 'Picking', icon: '🛒', route: '/picking'},
                    {id: 'packing', label: 'Packing', icon: '📦', route: '/packing'},
                    {id: 'shipping', label: 'Shipping', icon: '🚚', route: '/shipping'},
                    {id: 'transfers', label: 'Transfers', icon: '🔄', route: '/transfers'},
                    {id: 'problem_solving', label: 'Problem Solve', icon: '🔧', route: '/problem_solving'}
                ]
            },
            {
                id: 'inventory',
                label: 'Inventory',
                icon: '📊',
                order: 2,
                type: 'main',
                route: '/inventory',
                expanded: false,
                children: [
                    {id: 'inventory_view', label: 'View Items', icon: '📋', route: '/inventory'},
                    {id: 'cycle_count', label: 'Cycle Count', icon: '🔢', route: '/cycle_count'}
                ]
            },
            {
                id: 'erp',
                label: 'ERP',
                icon: '🏢',
                order: 3,
                type: 'main',
                route: '/erp_dashboard',
                expanded: false,
                children: [
                    {id: 'erp_dashboard', label: 'ERP Dashboard', icon: '📊', route: '/erp_dashboard'},
                    {id: 'finance', label: 'Finance', icon: '💰', route: '/finance'},
                    {id: 'hr', label: 'HR & Payroll', icon: '👥', route: '/hr_payroll'}
                ]
            },
            {
                id: 'reports',
                label: 'Reports',
                icon: '📈',
                order: 4,
                type: 'main',
                route: '/reports',
                expanded: false,
                children: [
                    {id: 'reports_hub', label: 'Reports Hub', icon: '📊', route: '/reports_hub'},
                    {id: 'custom_reports', label: 'Custom Reports', icon: '📋', route: '/custom_reports'},
                    {id: 'analytics', label: 'Analytics', icon: '📉', route: '/analytics_dashboard'}
                ]
            },
            {
                id: 'admin',
                label: 'Admin',
                icon: '⚙️',
                order: 5,
                type: 'main',
                expanded: false,
                children: [
                    {id: 'users', label: 'Users', icon: '👥', route: '/user_management'},
                    {id: 'settings', label: 'Settings', icon: '🔧', route: '/settings'},
                    {id: 'widgets', label: 'Widgets', icon: '🧩', route: '/widget_customization'}
                ]
            }
        ];
        this.homepage = 'dashboard';
    }

    async saveTabs() {
        try {
            const response = await fetch('/api/user/tabs', {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    tabs: this.tabs,
                    homepage: this.homepage
                })
            });
            
            const data = await response.json();
            if (data.success) {
                // Update localStorage
                localStorage.setItem('ql_tabs', JSON.stringify(this.tabs));
                localStorage.setItem('ql_homepage', this.homepage);
                return true;
            }
        } catch (error) {
            console.error('Error saving tabs:', error);
        }
        return false;
    }

    renderSidebar() {
        const sidebar = document.getElementById('qlSidebar');
        if (!sidebar) return;

        const tabsHTML = this.tabs.map(tab => {
            if (tab.type === 'main' && tab.children && tab.children.length > 0) {
                // Main tab with sub-tabs
                const isExpanded = this.expandedSections.has(tab.id);
                const childrenHTML = isExpanded ? 
                    tab.children.map(child => this.renderMiniTab(child, tab.id)).join('') : '';
                
                return `
                    <div class="sidebar-section" data-section="${tab.id}">
                        <div class="sidebar-main-tab ${this.isActive(tab) ? 'active' : ''}" 
                             data-tab-id="${tab.id}"
                             onclick="tabsController.toggleSection('${tab.id}')">
                            <span class="tab-icon">${tab.icon}</span>
                            <span class="tab-label">${tab.label}</span>
                            <span class="expand-icon">${isExpanded ? '▼' : '▶'}</span>
                        </div>
                        <div class="sidebar-mini-tabs ${isExpanded ? 'expanded' : ''}">
                            ${childrenHTML}
                        </div>
                    </div>
                `;
            } else {
                // Standalone main tab
                return `
                    <div class="sidebar-section">
                        <a href="${tab.route || '#'}" 
                           class="sidebar-main-tab ${this.isActive(tab) ? 'active' : ''}"
                           data-tab-id="${tab.id}">
                            <span class="tab-icon">${tab.icon}</span>
                            <span class="tab-label">${tab.label}</span>
                        </a>
                    </div>
                `;
            }
        }).join('');

        sidebar.innerHTML = `
            <div class="sidebar-header">
                <div class="sidebar-logo">
                    <span class="logo-icon">🟦</span>
                    <span class="logo-text">QR LEGENDS</span>
                </div>
                <button class="sidebar-collapse-btn" onclick="tabsController.toggleSidebar()" title="Collapse sidebar">
                    <span>◀</span>
                </button>
            </div>
            <div class="sidebar-tabs">
                ${tabsHTML}
            </div>
            <div class="sidebar-footer">
                <button class="sidebar-btn" onclick="tabsController.openAddTabModal()" title="Add new tab">
                    <span>➕</span>
                    <span>Add Tab</span>
                </button>
                <button class="sidebar-btn" onclick="tabsController.setHomepage()" title="Set current as homepage">
                    <span>🏠</span>
                    <span>Set Homepage</span>
                </button>
            </div>
        `;
    }

    renderMiniTab(child, parentId) {
        return `
            <a href="${child.route || '#'}" 
               class="sidebar-mini-tab ${this.isActive(child) ? 'active' : ''}"
               data-tab-id="${child.id}"
               data-parent="${parentId}">
                <span class="mini-tab-icon">${child.icon}</span>
                <span class="mini-tab-label">${child.label}</span>
            </a>
        `;
    }

    isActive(tab) {
        const currentPath = window.location.pathname;
        if (tab.route && currentPath === tab.route) return true;
        
        // Check children
        if (tab.children) {
            return tab.children.some(child => child.route === currentPath);
        }
        
        return false;
    }

    toggleSection(sectionId) {
        // Only toggle expanded state - no navigation
        if (this.expandedSections.has(sectionId)) {
            this.expandedSections.delete(sectionId);
        } else {
            this.expandedSections.add(sectionId);
        }
        
        // Update tab expanded state
        const tab = this.tabs.find(t => t.id === sectionId);
        if (tab) {
            tab.expanded = this.expandedSections.has(sectionId);
        }
        
        this.renderSidebar();
        this.saveTabs();
    }

    toggleSidebar() {
        const sidebar = document.getElementById('qlSidebar');
        const mainContent = document.getElementById('qlMainContent');
        
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('sidebar-collapsed');
        
        localStorage.setItem('ql_sidebar_collapsed', sidebar.classList.contains('collapsed'));
    }

    setActiveTab() {
        const currentPath = window.location.pathname;
        
        // Find and expand parent sections for current route
        this.tabs.forEach(tab => {
            if (tab.children) {
                const hasActiveChild = tab.children.some(child => child.route === currentPath);
                if (hasActiveChild) {
                    this.expandedSections.add(tab.id);
                    tab.expanded = true;
                }
            }
        });
        
        this.renderSidebar();
    }

    async setHomepage() {
        const currentPath = window.location.pathname;
        let newHomepage = 'dashboard';
        
        // Find current tab
        for (const tab of this.tabs) {
            if (tab.route === currentPath) {
                newHomepage = tab.id;
                break;
            }
            if (tab.children) {
                const child = tab.children.find(c => c.route === currentPath);
                if (child) {
                    newHomepage = child.id;
                    break;
                }
            }
        }
        
        this.homepage = newHomepage;
        
        // Update homepage flag
        this.tabs.forEach(tab => {
            tab.is_homepage = (tab.id === newHomepage);
            if (tab.children) {
                tab.children.forEach(child => {
                    child.is_homepage = (child.id === newHomepage);
                });
            }
        });
        
        await this.saveTabs();
        
        alert(`✅ Homepage set to: ${currentPath}\n\nThis page will now load when you open the dashboard.`);
    }

    openAddTabModal() {
        const modal = document.getElementById('addTabModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    closeAddTabModal() {
        const modal = document.getElementById('addTabModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    setupEventListeners() {
        // Close modal on outside click
        const modal = document.getElementById('addTabModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeAddTabModal();
                }
            });
        }
        
        // Restore sidebar state
        const collapsed = localStorage.getItem('ql_sidebar_collapsed') === 'true';
        if (collapsed) {
            document.getElementById('qlSidebar')?.classList.add('collapsed');
            document.getElementById('qlMainContent')?.classList.add('sidebar-collapsed');
        }
    }

    async addCustomTab() {
        const label = document.getElementById('newTabLabel').value;
        const icon = document.getElementById('newTabIcon').value;
        const route = document.getElementById('newTabRoute').value;
        const parent = document.getElementById('newTabParent').value;
        
        if (!label || !route) {
            alert('Please fill in tab label and route');
            return;
        }
        
        const newTab = {
            id: label.toLowerCase().replace(/\s+/g, '_'),
            label: label,
            icon: icon || '📄',
            route: route
        };
        
        if (parent && parent !== 'none') {
            // Add as mini-tab under parent
            const parentTab = this.tabs.find(t => t.id === parent);
            if (parentTab) {
                if (!parentTab.children) {
                    parentTab.children = [];
                }
                parentTab.children.push(newTab);
            }
        } else {
            // Add as main tab
            newTab.type = 'main';
            newTab.order = this.tabs.length;
            this.tabs.push(newTab);
        }
        
        await this.saveTabs();
        this.renderSidebar();
        this.closeAddTabModal();
        
        // Clear form
        document.getElementById('newTabLabel').value = '';
        document.getElementById('newTabIcon').value = '';
        document.getElementById('newTabRoute').value = '';
        document.getElementById('newTabParent').value = 'none';
    }
}

// Initialize global controller
let tabsController;
document.addEventListener('DOMContentLoaded', () => {
    tabsController = new TabsController();
});
