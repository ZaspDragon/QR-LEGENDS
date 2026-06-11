// Widget Access Control System
// Defines which widgets are available based on user role and department

const WIDGET_CATALOG = {
    // Executive Widgets
    executive: {
        'financial-overview': {
            name: '💰 Financial Overview',
            description: 'Revenue, EBITDA, cash flow metrics',
            category: 'Executive',
            roles: ['admin', 'manager', 'accountant'],
            departments: ['finance', 'Administration', 'executive']
        },
        'company-performance': {
            name: '📈 Company Performance',
            description: 'KPIs across all departments',
            category: 'Executive',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'executive']
        },
        'regional-operations': {
            name: '🌎 Regional Operations',
            description: 'Multi-branch performance dashboard',
            category: 'Executive',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'executive', 'regional_management']
        },
        'executive-alerts': {
            name: '🚨 Executive Alerts',
            description: 'Critical business alerts and notifications',
            category: 'Executive',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'executive']
        }
    },

    // Warehouse Operations Widgets
    warehouse: {
        'order-picking-stats': {
            name: '📦 Picking Performance',
            description: 'Pick rates, accuracy, active orders',
            category: 'Warehouse',
            roles: ['admin', 'manager', 'worker'],
            departments: ['warehouse', 'order_picking', 'Administration']
        },
        'receiving-dashboard': {
            name: '📥 Receiving Status',
            description: 'Inbound shipments and dock status',
            category: 'Warehouse',
            roles: ['admin', 'manager', 'worker'],
            departments: ['warehouse', 'receiving', 'Administration']
        },
        'shipping-dashboard': {
            name: '📤 Shipping Queue',
            description: 'Outbound orders and carrier tracking',
            category: 'Warehouse',
            roles: ['admin', 'manager', 'worker'],
            departments: ['warehouse', 'shipping', 'Administration']
        },
        'lift-driver-assignments': {
            name: '🏗️ Lift Driver Tasks',
            description: 'Forklift assignments and priorities',
            category: 'Warehouse',
            roles: ['admin', 'manager', 'lift_driver'],
            departments: ['warehouse', 'inventory', 'Administration']
        },
        'inventory-alerts': {
            name: '📊 Inventory Alerts',
            description: 'Low stock, overstock, and cycle counts',
            category: 'Warehouse',
            roles: ['admin', 'manager', 'worker'],
            departments: ['warehouse', 'inventory', 'Administration']
        },
        'warehouse-productivity': {
            name: '⚡ Productivity Metrics',
            description: 'Worker efficiency and throughput',
            category: 'Warehouse',
            roles: ['admin', 'manager'],
            departments: ['warehouse', 'Administration']
        },
        'quality-control': {
            name: '✅ Quality Checks',
            description: 'QC tasks and defect tracking',
            category: 'Warehouse',
            roles: ['admin', 'manager', 'worker'],
            departments: ['warehouse', 'quality_control', 'Administration']
        }
    },

    // Sales & Customer Service Widgets
    sales: {
        'sales-pipeline': {
            name: '💼 Sales Pipeline',
            description: 'Quotes, orders, and conversion rates',
            category: 'Sales',
            roles: ['admin', 'manager', 'sales'],
            departments: ['sales', 'Administration']
        },
        'customer-orders': {
            name: '🛒 Customer Orders',
            description: 'Active orders and fulfillment status',
            category: 'Sales',
            roles: ['admin', 'manager', 'sales'],
            departments: ['sales', 'customer_service', 'Administration']
        },
        'customer-support': {
            name: '🎧 Support Tickets',
            description: 'Customer inquiries and issues',
            category: 'Sales',
            roles: ['admin', 'manager', 'sales'],
            departments: ['sales', 'customer_service', 'Administration']
        },
        'sales-performance': {
            name: '📊 Sales Metrics',
            description: 'Revenue, margins, top customers',
            category: 'Sales',
            roles: ['admin', 'manager', 'sales'],
            departments: ['sales', 'Administration']
        }
    },

    // Finance & Accounting Widgets
    finance: {
        'accounts-receivable': {
            name: '💵 Accounts Receivable',
            description: 'Outstanding invoices and aging',
            category: 'Finance',
            roles: ['admin', 'manager', 'accountant'],
            departments: ['finance', 'Administration']
        },
        'accounts-payable': {
            name: '💳 Accounts Payable',
            description: 'Vendor payments and due dates',
            category: 'Finance',
            roles: ['admin', 'manager', 'accountant'],
            departments: ['finance', 'Administration']
        },
        'cash-flow': {
            name: '💰 Cash Flow',
            description: 'Daily cash position and forecasts',
            category: 'Finance',
            roles: ['admin', 'manager', 'accountant'],
            departments: ['finance', 'Administration']
        },
        'expense-tracking': {
            name: '📝 Expense Tracking',
            description: 'Department budgets and spending',
            category: 'Finance',
            roles: ['admin', 'manager', 'accountant'],
            departments: ['finance', 'Administration']
        }
    },

    // Purchasing & Procurement Widgets
    purchasing: {
        'purchase-orders': {
            name: '📋 Purchase Orders',
            description: 'Active POs and delivery tracking',
            category: 'Purchasing',
            roles: ['admin', 'manager', 'worker'],
            departments: ['purchasing', 'Administration']
        },
        'supplier-performance': {
            name: '🏢 Supplier Metrics',
            description: 'Vendor OTIF and lead times',
            category: 'Purchasing',
            roles: ['admin', 'manager'],
            departments: ['purchasing', 'Administration']
        },
        'inventory-planning': {
            name: '📦 Replenishment',
            description: 'Reorder points and procurement needs',
            category: 'Purchasing',
            roles: ['admin', 'manager'],
            departments: ['purchasing', 'inventory', 'Administration']
        }
    },

    // Branch Management Widgets
    branch: {
        'branch-operations': {
            name: '🏪 Branch Dashboard',
            description: 'Branch-specific operations overview',
            category: 'Branch',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'branch_management']
        },
        'branch-team': {
            name: '👥 Team Management',
            description: 'Staff scheduling and performance',
            category: 'Branch',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'branch_management', 'hr']
        },
        'branch-inventory': {
            name: '📊 Branch Inventory',
            description: 'Location-specific stock levels',
            category: 'Branch',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'branch_management', 'inventory']
        },
        'branch-maintenance': {
            name: '🔧 Facility Maintenance',
            description: 'Equipment and building issues',
            category: 'Branch',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'branch_management', 'maintenance']
        }
    },

    // Regional Management Widgets
    regional: {
        'regional-dashboard': {
            name: '🌐 Regional Overview',
            description: 'Multi-location performance metrics',
            category: 'Regional',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'regional_management']
        },
        'regional-compliance': {
            name: '📜 Compliance Tracking',
            description: 'Regulatory and policy adherence',
            category: 'Regional',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'regional_management', 'compliance']
        },
        'regional-logistics': {
            name: '🚛 Regional Logistics',
            description: 'Inter-branch transfers and routing',
            category: 'Regional',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'regional_management', 'logistics']
        }
    },

    // HR & Payroll Widgets
    hr: {
        'employee-directory': {
            name: '👤 Employee Directory',
            description: 'Staff contacts and org chart',
            category: 'HR',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'hr']
        },
        'time-attendance': {
            name: '⏰ Time & Attendance',
            description: 'Clock in/out and schedule tracking',
            category: 'HR',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'hr']
        },
        'payroll-summary': {
            name: '💵 Payroll Overview',
            description: 'Payroll periods and processing',
            category: 'HR',
            roles: ['admin', 'manager'],
            departments: ['Administration', 'hr', 'finance']
        }
    },

    // General/Universal Widgets
    universal: {
        'recent-activity': {
            name: '📝 Recent Activity',
            description: 'Latest system actions and updates',
            category: 'Universal',
            roles: ['admin', 'manager', 'worker', 'sales', 'accountant', 'lift_driver'],
            departments: '*'
        },
        'my-tasks': {
            name: '✅ My Tasks',
            description: 'Personal task list and assignments',
            category: 'Universal',
            roles: ['admin', 'manager', 'worker', 'sales', 'accountant', 'lift_driver'],
            departments: '*'
        },
        'notifications': {
            name: '🔔 Notifications',
            description: 'Alerts and messages',
            category: 'Universal',
            roles: ['admin', 'manager', 'worker', 'sales', 'accountant', 'lift_driver'],
            departments: '*'
        },
        'quick-scan': {
            name: '📱 Quick QR Scan',
            description: 'Fast QR code scanner widget',
            category: 'Universal',
            roles: ['admin', 'manager', 'worker', 'sales', 'accountant', 'lift_driver'],
            departments: '*'
        }
    }
};

// Widget Access Control Functions
function getUserAccessLevel(userRole, userDepartment) {
    return {
        role: userRole,
        department: userDepartment,
        isAdmin: userRole === 'admin',
        isManager: userRole === 'manager',
        isWorker: userRole === 'worker',
        isSales: userRole === 'sales',
        isAccountant: userRole === 'accountant',
        isLiftDriver: userRole === 'lift_driver'
    };
}

function getAvailableWidgets(userRole, userDepartment) {
    const availableWidgets = [];
    
    // Iterate through all widget categories
    Object.keys(WIDGET_CATALOG).forEach(categoryKey => {
        const category = WIDGET_CATALOG[categoryKey];
        
        Object.keys(category).forEach(widgetKey => {
            const widget = category[widgetKey];
            
            // Check if user's role has access
            const hasRoleAccess = widget.roles.includes(userRole);
            
            // Check if user's department has access
            const hasDepartmentAccess = 
                widget.departments === '*' || 
                widget.departments.includes(userDepartment);
            
            // Special case: admins get access to everything
            const isAdmin = userRole === 'admin';
            
            // Special case: managers get access to their department widgets
            const isManagerWithDeptAccess = 
                userRole === 'manager' && hasDepartmentAccess;
            
            if (isAdmin || (hasRoleAccess && hasDepartmentAccess) || isManagerWithDeptAccess) {
                availableWidgets.push({
                    id: widgetKey,
                    ...widget,
                    categoryKey: categoryKey
                });
            }
        });
    });
    
    return availableWidgets;
}

function filterWidgetsByCategory(widgets, category) {
    if (!category || category === 'all') {
        return widgets;
    }
    return widgets.filter(w => w.categoryKey === category);
}

function canUserAccessWidget(widgetId, userRole, userDepartment) {
    const availableWidgets = getAvailableWidgets(userRole, userDepartment);
    return availableWidgets.some(w => w.id === widgetId);
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        WIDGET_CATALOG,
        getUserAccessLevel,
        getAvailableWidgets,
        filterWidgetsByCategory,
        canUserAccessWidget
    };
}

// Make available globally
window.WidgetAccessControl = {
    WIDGET_CATALOG,
    getUserAccessLevel,
    getAvailableWidgets,
    filterWidgetsByCategory,
    canUserAccessWidget
};
