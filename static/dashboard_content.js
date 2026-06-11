import React, {useState, useMemo} from 'react';

function Content({ current}) {const [role, setRole] = useState("All")
  
  const roleKPIs = useMemo(() => {
    const map = {
      All: [
        { label: "Revenue", value: "$1.61M", sub: "+4.1% MoM", color: "#16a34a"},
        { label: "Gross Margin", value: "28.4%", sub: "+0.6pp", color: "#3b82f6"},
        { label: "Orders Today", value: "825", sub: "742 on-time", color: "#f59e0b"},
        { label: "Fill Rate", value: "97.2%", sub: "Across branches", color: "#8b5cf6"}
      ],
      Executive: [
        { label: "Revenue", value: "$1.61M", sub: "+4.1% MoM", color: "#16a34a"},
        { label: "EBITDA", value: "$224k", sub: "+2.3% MoM", color: "#3b82f6"},
        { label: "DSO", value: "32.6", sub: "days", color: "#f59e0b"},
        { label: "Inventory Turns", value: "7.8", sub: "+0.3", color: "#8b5cf6"}
      ],
      Sales: [
        { label: "Open Quotes", value: "112", sub: "avg age 3.1d", color: "#16a34a"},
        { label: "Win Rate", value: "41%", sub: "+3pp", color: "#3b82f6"},
        { label: "Bookings", value: "$402k", sub: "MTD", color: "#f59e0b"},
        { label: "Top Account", value: "Chadwell", sub: "$92k MTD", color: "#8b5cf6"}
      ],
      Warehouse: [
        { label: "Pick Rate", value: "142/hr", sub: "+8%", color: "#16a34a"},
        { label: "Pick Accuracy", value: "99.7%", sub: "+0.3%", color: "#3b82f6"},
        { label: "Active Workers", value: "23", sub: "2 on break", color: "#f59e0b"},
        { label: "Orders Shipped", value: "1,247", sub: "Today", color: "#8b5cf6"}
      ],
      Purchasing: [
        { label: "POs Due", value: "38", sub: "5 past due", color: "#ef4444"},
        { label: "Lead Time", value: "12.4d", sub: "avg", color: "#3b82f6"},
        { label: "Vendor OTIF", value: "93%", sub: "+2pp", color: "#16a34a"},
        { label: "Backorders", value: "61", sub: "priority", color: "#f59e0b"}
      ]};
    return map[role] || map["All"];
  }, [role]);

  const renderKPICards = () => {return roleKPIs.map((kpi, index) => (
      <div key={index} className="kpi-card" style={{
        background: 'white',
        border: '1px solid #e4e4e7',
        borderRadius: '16px',
        padding: '16px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'}}>
        <div style={{
          fontSize: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: '#71717a',
          marginBottom: '8px'}}>
          {kpi.label}
        </div>
        <div style={{
          fontSize: '24px',
          fontWeight: '600',
          color: '#18181b',
          marginBottom: '4px'}}>
          {kpi.value}
        </div>
        <div style={{
          fontSize: '12px',
          color: kpi.color || '#71717a'}}>
          {kpi.sub}
        </div>
      </div>
    ));
  };

  const renderRoleSwitcher = () => {const roles = ['All', 'Executive', 'Sales', 'Warehouse', 'Purchasing']
    
    return (
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px'}}>
        {roles.map(roleOption => (
          <button
            key={roleOption}
            onClick={() => setRole(roleOption)}
            style={{
              padding: '4px 12px',
              borderRadius: '20px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '12px',
              transition: 'all 0.2s',
              background: role === roleOption ? '#18181b' : '#f4f4f5',
              color: role === roleOption ? 'white' : '#374151'}}
          >
            {roleOption}
          </button>
        ))}
      </div>
    );
  };

  const renderQuickActions = () => {
    const actions = {
      All: [
        { title: "🏠 Main Dashboard", link: "/main_dashboard"},
        { title: "📊 Analytics", link: "/analytics_dashboard"},
        { title: "📦 Inventory", link: "/inventory_hub"},
        { title: "📋 Reports", link: "/reports_hub"}
      ],
      Executive: [
        { title: "💰 Financial Reports", link: "/financial_reports"},
        { title: "📈 ERP Analytics", link: "/erp_analytics"},
        { title: "👥 Company Management", link: "/company_employee_management"},
        { title: "⚙️ System Config", link: "/system_config"}
      ],
      Sales: [
        { title: "🛒 Order Management", link: "/order_management"},
        { title: "👤 Customer Portal", link: "/customer_portal"},
        { title: "💼 ERP CRM", link: "/erp_crm"},
        { title: "📊 Sales Analytics", link: "/erp_sales"}
      ],
      Warehouse: [
        { title: "📥 Receiving", link: "/receiving"},
        { title: "📤 Shipping", link: "/shipping"},
        { title: "🔍 Order Picking", link: "/order_picking"},
        { title: "📦 Putaway", link: "/putaway"}
      ],
      Purchasing: [
        { title: "🛒 ERP Purchasing", link: "/erp_purchasing"},
        { title: "🏢 Suppliers", link: "/erp_suppliers"},
        { title: "📊 Supplier Performance", link: "/erp_supplier_performance"},
        { title: "💰 Accounts Payable", link: "/accounts_payable"}
      ]};

    const currentActions = actions[role] || actions['All'];

    return (
      <div style={{
        background: 'white',
        border: '1px solid #e4e4e7',
        borderRadius: '16px',
        padding: '20px',
        marginTop: '20px'}}>
        <h3 style={{ marginBottom: '15px', color: '#18181b'}}>Quick Actions</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px'}}>
          {currentActions.map((action, index) => (
            <a
              key={index}
              href={action.link}
              style={{
                display: 'block',
                padding: '12px',
                background: '#f8fafc',
                borderRadius: '8px',
                textDecoration: 'none',
                color: '#374151',
                border: '1px solid #e2e8f0',
                transition: 'all 0.2s'}}
              onMouseOver={(e) => {
                e.target.style.background = '#e2e8f0'
                e.target.style.transform = 'translateY(-1px)'}}
              onMouseOut={(e) => {
                e.target.style.background = '#f8fafc'
                e.target.style.transform = 'translateY(0)'}}
            >
              {action.title}
            </a>
          ))}
        </div>
      </div>
    );
  };

  if (current !== "dashboard") {
    return (
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto'}}>
        <h2 style={{ marginBottom: '20px', color: '#18181b'}}>
          {current.charAt(0).toUpperCase() + current.slice(1)} Dashboard
        </h2>
        
        {renderRoleSwitcher()}
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          marginBottom: '20px'}}>
          {renderKPICards()}
        </div>

        {renderQuickActions()}
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto'}}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'}}>
        <h1 style={{ color: '#18181b', fontSize: '28px', fontWeight: '600'}}>
          QR Legends Dashboard
        </h1>
        <div style={{ fontSize: '14px', color: '#71717a'}}>
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'});}
        </div>
      </div>

      {renderRoleSwitcher()}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        marginBottom: '20px'}}>
        {renderKPICards()}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '20px',
        marginBottom: '20px'}}>
        <div style={{
          background: 'white',
          border: '1px solid #e4e4e7',
          borderRadius: '16px',
          padding: '20px'}}>
          <h3 style={{ marginBottom: '15px', color: '#18181b'}}>Revenue Trend</h3>
          <div style={{
            height: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#f8fafc',
            borderRadius: '8px',
            color: '#71717a'}}>
            Chart placeholder - Revenue over time
          </div>
        </div>

        <div style={{
          background: 'white',
          border: '1px solid #e4e4e7',
          borderRadius: '16px',
          padding: '20px'}}>
          <h3 style={{ marginBottom: '15px', color: '#18181b'}}>Order Health</h3>
          <div style={{
            height: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#f8fafc',
            borderRadius: '8px',
            color: '#71717a'}}>
            Chart placeholder - Order status breakdown
          </div>
        </div>
      </div>

      {renderQuickActions()}
    </div>
  );
}

export default Content;


// QR Legends Dashboard Content Management
(function() {'use strict'

    // Initialize dashboard when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeDashboard();
        setupEventListeners();
        loadDashboardData();});

    function initializeDashboard() {console.log('Customizable Dashboard initialized')

        // Set default active section
        showSection('overview');

        // Initialize any widgets
        initializeWidgets();}

    function setupEventListeners() {// Add click handlers for dashboard buttons
        const dashboardButtons = document.querySelectorAll('.dashboard-button, .btn')
        dashboardButtons.forEach(button => {
            if (!button.onclick) {
                button.addEventListener('click', handleButtonClick);}
        });

        // Add form submission handlers
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {form.addEventListener('submit', handleFormSubmit)});
    }

    function handleButtonClick(event) {const button = event.target
        const action = button.getAttribute('data-action') || button.getAttribute('onclick');

        if (action) {
            try {
                // Try to execute the action if it's a function
                if (typeof window[action] === 'function') {
                    window[action]();}
            } catch (error) {console.warn('Button action failed:', action, error)}
        }
    }

    function handleFormSubmit(event) {const form = event.target
        const action = form.action;

        // Basic form validation
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#dc2626';} else {field.style.borderColor = '#d1d5db'}
        });

        if (!isValid) {event.preventDefault()
            alert('Please fill in all required fields.');}
    }

    function showSection(sectionName) {// Hide all sections
        const sections = document.querySelectorAll('.dashboard-section, .tab-content')
        sections.forEach(section => {
            section.style.display = 'none'
            section.classList.remove('active');});

        // Show target section
        const targetSection = document.getElementById(sectionName + 'Section') || 
                             document.getElementById(sectionName + 'Tab') ||
                             document.getElementById(sectionName);

        if (targetSection) {targetSection.style.display = 'block'
            targetSection.classList.add('active');}

        // Update navigation
        updateNavigation(sectionName);
    }

    function updateNavigation(activeSectionName) {const navItems = document.querySelectorAll('.nav-item, .tab-button')
        navItems.forEach(item => {
            item.classList.remove('active');

            // Check if this nav item corresponds to the active section
            const itemTarget = item.getAttribute('data-target') || 
                              item.getAttribute('onclick')?.match(/switchTab\('(.+)'\)/)?.[1] ||
                              item.getAttribute('onclick')?.match(/showSection\('(.+)'\)/)?.[1];

            if (itemTarget === activeSectionName) {
                item.classList.add('active');}
        });
    }

    function initializeWidgets() {// Initialize any dashboard widgets
        const widgets = document.querySelectorAll('.widget, .metric-card')
        widgets.forEach(widget => {
            // Add loading animation
            widget.style.opacity = '0'
            widget.style.transform = 'translateY(20px)';

            setTimeout(() => {
                widget.style.transition = 'all 0.3s ease';
                widget.style.opacity = '1';
                widget.style.transform = 'translateY(0)';}, Math.random() * 500);
        });
    }

    function loadDashboardData() {// Simulate loading dashboard data
        setTimeout(() => {
            updateMetrics()
            updateCharts();}, 1000);
    }

    function updateMetrics() {// Update metric cards with sample data
        const metricCards = document.querySelectorAll('.metric-card')
        metricCards.forEach(card => {
            const valueElement = card.querySelector('.metric-value');
            if (valueElement && valueElement.textContent === '0') {
                // Animate counter
                animateCounter(valueElement, Math.floor(Math.random() * 1000));}
        });
    }

    function animateCounter(element, targetValue) {let currentValue = 0
        const increment = targetValue / 50;
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);}
            element.textContent = Math.floor(currentValue);
        }, 20);
    }

    function updateCharts() {// Placeholder for chart updates
        console.log('Charts updated')}

    // Expose global functions for inline event handlers
    window.showSection = showSection;
    window.switchTab = showSection; // Alias for compatibility

    // Additional utility functions
    window.refreshDashboard = function() {loadDashboardData()};

    window.toggleWidget = function(widgetId) {const widget = document.getElementById(widgetId)
        if (widget) {
            widget.style.display = widget.style.display === 'none' ? 'block' : 'none';}
    };

})();

// Global function definitions for common dashboard actions
function generatePOQR() {alert('Purchase Order QR generation feature coming soon!')}

function submitToERP() {alert('ERP submission feature coming soon!')}

function printPO() {window.print()}

function generateBulkLocationQRs() {alert('Bulk QR generation feature coming soon!')}

function closeTosModal() {const modal = document.getElementById('tosModal')
    if (modal) {
        modal.style.display = 'none';}
}

function showTosModal() {const modal = document.getElementById('tosModal')
    if (modal) {
        modal.style.display = 'block';}
}