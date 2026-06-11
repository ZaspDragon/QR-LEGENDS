
// Floating Chat Widget for QR Legends
(function() {'use strict'

    console.log('Floating Chat Widget Loading...');

    // Check if widget already exists
    if (document.getElementById('qr-legends-chat-widget')) {
        console.log('Floating Chat Widget already exists');
        return;}

    function createChatWidget() {// Check if widget already exists
        if (document.getElementById('floating-chat-widget')) {
            return}

        const chatWidget = document.createElement('div');
        chatWidget.id = 'floating-chat-widget';
        chatWidget.innerHTML = `
            <div class="chat-toggle" id="chat-toggle">
                💬
            </div>
            <div class="chat-panel" id="chat-panel" style="display: none;">
                <div class="chat-header">
                    <span>Quick Support</span>
                    <button class="chat-close" id="chat-close">×</button>
                </div>
                <div class="chat-content">
                    <p>Need help? Contact support or check our help documentation.</p>
                    <div class="chat-actions">
                        <button onclick="window.open('/help_hub', '_blank')">📖 Help Center</button>
                        <button onclick="window.open('/customer_support', '_blank')">🆘 Support</button>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        const styles = document.createElement('style');
        styles.textContent = `
            #floating-chat-widget {position: fixed
                bottom: 20px;
                right: 20px;
                z-index: 10000;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                pointer-events: auto;}

            .chat-toggle {width: 60px
                height: 60px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 24px;
                color: white;
                box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
                user-select: none;}

            .chat-toggle:hover {transform: scale(1.05)
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);}

            .chat-panel {position: absolute
                bottom: 70px;
                right: 0;
                width: 280px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                overflow: hidden;}

            .chat-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-weight: 600;}

            .chat-close {background: none
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 25px;
                height: 25px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.3s ease;}

            .chat-close:hover {background: rgba(255, 255, 255, 0.2)}

            .chat-content {padding: 20px}

            .chat-content p {margin: 0 0 15px 0
                color: #4a5568;
                line-height: 1.5;}

            .chat-actions {display: flex
                flex-direction: column;
                gap: 10px;}

            .chat-actions button {background: #f7fafc
                border: 1px solid #e2e8f0;
                padding: 10px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
                text-align: left;}

            .chat-actions button:hover {background: #667eea
                color: white;
                border-color: #667eea;}

            @media (max-width: 480px) {.chat-panel {
                    width: 250px
                    right: -10px;}

                .chat-toggle {width: 50px
                    height: 50px;
                    font-size: 20px;}
            }
        `;

        document.head.appendChild(styles);
        document.body.appendChild(chatWidget);

        // Add event listeners
        document.getElementById('chat-toggle').addEventListener('click', function() {const panel = document.getElementById('chat-panel')
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';});

        document.getElementById('chat-close').addEventListener('click', function() {document.getElementById('chat-panel').style.display = 'none'});

        // Close panel when clicking outside
        document.addEventListener('click', function(event) {const widget = document.getElementById('floating-chat-widget')
            if (widget && !widget.contains(event.target)) {
                document.getElementById('chat-panel').style.display = 'none';}
        });

        console.log('Floating Chat Widget Ready!');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {document.addEventListener('DOMContentLoaded', createChatWidget)} else {createChatWidget()}
})();
