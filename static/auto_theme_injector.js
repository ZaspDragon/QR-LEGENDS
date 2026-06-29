// Auto Theme Injector - Ensures all pages load with QR Legends dark theme
(function() {
    'use strict';

    // Skip injection on login pages
    const authPathPattern = /(login|signup|forgot_password|reset_password|two_factor|subscription_suspended)/i;
    if (authPathPattern.test(window.location.pathname) || window.skipNavigationInjection) {
        return;
    }

    function ensureForceDarkTheme() {
        if (document.head && !document.querySelector('link[href*="force_dark_theme.css"]')) {
            const forceLink = document.createElement('link');
            forceLink.rel = 'stylesheet';
            forceLink.href = '/static/force_dark_theme.css';
            document.head.appendChild(forceLink);
        }
    }

    ensureForceDarkTheme();

    // Inject immediately to prevent white flash
    const style = document.createElement('style');
    style.innerHTML = `
        body {
            background: radial-gradient(1200px 600px at 60% -100px, #123a86 0%, #0e2242 45%, #081b2e 100%) fixed !important;
            color: #f7fbff !important;
            font-family: Inter, ui-sans-serif, system-ui, Arial, sans-serif !important;
            min-height: 100vh;
        }

        * {
            box-sizing: border-box;
        }

        .container, .main-content {
            background: #102943 !important;
            background-color: #102943 !important;
            backdrop-filter: none !important;
            border-radius: 16px;
            padding: 24px;
            margin: 20px auto;
            max-width: 1200px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid rgba(99, 102, 241, 0.2);
            color: #f7fbff !important;
        }

        .loading, [class*="loading"] {
            opacity: 1 !important;
            animation: none !important;
            filter: none !important;
        }
    `;
    document.head.insertBefore(style, document.head.firstChild);

    // Load the full professional styling
    const link = document.createElement('script');
    link.src = '/static/apply_professional_styling.js';
    document.head.appendChild(link);

    // Load responsive design system
    const responsiveScript = document.createElement('script');
    responsiveScript.src = '/static/responsive_design.js';
    document.head.appendChild(responsiveScript);
    ensureForceDarkTheme();

    // Force dark theme for all pages
    const currentTheme = 'dark';
    // Save to localStorage to ensure consistency
    try {
        localStorage.setItem('qr-legends-theme', 'dark');
    } catch(e) {}

    // Apply theme when DOM is ready
    function applyTheme() {
        if (document.body && document.body.classList) {
            try {
                document.body.classList.remove('light-theme', 'dark-theme');
                document.body.classList.add(currentTheme + '-theme');
            } catch(e) {
                console.log('Theme application skipped:', e.message);
            }
        }
    }

    // Apply immediately if body exists, otherwise wait for DOM
    if (document.body && document.body.classList) {
        applyTheme();
    } else {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', applyTheme);
        } else {
            setTimeout(applyTheme, 100);
        }
    }

    document.addEventListener('DOMContentLoaded', ensureForceDarkTheme);
})();
