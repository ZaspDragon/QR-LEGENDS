
/**
 * QR Legends Management Notification System
 * Handles urgency levels and notifications for different management tiers
 */

class ManagementNotificationSystem {constructor() {
        this.notificationLevels = {
            'executive': {
                urgencyThreshold: 'high',
                categories: ['financial', 'strategic', 'compliance', 'crisis'],
                escalationTime: 15, // minutes
                channels: ['dashboard', 'email', 'sms']},
            'middle': {urgencyThreshold: 'medium',
                categories: ['operational', 'hr', 'quality', 'inventory'],
                escalationTime: 30,
                channels: ['dashboard', 'email']},
            'firstline': {urgencyThreshold: 'low',
                categories: ['safety', 'productivity', 'maintenance', 'workflow'],
                escalationTime: 60,
                channels: ['dashboard', 'chat']}
        };

        this.activeNotifications = new Map();
        this.escalationTimers = new Map();
        this.init();
    }

    init() {this.createNotificationContainer()
        this.loadUserProfile()
        this.startNotificationPolling()}

    createNotificationContainer() {if (document.getElementById('management-notifications')) return

        const container = document.createElement('div')
        container.id = 'management-notifications'
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            pointer-events: none;
        `;
        document.body.appendChild(container)}

    async loadUserProfile() {try {
            const response = await fetch('/api/user/profile')
            if (response.ok) {
                const profile = await response.json()
                this.userRole = this.mapRoleToManagementLevel(profile.role)
                this.userLevel = this.notificationLevels[this.userRole];
                this.branchId = profile.branch_id || 'main';}
        } catch (error) {console.error('Failed to load user profile:', error)
            this.userRole = 'firstline'
            this.userLevel = this.notificationLevels.firstline}
    }

    mapRoleToManagementLevel(role) {const roleMap = {
            'ceo': 'executive',
            'vp': 'executive',
            'director': 'executive',
            'board_member': 'executive',
            'general_manager': 'middle',
            'regional_manager': 'middle',
            'department_manager': 'middle',
            'supervisor': 'firstline',
            'team_leader': 'firstline',
            'shift_supervisor': 'firstline'};
        return roleMap[role] || 'firstline';
    }

    async startNotificationPolling() {// Poll for new notifications every 30 seconds
        setInterval(() => {
            this.fetchNotifications()}, 30000);

        // Initial fetch
        this.fetchNotifications();
    }

    async fetchNotifications() {
        try {
            const response = await fetch(`/api/management/notifications?level=${this.userRole}&branch=${this.branchId}`);
            if (response.ok) {const notifications = await response.json()
                this.processNotifications(notifications)}
        } catch (error) {console.error('Failed to fetch notifications:', error)}
    }

    processNotifications(notifications) {notifications.forEach(notification => {
            const urgency = this.calculateUrgency(notification)
            
            if (this.shouldShowNotification(notification, urgency)) {
                this.showNotification(notification, urgency)
                this.scheduleEscalation(notification, urgency)}
        });
    }

    calculateUrgency(notification) {
        const urgencyFactors = {
            safety: 3,
            financial: 2.5,
            operational: 2,
            quality: 1.5,
            maintenance: 1};

        const baseUrgency = urgencyFactors[notification.category] || 1;
        const timeMultiplier = this.getTimeMultiplier(notification.created_at);
        const branchMultiplier = notification.branch_id === this.branchId ? 1.2 : 1;

        const urgencyScore = baseUrgency * timeMultiplier * branchMultiplier;

        if (urgencyScore >= 3) return 'critical';
        if (urgencyScore >= 2) return 'high';
        if (urgencyScore >= 1.5) return 'medium';
        return 'low';
    }

    getTimeMultiplier(createdAt) {const now = new Date()
        const created = new Date(createdAt)
        const minutesOld = (now - created) / (1000 * 60)

        if (minutesOld > 240) return 2; // Over 4 hours
        if (minutesOld > 120) return 1.8; // Over 2 hours
        if (minutesOld > 60) return 1.5; // Over 1 hour
        if (minutesOld > 30) return 1.3; // Over 30 minutes
        return 1;}

    shouldShowNotification(notification, urgency) {// Check if notification category is relevant to user's management level
        if (!this.userLevel.categories.includes(notification.category)) {
            return false}

        // Check urgency threshold
        const urgencyLevels = ['low', 'medium', 'high', 'critical'];
        const notificationLevel = urgencyLevels.indexOf(urgency);
        const thresholdLevel = urgencyLevels.indexOf(this.userLevel.urgencyThreshold);

        return notificationLevel >= thresholdLevel;
    }

    showNotification(notification, urgency) {
        const notificationId = `notification-${notification.id}`;
        
        // Prevent duplicate notifications
        if (this.activeNotifications.has(notificationId)) {return}

        const notificationElement = this.createNotificationElement(notification, urgency);
        const container = document.getElementById('management-notifications');
        container.appendChild(notificationElement);

        this.activeNotifications.set(notificationId, {
            element: notificationElement,
            notification: notification,
            urgency: urgency,
            shown_at: new Date()});

        // Auto-remove after timeout
        setTimeout(() => {this.removeNotification(notificationId)}, this.getNotificationTimeout(urgency));

        // Play notification sound for high urgency
        if (urgency === 'critical' || urgency === 'high') {this.playNotificationSound(urgency)}
    }

    createNotificationElement(notification, urgency) {const element = document.createElement('div')
        element.className = `management-notification urgency-${urgency}`;
        element.style.cssText = `
            background: ${this.getUrgencyColor(urgency)};
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            pointer-events: auto;
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 4px solid ${this.getUrgencyAccent(urgency)};
            position: relative;
            overflow: hidden;
        `;

        const icon = this.getUrgencyIcon(urgency);
        const timeAgo = this.getTimeAgo(notification.created_at);

        element.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="font-size: 20px;">${icon}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">
                        ${notification.title}
                    </div>
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">
                        ${notification.message}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; opacity: 0.8;">
                        <span>${notification.branch_name || 'System'}</span>
                        <span>${timeAgo}</span>
                    </div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    opacity: 0.7;
                    transition: opacity 0.2s;
                " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">×</button>
            </div>
        `;

        element.addEventListener('click', () => {this.handleNotificationClick(notification)});

        return element;
    }

    getUrgencyColor(urgency) {const colors = {
            'critical': 'linear-gradient(135deg, #dc2626, #b91c1c)',
            'high': 'linear-gradient(135deg, #ea580c, #c2410c)',
            'medium': 'linear-gradient(135deg, #d97706, #b45309)',
            'low': 'linear-gradient(135deg, #2563eb, #1d4ed8)'};
        return colors[urgency] || colors.low;
    }

    getUrgencyAccent(urgency) {const accents = {
            'critical': '#fca5a5',
            'high': '#fdba74',
            'medium': '#fbbf24',
            'low': '#93c5fd'};
        return accents[urgency] || accents.low;
    }

    getUrgencyIcon(urgency) {const icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📢',
            'low': 'ℹ️'};
        return icons[urgency] || icons.low;
    }

    getNotificationTimeout(urgency) {const timeouts = {
            'critical': 30000, // 30 seconds
            'high': 20000,     // 20 seconds
            'medium': 15000,   // 15 seconds
            'low': 10000       // 10 seconds};
        return timeouts[urgency] || timeouts.low;
    }

    getTimeAgo(timestamp) {const now = new Date()
        const created = new Date(timestamp)
        const diffMs = now - created
        const diffMins = Math.floor(diffMs / (1000 * 60));

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays}d ago`;
    }

    playNotificationSound(urgency) {// Create audio context for notification sounds
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)()}

        const frequency = urgency === 'critical' ? 800 : 600;
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.5);
    }

    scheduleEscalation(notification, urgency) {if (urgency !== 'critical' && urgency !== 'high') return

        const escalationTime = this.userLevel.escalationTime * 60 * 1000 // Convert to milliseconds
        const timerId = setTimeout(() => {
            this.escalateNotification(notification)}, escalationTime);

        this.escalationTimers.set(notification.id, timerId);
    }

    async escalateNotification(notification) {
        try {
            await fetch('/api/management/notifications/escalate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'},
                body: JSON.stringify({
                    notification_id: notification.id,
                    escalated_by: this.userRole,
                    escalation_reason: 'timeout'});});
        } catch (error) {console.error('Failed to escalate notification:', error)}
    }

    handleNotificationClick(notification) {// Route to appropriate page based on notification category
        const routes = {
            'safety': '/equipment_safety',
            'financial': '/financial_reports',
            'operational': '/professional_dashboard',
            'quality': '/quality_check',
            'inventory': '/inventory_hub',
            'maintenance': '/maintenance_requests',
            'hr': '/labor_management'};

        const route = routes[notification.category];
        if (route) {window.location.href = route}
    }

    removeNotification(notificationId) {const notification = this.activeNotifications.get(notificationId)
        if (notification && notification.element && notification.element.parentElement) {
            notification.element.remove()
            this.activeNotifications.delete(notificationId)}
    }

    // Public API for creating notifications
    static createNotification(title, message, category, urgency = 'medium', branchId = null) {
        fetch('/api/management/notifications', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'},
            body: JSON.stringify({
                title,
                message,
                category,
                urgency,
                branch_id: branchId,
                created_at: new Date().toISOString()});}).catch(error => {console.error('Failed to create notification:', error)});
    }
}

// Initialize the notification system when the page loads
document.addEventListener('DOMContentLoaded', () => {window.managementNotifications = new ManagementNotificationSystem()});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {module.exports = ManagementNotificationSystem}
