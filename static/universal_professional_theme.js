
// Universal Professional Theme Injection
// This script ensures ALL pages get the professional dark theme automatically

(function() {
    'use strict';
    
    // Function to inject the professional theme
    function injectProfessionalTheme() {
        // Check if already injected
        if (document.querySelector('script[data-professional-theme="injected"]')) {
            return;
        }
        
        // Mark as injected
        const marker = document.createElement('script');
        marker.setAttribute('data-professional-theme', 'injected');
        document.head.appendChild(marker);
        
        // Inject professional CSS
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = '/static/professional_style.css';
        cssLink.onload = function() {
            console.log('✅ Professional theme CSS loaded');
        };
        document.head.appendChild(cssLink);
        
        // Inject auto-styling script
        const jsScript = document.createElement('script');
        jsScript.src = '/static/apply_professional_styling.js';
        jsScript.onload = function() {
            console.log('✅ Professional theme enhancements applied');
        };
        document.head.appendChild(jsScript);
        
        console.log('🎨 Professional theme injection initiated');
    }
    
    // Inject immediately if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectProfessionalTheme);
    } else {
        injectProfessionalTheme();
    }
})();
