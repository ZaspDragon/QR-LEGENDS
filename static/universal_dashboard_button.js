// Universal Dashboard Button - Enhanced Navigation
(function() {
    'use strict';

    // Check if current page is a dashboard to avoid duplicate buttons
    const currentPath = window.location.pathname;
    const isDashboard = currentPath.includes('dashboard') || currentPath === '/' || currentPath === '/index';

    if (isDashboard) {
        return; // Don't add button on dashboard pages
    }

    function addDashboardButton() {
        // Remove existing button if any
        const existingBtn = document.getElementById('universal-dashboard-btn');
        if (existingBtn) {
            existingBtn.remove();
        }

        // Create dashboard button
        const dashboardBtn = document.createElement('button');
        dashboardBtn.id = 'universal-dashboard-btn';
        dashboardBtn.innerHTML = '🏠';
        dashboardBtn.title = 'Go to Dashboard';

        // Enhanced styling
        dashboardBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
            transition: all 0.3s ease;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        `;

        // Hover effects
        dashboardBtn.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) translateY(-2px)';
            this.style.boxShadow = '0 12px 35px rgba(99, 102, 241, 0.6)';
        });

        dashboardBtn.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateY(0)';
            this.style.boxShadow = '0 8px 25px rgba(99, 102, 241, 0.4)';
        });

        // Click handler - smart routing
        dashboardBtn.addEventListener('click', async function() {
            try {
                // Try to determine user type from session
                const response = await fetch('/api/auth/profile', {
                    credentials: 'include'
                });

                if (response.ok) {
                    const profile = await response.json();

                    // Route based on user type and role
                    if (profile.user_type === 'employee' && profile.role === 'employee') {
                        window.location.href = '/employee_dashboard';
                    } else {
                        window.location.href = '/main_dashboard';
                    }
                } else {
                    // Default to main dashboard
                    window.location.href = '/main_dashboard';
                }
            } catch (error) {
                console.log('Using fallback navigation');
                window.location.href = '/main_dashboard';
            }
        });

        // Add to page
        document.body.appendChild(dashboardBtn);

        // Adjust body padding to prevent overlap
        adjustBodyPadding();

        console.log('Universal Dashboard Button added successfully');
    }

    function adjustBodyPadding() {
        if (!document.body.style.paddingBottom || 
            parseInt(document.body.style.paddingBottom) < 100) {
            document.body.style.paddingBottom = '100px';
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addDashboardButton);
    } else {
        addDashboardButton();
    }

    // Handle dynamic content changes
    window.addEventListener('resize', adjustBodyPadding);

    // Fallback check
    setInterval(function() {
        if (!document.getElementById('universal-dashboard-btn') && 
            !isDashboard && 
            document.body) {
            addDashboardButton();
        }
    }, 5000);

    // Load QR camera scanner if not already loaded
    if (typeof QRCameraScanner === 'undefined' && typeof window.QRCameraScanner === 'undefined') {
        const qrScript = document.createElement('script');
        qrScript.src = '/static/qr_camera_scanner.js';
        qrScript.onload = function() {
            console.log('✅ QR Camera Scanner loaded via universal button');
            // Initialize global functions after loading
            if (typeof window.openCameraScanner === 'undefined') {
                window.openCameraScanner = function(callback) {
                    if (window.QRCameraScanner) {
                        window.QRCameraScanner.openScanner(callback);
                    }
                };
            }
        };
        document.head.appendChild(qrScript);
    }

})();