// QR Legends Responsive Design System
// Automatically detects device type and applies appropriate styles

(function() {
    'use strict';

    // Device detection
    const deviceDetection = {
        isMobile: function() {
            return window.innerWidth < 768;
        },
        isTablet: function() {
            return window.innerWidth >= 768 && window.innerWidth < 1024;
        },
        isDesktop: function() {
            return window.innerWidth >= 1024;
        },
        isTouchDevice: function() {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        },
        getDeviceType: function() {
            if (this.isMobile()) return 'mobile';
            if (this.isTablet()) return 'tablet';
            return 'desktop';
        }
    };

    // Apply device-specific classes
    function applyDeviceClasses() {
        const deviceType = deviceDetection.getDeviceType();
        const isTouchDevice = deviceDetection.isTouchDevice();
        
        // Remove old classes
        document.body.classList.remove('device-mobile', 'device-tablet', 'device-desktop', 'touch-device', 'no-touch');
        
        // Add new classes
        document.body.classList.add(`device-${deviceType}`);
        document.body.classList.add(isTouchDevice ? 'touch-device' : 'no-touch');
        
        // Set data attributes for CSS targeting
        document.body.setAttribute('data-device', deviceType);
        document.body.setAttribute('data-touch', isTouchDevice);
        
        // Store in global object
        window.QRLegends = window.QRLegends || {};
        window.QRLegends.device = {
            type: deviceType,
            isMobile: deviceDetection.isMobile(),
            isTablet: deviceDetection.isTablet(),
            isDesktop: deviceDetection.isDesktop(),
            isTouch: isTouchDevice,
            width: window.innerWidth,
            height: window.innerHeight
        };
    }

    // Inject responsive CSS
    const responsiveStyles = document.createElement('style');
    responsiveStyles.innerHTML = `
        /* ============================================
           QR LEGENDS RESPONSIVE DESIGN SYSTEM
           Auto-adjusts for Mobile, Tablet, Desktop
        ============================================ */

        /* Ensure proper viewport behavior */
        html {
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }

        /* Base responsive containers */
        .ql-container,
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* ============================================
           MOBILE (< 768px)
        ============================================ */
        @media (max-width: 767px) {
            body.device-mobile {
                font-size: 14px;
                line-height: 1.5;
            }

            .ql-container,
            .container {
                padding: 0 12px;
            }

            /* Mobile navigation */
            .ql-nav {
                display: none !important;
            }

            .mobile-nav-toggle {
                display: block !important;
            }

            /* Stack cards vertically */
            .widgets-grid,
            .ql-grid,
            .grid {
                display: block !important;
                grid-template-columns: 1fr !important;
            }

            .widget-card,
            .ql-card,
            .card {
                margin-bottom: 16px !important;
                padding: 16px !important;
            }

            /* Larger touch targets */
            button,
            .btn,
            .ql-btn,
            a.btn,
            input[type="button"],
            input[type="submit"] {
                min-height: 44px !important;
                min-width: 44px !important;
                padding: 12px 16px !important;
                font-size: 14px !important;
            }

            /* Mobile-friendly inputs */
            input,
            textarea,
            select {
                font-size: 16px !important; /* Prevents zoom on iOS */
                padding: 12px !important;
                min-height: 44px !important;
            }

            /* Responsive tables */
            table {
                display: block;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }

            /* Mobile headers */
            h1, .dashboard-title {
                font-size: 1.75rem !important;
            }

            h2 {
                font-size: 1.25rem !important;
            }

            h3 {
                font-size: 1.1rem !important;
            }

            /* Hide desktop-only elements */
            .desktop-only {
                display: none !important;
            }

            /* Show mobile-only elements */
            .mobile-only {
                display: block !important;
            }

            /* Responsive navigation */
            .ql-header-inner {
                flex-wrap: wrap;
                padding: 12px 16px !important;
            }

            /* Full-width buttons on mobile */
            .quick-actions {
                display: grid !important;
                grid-template-columns: 1fr !important;
                gap: 8px !important;
            }

            .quick-action-btn {
                width: 100% !important;
                text-align: center;
            }
        }

        /* ============================================
           TABLET (768px - 1023px)
        ============================================ */
        @media (min-width: 768px) and (max-width: 1023px) {
            body.device-tablet {
                font-size: 15px;
            }

            .ql-container,
            .container {
                padding: 0 16px;
            }

            /* 2-column grid for tablets */
            .widgets-grid,
            .ql-grid {
                grid-template-columns: repeat(2, 1fr) !important;
            }

            .widget-card,
            .ql-card,
            .card {
                padding: 20px !important;
            }

            /* Touch-friendly buttons */
            button,
            .btn,
            .ql-btn {
                min-height: 42px;
                padding: 10px 16px;
            }

            /* 2-column quick actions */
            .quick-actions {
                grid-template-columns: repeat(2, 1fr) !important;
            }
        }

        /* ============================================
           DESKTOP (>= 1024px)
        ============================================ */
        @media (min-width: 1024px) {
            body.device-desktop {
                font-size: 16px;
            }

            /* Hide mobile-only elements */
            .mobile-only {
                display: none !important;
            }

            /* Show desktop-only elements */
            .desktop-only {
                display: block !important;
            }

            /* Desktop navigation visible */
            .ql-nav {
                display: flex !important;
            }

            .mobile-nav-toggle {
                display: none !important;
            }

            /* Optimal grid layouts */
            .widgets-grid {
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)) !important;
            }
        }

        /* ============================================
           TOUCH DEVICE SPECIFIC
        ============================================ */
        body.touch-device {
            /* Remove hover effects on touch devices */
            -webkit-tap-highlight-color: rgba(59, 130, 246, 0.2);
        }

        body.touch-device button:hover,
        body.touch-device .btn:hover,
        body.touch-device .ql-btn:hover {
            transform: none !important; /* Disable hover transforms */
        }

        /* Active state for touch */
        body.touch-device button:active,
        body.touch-device .btn:active,
        body.touch-device .ql-btn:active {
            transform: scale(0.98);
            opacity: 0.9;
        }

        /* Larger widget delete buttons on touch */
        body.touch-device .widget-remove {
            width: 36px !important;
            height: 36px !important;
            font-size: 20px !important;
        }

        /* ============================================
           RESPONSIVE UTILITIES
        ============================================ */

        /* Responsive spacing */
        @media (max-width: 767px) {
            .responsive-spacing {
                margin: 8px 0 !important;
                padding: 8px !important;
            }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
            .responsive-spacing {
                margin: 12px 0 !important;
                padding: 12px !important;
            }
        }

        @media (min-width: 1024px) {
            .responsive-spacing {
                margin: 16px 0 !important;
                padding: 16px !important;
            }
        }

        /* Responsive text sizes */
        .text-responsive-sm {
            font-size: 12px;
        }

        .text-responsive-md {
            font-size: 14px;
        }

        .text-responsive-lg {
            font-size: 16px;
        }

        @media (min-width: 768px) {
            .text-responsive-sm { font-size: 14px; }
            .text-responsive-md { font-size: 16px; }
            .text-responsive-lg { font-size: 18px; }
        }

        @media (min-width: 1024px) {
            .text-responsive-sm { font-size: 14px; }
            .text-responsive-md { font-size: 16px; }
            .text-responsive-lg { font-size: 20px; }
        }

        /* Responsive images */
        img {
            max-width: 100%;
            height: auto;
        }

        /* Prevent horizontal scroll */
        body {
            overflow-x: hidden;
        }

        /* Mobile-friendly modals */
        @media (max-width: 767px) {
            .modal,
            .popup,
            .dialog {
                width: 95% !important;
                max-width: 95% !important;
                margin: 10px auto !important;
            }
        }

        /* Landscape mobile orientation */
        @media (max-width: 767px) and (orientation: landscape) {
            .ql-header {
                padding: 8px 16px !important;
            }

            .dashboard-title {
                font-size: 1.5rem !important;
            }
        }

        /* Print styles */
        @media print {
            .ql-header,
            .ql-nav,
            .mobile-nav-toggle,
            .floating-dashboard-btn,
            .widget-remove,
            button {
                display: none !important;
            }

            body {
                background: white !important;
                color: black !important;
            }
        }
    `;
    
    document.head.appendChild(responsiveStyles);

    // Apply on load
    applyDeviceClasses();

    // Reapply on resize (debounced)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            applyDeviceClasses();
            console.log('📱 Device detected:', window.QRLegends.device.type, 
                       `(${window.QRLegends.device.width}x${window.QRLegends.device.height})`);
        }, 250);
    });

    // Reapply on orientation change
    window.addEventListener('orientationchange', function() {
        setTimeout(applyDeviceClasses, 100);
    });

    console.log('✅ QR Legends Responsive Design System loaded');
    console.log('📱 Device:', window.QRLegends.device.type);
    console.log('📏 Screen:', `${window.QRLegends.device.width}x${window.QRLegends.device.height}`);
    console.log('👆 Touch:', window.QRLegends.device.isTouch);
})();
