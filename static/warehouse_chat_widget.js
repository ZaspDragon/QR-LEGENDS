(function() {'use strict'

    console.log('Warehouse Chat Widget Loading...')

    function createWarehouseChatWidget() {
        // Check if widget already exists
        if (document.getElementById('warehouse-chat-widget')) {
            return;}

        const chatWidget = document.createElement('div');
        chatWidget.id = 'warehouse-chat-widget';
        chatWidget.innerHTML = `
            <div class="warehouse-chat-toggle" id="warehouse-chat-toggle">
                💬
            </div>
            <div class="warehouse-chat-panel" id="warehouse-chat-panel" style="display: none;">
                <div class="warehouse-chat-header">
                    <span>🏭 Team Chat</span>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button onclick="window.open('/warehouse_chat', '_blank')" style="background: rgba(16,41,67,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px;">📱 Full Chat</button>
                        <button class="warehouse-chat-close" id="warehouse-chat-close">×</button>
                    </div>
                </div>
                <div class="warehouse-chat-tabs">
                    <button class="warehouse-tab active" data-channel="company_wide" onclick="switchWarehouseChannel('company_wide')">Company</button>
                    <button class="warehouse-tab" data-channel="department" onclick="switchWarehouseChannel('department')">Department</button>
                    <button class="warehouse-tab" data-channel="urgent" onclick="switchWarehouseChannel('urgent')">Urgent</button>
                </div>
                <div class="warehouse-chat-messages" id="warehouse-chat-messages">
                    <div class="warehouse-message system">
                        <strong>🏭 Warehouse Chat</strong><br>
                        Connect with your team across all departments and locations.
                    </div>
                </div>
                <div class="warehouse-chat-input-area">
                    <button class="urgent-toggle" id="warehouse-urgent-toggle" onclick="toggleWarehouseUrgent()">🚨</button>
                    <input type="text" id="warehouse-chat-input" placeholder="Type message... Use @name to mention" onkeypress="handleWarehouseChatEnter(event)">
                    <button onclick="sendWarehouseMessage()">Send</button>
                </div>
            </div>
        `;

        // Add styles
        const styles = `
            <style>
            #warehouse-chat-widget {position: fixed
                bottom: 20px
                right: 20px;
                z-index: 9998;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}

            .warehouse-chat-toggle {width: 60px
                height: 60px
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
                user-select: none}

            .warehouse-chat-toggle:hover {transform: scale(1.05)
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6)}

            .warehouse-chat-panel {position: absolute
                bottom: 70px
                right: 0;
                width: 320px;
                height: 450px;
                background: #102943;
                border-radius: 12px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                overflow: hidden;
                display: flex;
                flex-direction: column}

            .warehouse-chat-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
                color: white
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-weight: 600}

            .warehouse-chat-close {background: none
                border: none
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
                transition: background 0.3s ease}

            .warehouse-chat-close:hover {background: rgba(16,41,67,0.2)}

            .warehouse-chat-tabs {display: flex
                background: #f8f9fa
                border-bottom: 1px solid #e5e7eb}

            .warehouse-tab {flex: 1
                padding: 8px 12px
                border: none;
                background: none;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                color: #6b7280;
                transition: all 0.3s ease}

            .warehouse-tab.active {background: #667eea
                color: white}

            .warehouse-chat-messages {flex: 1
                padding: 15px
                overflow-y: auto;
                background: #f9fafb}

            .warehouse-message {margin-bottom: 12px
                padding: 8px 12px
                border-radius: 8px;
                max-width: 85%;
                word-wrap: break-word;
                font-size: 13px}

            .warehouse-message.system {background: #e5f3ff
                border-left: 3px solid #667eea
                max-width: 100%;
                text-align: center}

            .warehouse-message.sent {background: #667eea
                color: white
                margin-left: auto;
                text-align: right}

            .warehouse-message.received {background: #102943
                border: 1px solid #e5e7eb}

            .warehouse-message.urgent {border-left: 4px solid #dc2626
                background: #fef2f2}

            .warehouse-chat-input-area {display: flex
                padding: 12px
                border-top: 1px solid #e5e7eb;
                background: #102943;
                gap: 8px}

            .urgent-toggle {background: #f3f4f6
                border: 1px solid #d1d5db
                padding: 6px 8px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease}

            .urgent-toggle.active {background: #dc2626
                color: white
                border-color: #f7fbff}

            .warehouse-chat-input-area input {flex: 1
                padding: 8px 12px
                border: 1px solid #d1d5db;
                border-radius: 16px;
                outline: none;
                font-size: 13px}

            .warehouse-chat-input-area button: last-child {background: #667eea
                color: white
                border: none;
                padding: 8px 16px;
                border-radius: 16px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: background 0.3s ease}

            .warehouse-chat-input-area button:last-child:hover {background: #5b21b6}

            .mentions {color: #667eea
                font-weight: bold}

            @media (max-width: 768px) {.warehouse-chat-panel {
                    width: 280px
                    right: -10px}

                .warehouse-chat-toggle {width: 50px
                    height: 50px
                    font-size: 20px}
            }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
        document.body.appendChild(chatWidget);

        // Add event listeners
        document.getElementById('warehouse-chat-toggle').addEventListener('click', function() {const panel = document.getElementById('warehouse-chat-panel')
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none'
            if (panel.style.display === 'block') {
                loadWarehouseMessages();}
        });

        document.getElementById('warehouse-chat-close').addEventListener('click', function() {document.getElementById('warehouse-chat-panel').style.display = 'none'});

        // Close panel when clicking outside
        document.addEventListener('click', function(event) {const widget = document.getElementById('warehouse-chat-widget')
            if (widget && !widget.contains(event.target)) {
                document.getElementById('warehouse-chat-panel').style.display = 'none'}
        });

        // Global variables and functions
        let warehouseCurrentChannel = 'company_wide';
        let warehouseIsUrgent = false;

        window.switchWarehouseChannel = function(channel) {warehouseCurrentChannel = channel

            document.querySelectorAll('.warehouse-tab').forEach(tab => {
                tab.classList.remove('active')});
            document.querySelector(`[data-channel="${channel}"]`).classList.add('active');

            loadWarehouseMessages();
        };

        window.toggleWarehouseUrgent = function() {warehouseIsUrgent = !warehouseIsUrgent
            const btn = document.getElementById('warehouse-urgent-toggle')
            btn.classList.toggle('active', warehouseIsUrgent);};

        window.handleWarehouseChatEnter = function(event) {if (event.key === 'Enter') {
                sendWarehouseMessage()}
        };

        window.sendWarehouseMessage = async function() {const input = document.getElementById('warehouse-chat-input')
            const message = input.value.trim()

            if (!message) return;

            try {
                const response = await fetch('/api/employee/department-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        department: warehouseCurrentChannel,
                        content: message,
                        urgent: warehouseIsUrgent});});

                if (response.ok) {input.value = ''
                    if (warehouseIsUrgent) {
                        toggleWarehouseUrgent()}
                    loadWarehouseMessages();
                } else {addWarehouseMessage('Failed to send message. Please try again.', 'system')}
            } catch (error) {addWarehouseMessage('Network error. Please check your connection.', 'system')}
        };

        async function loadWarehouseMessages() {
            try {
                const response = await fetch(`/api/employee/department-messages/${warehouseCurrentChannel}`);
                if (response.ok) {const data = await response.json()
                    displayWarehouseMessages(data.messages || [])} else {addWarehouseMessage('Error loading messages', 'system')}
            } catch (error) {addWarehouseMessage('Network error loading messages', 'system')}
        }

        function displayWarehouseMessages(messages) {const container = document.getElementById('warehouse-chat-messages')

            if (messages.length === 0) {
                container.innerHTML = `
                    <div class="warehouse-message system">
                        <strong>💬 ${warehouseCurrentChannel.replace('_', ' ').toUpperCase()}</strong><br>
                        No messages yet. Start the conversation!
                    </div>
                `;
                return;
            }

            container.innerHTML = messages.map(msg => {
                const isOwn = false // Would check against current user
                const messageClass = `warehouse-message ${isOwn ? 'sent' : 'received'} ${msg.urgent ? 'urgent' : ''}`

                let content = msg.content;
                if (msg.mentions) {
                    msg.mentions.forEach(mention => {
                        content = content.replace(new RegExp(`@${mention.name}`, 'gi'), `<span class="mentions">@${mention.name}</span>`);
                    });
                }

                return `
                    <div class="${messageClass}">
                        <div style="font-size: 11px; font-weight: bold; margin-bottom: 3px;">
                            ${msg.sender_name} ${msg.sender_role ? `(${msg.sender_role})` : ''}
                            <span style="float: right; font-weight: normal;">${new Date(msg.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div>${content}</div>
                        ${msg.urgent ? '<div style="color: #f7fbff font-weight: bold font-size: 10px margin-top: 3px">⚠️ URGENT</div>' : ''}
                    </div>
                `;
            }).join('');

            container.scrollTop = container.scrollHeight;
        }

        function addWarehouseMessage(text, type) {const container = document.getElementById('warehouse-chat-messages')
            const messageDiv = document.createElement('div')
            messageDiv.className = `warehouse-message ${type}`;
            messageDiv.innerHTML = `<strong>🏭 System</strong><br>${text}`;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        console.log('Warehouse Chat Widget Ready!');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {document.addEventListener('DOMContentLoaded', createWarehouseChatWidget)} else {createWarehouseChatWidget()}

})();
(function() {'use strict'

    console.log('Warehouse Chat Widget Loading...')

    function createWarehouseChatWidget() {
        // Check if widget already exists
        if (document.getElementById('warehouse-chat-widget')) {
            return;}

        const chatWidget = document.createElement('div');
        chatWidget.id = 'warehouse-chat-widget';
        chatWidget.innerHTML = `
            <div class="warehouse-chat-toggle" id="warehouse-chat-toggle">
                💬
            </div>
            <div class="warehouse-chat-panel" id="warehouse-chat-panel" style="display: none;">
                <div class="warehouse-chat-header">
                    <span>🏭 Team Chat</span>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button onclick="window.open('/warehouse_chat', '_blank')" style="background: rgba(16,41,67,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px;">📱 Full Chat</button>
                        <button class="warehouse-chat-close" id="warehouse-chat-close">×</button>
                    </div>
                </div>
                <div class="warehouse-chat-tabs">
                    <button class="warehouse-tab active" data-channel="company_wide" onclick="switchWarehouseChannel('company_wide')">Company</button>
                    <button class="warehouse-tab" data-channel="department" onclick="switchWarehouseChannel('department')">Department</button>
                    <button class="warehouse-tab" data-channel="urgent" onclick="switchWarehouseChannel('urgent')">Urgent</button>
                </div>
                <div class="warehouse-chat-messages" id="warehouse-chat-messages">
                    <div class="warehouse-message system">
                        <strong>🏭 Warehouse Chat</strong><br>
                        Connect with your team across all departments and locations.
                    </div>
                </div>
                <div class="warehouse-chat-input-area">
                    <button class="urgent-toggle" id="warehouse-urgent-toggle" onclick="toggleWarehouseUrgent()">🚨</button>
                    <input type="text" id="warehouse-chat-input" placeholder="Type message... Use @name to mention" onkeypress="handleWarehouseChatEnter(event)">
                    <button onclick="sendWarehouseMessage()">Send</button>
                </div>
            </div>
        `;

        // Add styles
        const styles = `
            <style>
            #warehouse-chat-widget {position: fixed
                bottom: 20px
                right: 20px;
                z-index: 9998;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}

            .warehouse-chat-toggle {width: 60px
                height: 60px
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
                user-select: none}

            .warehouse-chat-toggle:hover {transform: scale(1.05)
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6)}

            .warehouse-chat-panel {position: absolute
                bottom: 70px
                right: 0;
                width: 320px;
                height: 450px;
                background: #102943;
                border-radius: 12px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                overflow: hidden;
                display: flex;
                flex-direction: column}

            .warehouse-chat-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
                color: white
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-weight: 600}

            .warehouse-chat-close {background: none
                border: none
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
                transition: background 0.3s ease}

            .warehouse-chat-close:hover {background: rgba(16,41,67,0.2)}

            .warehouse-chat-tabs {display: flex
                background: #f8f9fa
                border-bottom: 1px solid #e5e7eb}

            .warehouse-tab {flex: 1
                padding: 8px 12px
                border: none;
                background: none;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                color: #6b7280;
                transition: all 0.3s ease}

            .warehouse-tab.active {background: #667eea
                color: white}

            .warehouse-chat-messages {flex: 1
                padding: 15px
                overflow-y: auto;
                background: #f9fafb}

            .warehouse-message {margin-bottom: 12px
                padding: 8px 12px
                border-radius: 8px;
                max-width: 85%;
                word-wrap: break-word;
                font-size: 13px}

            .warehouse-message.system {background: #e5f3ff
                border-left: 3px solid #667eea
                max-width: 100%;
                text-align: center}

            .warehouse-message.sent {background: #667eea
                color: white
                margin-left: auto;
                text-align: right}

            .warehouse-message.received {background: #102943
                border: 1px solid #e5e7eb}

            .warehouse-message.urgent {border-left: 4px solid #dc2626
                background: #fef2f2}

            .warehouse-chat-input-area {display: flex
                padding: 12px
                border-top: 1px solid #e5e7eb;
                background: #102943;
                gap: 8px}

            .urgent-toggle {background: #f3f4f6
                border: 1px solid #d1d5db
                padding: 6px 8px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease}

            .urgent-toggle.active {background: #dc2626
                color: white
                border-color: #f7fbff}

            .warehouse-chat-input-area input {flex: 1
                padding: 8px 12px
                border: 1px solid #d1d5db;
                border-radius: 16px;
                outline: none;
                font-size: 13px}

            .warehouse-chat-input-area button: last-child {background: #667eea
                color: white
                border: none;
                padding: 8px 16px;
                border-radius: 16px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: background 0.3s ease}

            .warehouse-chat-input-area button:last-child:hover {background: #5b21b6}

            .mentions {color: #667eea
                font-weight: bold}

            @media (max-width: 768px) {.warehouse-chat-panel {
                    width: 280px
                    right: -10px}

                .warehouse-chat-toggle {width: 50px
                    height: 50px
                    font-size: 20px}
            }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
        document.body.appendChild(chatWidget);

        // Add event listeners
        document.getElementById('warehouse-chat-toggle').addEventListener('click', function() {const panel = document.getElementById('warehouse-chat-panel')
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none'
            if (panel.style.display === 'block') {
                loadWarehouseMessages();}
        });

        document.getElementById('warehouse-chat-close').addEventListener('click', function() {document.getElementById('warehouse-chat-panel').style.display = 'none'});

        // Close panel when clicking outside
        document.addEventListener('click', function(event) {const widget = document.getElementById('warehouse-chat-widget')
            if (widget && !widget.contains(event.target)) {
                document.getElementById('warehouse-chat-panel').style.display = 'none'}
        });

        // Global variables and functions
        let warehouseCurrentChannel = 'company_wide';
        let warehouseIsUrgent = false;

        window.switchWarehouseChannel = function(channel) {warehouseCurrentChannel = channel

            document.querySelectorAll('.warehouse-tab').forEach(tab => {
                tab.classList.remove('active')});
            document.querySelector(`[data-channel="${channel}"]`).classList.add('active');

            loadWarehouseMessages();
        };

        window.toggleWarehouseUrgent = function() {warehouseIsUrgent = !warehouseIsUrgent
            const btn = document.getElementById('warehouse-urgent-toggle')
            btn.classList.toggle('active', warehouseIsUrgent);};

        window.handleWarehouseChatEnter = function(event) {if (event.key === 'Enter') {
                sendWarehouseMessage()}
        };

        window.sendWarehouseMessage = async function() {const input = document.getElementById('warehouse-chat-input')
            const message = input.value.trim()

            if (!message) return;

            try {
                const response = await fetch('/api/employee/department-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        department: warehouseCurrentChannel,
                        content: message,
                        urgent: warehouseIsUrgent});});

                if (response.ok) {input.value = ''
                    if (warehouseIsUrgent) {
                        toggleWarehouseUrgent()}
                    loadWarehouseMessages();
                } else {addWarehouseMessage('Failed to send message. Please try again.', 'system')}
            } catch (error) {addWarehouseMessage('Network error. Please check your connection.', 'system')}
        };

        async function loadWarehouseMessages() {
            try {
                const response = await fetch(`/api/employee/department-messages/${warehouseCurrentChannel}`);
                if (response.ok) {const data = await response.json()
                    displayWarehouseMessages(data.messages || [])} else {addWarehouseMessage('Error loading messages', 'system')}
            } catch (error) {addWarehouseMessage('Network error loading messages', 'system')}
        }

        function displayWarehouseMessages(messages) {const container = document.getElementById('warehouse-chat-messages')

            if (messages.length === 0) {
                container.innerHTML = `
                    <div class="warehouse-message system">
                        <strong>💬 ${warehouseCurrentChannel.replace('_', ' ').toUpperCase()}</strong><br>
                        No messages yet. Start the conversation!
                    </div>
                `;
                return;
            }

            container.innerHTML = messages.map(msg => {
                const isOwn = false // Would check against current user
                const messageClass = `warehouse-message ${isOwn ? 'sent' : 'received'} ${msg.urgent ? 'urgent' : ''}`

                let content = msg.content;
                if (msg.mentions) {
                    msg.mentions.forEach(mention => {
                        content = content.replace(new RegExp(`@${mention.name}`, 'gi'), `<span class="mentions">@${mention.name}</span>`);
                    });
                }

                return `
                    <div class="${messageClass}">
                        <div style="font-size: 11px; font-weight: bold; margin-bottom: 3px;">
                            ${msg.sender_name} ${msg.sender_role ? `(${msg.sender_role})` : ''}
                            <span style="float: right; font-weight: normal;">${new Date(msg.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div>${content}</div>
                        ${msg.urgent ? '<div style="color: #f7fbff font-weight: bold font-size: 10px margin-top: 3px">⚠️ URGENT</div>' : ''}
                    </div>
                `;
            }).join('');

            container.scrollTop = container.scrollHeight;
        }

        function addWarehouseMessage(text, type) {const container = document.getElementById('warehouse-chat-messages')
            const messageDiv = document.createElement('div')
            messageDiv.className = `warehouse-message ${type}`;
            messageDiv.innerHTML = `<strong>🏭 System</strong><br>${text}`;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        console.log('Warehouse Chat Widget Ready!');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {document.addEventListener('DOMContentLoaded', createWarehouseChatWidget)} else {createWarehouseChatWidget()}
})();