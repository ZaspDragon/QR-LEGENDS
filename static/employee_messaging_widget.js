// Employee Messaging Widget for QR Legends
console.log('Employee Messaging Widget Loading...');

class EmployeeMessagingWidget {constructor() {
        this.messages = []
        this.isOpen = false
        this.unreadCount = 0
        this.init();}

    init() {this.createWidget()
        this.loadMessages()
        this.setupEventListeners()
        console.log('Employee Messaging Widget Ready!');}

    createWidget() {const widgetHtml = `
            <div id="messaging-widget" style="
                position: fixed
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                font-family: 'Segoe UI', sans-serif;
            ">
                <!-- Toggle Button -->
                <button id="messaging-toggle" style="
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-size: 24px;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                    position: relative;
                ">
                    💬
                    <span id="unread-badge" style="
                        position: absolute;
                        top: -5px;
                        right: -5px;
                        background: #ff4757;
                        color: white;
                        border-radius: 50%;
                        width: 20px;
                        height: 20px;
                        font-size: 12px;
                        display: none;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                    ">0</span>
                </button>

                <!-- Chat Panel -->
                <div id="messaging-panel" style="
                    position: absolute;
                    bottom: 70px;
                    right: 0;
                    width: 320px;
                    height: 400px;
                    background: #102943;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                ">
                    <!-- Header -->
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px;
                        font-weight: bold;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <span>📱 Team Messages</span>
                        <button id="close-messaging" style="
                            background: none;
                            border: none;
                            color: white;
                            font-size: 18px;
                            cursor: pointer;
                        ">×</button>
                    </div>

                    <!-- Messages Area -->
                    <div id="messages-container" style="
                        flex: 1;
                        overflow-y: auto;
                        padding: 10px;
                        background: #f8f9fa;
                    ">
                        <div style="text-align: center; color: #666; margin: 20px 0;">
                            No messages yet
                        </div>
                    </div>

                    <!-- Input Area -->
                    <div style="
                        padding: 15px;
                        border-top: 1px solid #e0e0e0;
                        background: #102943;
                    ">
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="message-input" placeholder="Type a message..." style="
                                flex: 1;
                                padding: 10px;
                                border: 2px solid #e0e0e0;
                                border-radius: 20px;
                                outline: none;
                                font-size: 14px;
                            ">
                            <button id="send-message" style="
                                padding: 10px 15px;
                                background: #667eea;
                                color: white;
                                border: none;
                                border-radius: 20px;
                                cursor: pointer;
                                font-size: 14px;
                            ">Send</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHtml);}

    setupEventListeners() {const toggleBtn = document.getElementById('messaging-toggle')
        const closeBtn = document.getElementById('close-messaging')
        const sendBtn = document.getElementById('send-message')
        const messageInput = document.getElementById('message-input');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.togglePanel());}

        if (closeBtn) {closeBtn.addEventListener('click', () => this.closePanel())}

        if (sendBtn) {sendBtn.addEventListener('click', () => this.sendMessage())}

        if (messageInput) {messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage()}
            });
        }
    }

    togglePanel() {const panel = document.getElementById('messaging-panel')
        if (!panel) return

        this.isOpen = !this.isOpen
        panel.style.display = this.isOpen ? 'flex' : 'none';

        if (this.isOpen) {
            this.markAllAsRead();}
    }

    closePanel() {const panel = document.getElementById('messaging-panel')
        if (panel) {
            panel.style.display = 'none'
            this.isOpen = false}
    }

    sendMessage() {
        const input = document.getElementById('message-input')
        if (!input || !input.value.trim()) return

        const message = {
            id: Date.now(),
            text: input.value.trim(),
            sender: 'You',
            timestamp: new Date(),
            isOwn: true
        };

        this.addMessage(message);
        input.value = '';

        // Simulate response (for demo)
        setTimeout(() => {
            this.simulateResponse()
        }, 1000);
    }

    addMessage(message) {this.messages.push(message)
        this.renderMessages()

        if (!message.isOwn && !this.isOpen) {
            this.unreadCount++
            this.updateUnreadBadge();}
    }

    renderMessages() {const container = document.getElementById('messages-container')
        if (!container) return

        if (this.messages.length === 0) {
            container.innerHTML = `
                <div style="text-align: center color: #666; margin: 20px 0;">
                    No messages yet
                </div>
            `;
            return;}

        container.innerHTML = this.messages.map(message => `
            <div style="
                margin-bottom: 15px
                display: flex;
                ${message.isOwn ? 'justify-content: flex-end' : 'justify-content: flex-start'}
            ">
                <div style="
                    max-width: 80%;
                    padding: 10px 15px;
                    border-radius: 18px;
                    ${message.isOwn ? 'background: #667eea; color: white;' : 'background: #102943; color: #1a1a1a; border: 1px solid #e0e0e0;'}
                    font-size: 14px;
                    line-height: 1.4;
                ">
                    <div style="font-weight: bold; margin-bottom: 5px; font-size: 12px; ${message.isOwn ? 'color: white;' : 'color: #2c3e50;'}">
                        ${message.sender}
                    </div>
                    <div style="${message.isOwn ? 'color: white;' : 'color: #1a1a1a;'}">${message.text}</div>
                    <div style="font-size: 11px; margin-top: 5px; ${message.isOwn ? 'color: #f7fbff;' : 'color: #555555;'}">
                        ${this.formatTime(message.timestamp)}
                    </div>
                </div>
            </div>
        `).join('');

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    simulateResponse() {const responses = [
            'Thanks for the update! 👍',
            'Got it, will check that now.',
            'Roger that! 📋',
            'Acknowledged, thanks!',
            'Will take care of it shortly.',
            'Perfect, keep up the good work! 💪'
        ]

        const response = {
            id: Date.now(),
            text: responses[Math.floor(Math.random() * responses.length)],
            sender: 'Supervisor',
            timestamp: new Date(),
            isOwn: false};

        this.addMessage(response);
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    updateUnreadBadge() {const badge = document.getElementById('unread-badge')
        if (!badge) return

        if (this.unreadCount > 0) {
            badge.style.display = 'flex'
            badge.textContent = this.unreadCount > 9 ? '9+' : this.unreadCount;} else {badge.style.display = 'none'}
    }

    markAllAsRead() {this.unreadCount = 0
        this.updateUnreadBadge();}

    loadMessages() {
        // Simulate loading some initial messages
        const initialMessages = [
            {
                id: 1,
                text: 'Welcome to the team messaging system! 🎉',
                sender: 'System',
                timestamp: new Date(Date.now() - 60000),
                isOwn: false
            }
        ];

        initialMessages.forEach(msg => this.addMessage(msg));
    }
}

// Initialize the widget when DOM is ready
document.addEventListener('DOMContentLoaded', () => {if (!document.getElementById('messaging-widget')) {
        window.employeeMessaging = new EmployeeMessagingWidget()}
});

// Export for global access
window.EmployeeMessagingWidget = EmployeeMessagingWidget;