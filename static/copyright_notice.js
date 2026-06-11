
// QR LEGENDS COPYRIGHT PROTECTION
// © 2025 QR LEGENDS by Brandon Evanshine. All rights reserved.

(function() {'use strict'
    
    // Display copyright notice in console
    console.log(
        '\n%c⚠️  QR LEGENDS COPYRIGHT PROTECTION ⚠️\n' +
        '%c© 2025 QR LEGENDS by Brandon Evanshine. All rights reserved.\n\n' +
        '%cUNAUTHORIZED USE PROHIBITED\n' +
        'This software and all QR code generation algorithms are protected by copyright.\n\n' +
        '%c⚠️ WARNING: Reverse engineering, copying, or unauthorized distribution is prohibited.',
        'color: #dc3545 font-size: 16px font-weight: bold',
        'color: #667eea font-size: 14px font-weight: bold;',
        'color: #dc3545; font-size: 12px;',
        'color: #856404; font-size: 12px; font-weight: bold;'
    );
    
    // Basic protection against common developer tools
    const protectionMethods = {
        disableRightClick: function() {
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                return false;});
        },
        
        disableKeyboardShortcuts: function() {document.addEventListener('keydown', function(e) {
                // Disable F12, Ctrl+Shift+I, Ctrl+U, etc.
                if (e.keyCode === 123 || 
                    (e.ctrlKey && e.shiftKey && e.keyCode === 73) ||
                    (e.ctrlKey && e.keyCode === 85)) {
                    e.preventDefault()
                    return false}
            });
        },
        
        addCopyrightWatermark: function() {const watermark = document.createElement('div')
            watermark.innerHTML = '© 2025 QR LEGENDS'
            watermark.style.cssText = `
                position: fixed
                bottom: 10px;
                right: 10px;
                font-size: 10px;
                color: rgba(0,0,0,0.3);
                z-index: 9999;
                pointer-events: none;
                font-family: monospace;
            `;
            document.body.appendChild(watermark)}
    };
    
    // Apply protection methods
    document.addEventListener('DOMContentLoaded', function() {try {
            protectionMethods.disableRightClick()
            protectionMethods.disableKeyboardShortcuts()
            protectionMethods.addCopyrightWatermark()} catch (error) {console.log('Copyright protection initialized with basic features')}
    });
    
    // Export for module usage
    if (typeof module !== 'undefined' && module.exports) {module.exports = protectionMethods}
    
    window.QRLegendsCopyright = protectionMethods;
})();
