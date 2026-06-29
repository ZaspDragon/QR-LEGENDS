
// Warehouse User Tracking and Safety System
class WarehouseUserTracker {
    constructor() {
        this.userLocations = new Map();
        this.currentUser = null;
        this.warningDistance = 10; // meters
        this.updateInterval = 2000; // 2 seconds
        this.isTracking = false;
        this.navigationActive = false;
        
        this.init();
    }

    init() {
        console.log("🗺️ Warehouse User Tracking System Loading...");
        this.setupLocationTracking();
        this.startLocationUpdates();
        this.setupSafetyWarnings();
        console.log("✅ User Tracking System Ready!");
    }

    setupLocationTracking() {
        // Get current user info
        this.currentUser = {
            id: sessionStorage.getItem('user_id') || 'user_' + Date.now(),
            name: sessionStorage.getItem('username') || 'Driver',
            role: sessionStorage.getItem('role') || 'driver',
            device: navigator.userAgent.includes('Mobile') ? 'mobile' : 'desktop'
        };

        // Start geolocation if available
        if (navigator.geolocation) {
            this.isTracking = true;
            this.watchPosition();
        }
    }

    watchPosition() {
        navigator.geolocation.watchPosition(
            (position) => {
                this.updateUserLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: Date.now(),
                    zone: this.determineZone(position.coords.latitude, position.coords.longitude)
                });
            },
            (error) => {
                console.warn("Location tracking error:", error.message);
                // Fallback to manual zone entry
                this.showZoneSelector();
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 5000
            }
        );
    }

    determineZone(lat, lng) {
        // Mock zone determination - in real app this would use warehouse layout
        const zones = ['A', 'B', 'C', 'D', 'E'];
        const mockZone = zones[Math.floor(Math.random() * zones.length)];
        const mockAisle = Math.floor(Math.random() * 20) + 1;
        const mockBay = Math.floor(Math.random() * 50) + 1;
        
        return `${mockZone}-${mockAisle.toString().padStart(2, '0')}-${mockBay.toString().padStart(2, '0')}`;
    }

    updateUserLocation(location) {
        const userUpdate = {
            ...this.currentUser,
            location: location,
            lastSeen: Date.now(),
            status: this.navigationActive ? 'navigating' : 'stationary'
        };

        this.userLocations.set(this.currentUser.id, userUpdate);
        
        // Send to server
        this.syncWithServer(userUpdate);
        
        // Check for nearby users
        this.checkNearbyUsers();
        
        // Update UI
        this.updateLocationDisplay(location);
    }

    async syncWithServer(userUpdate) {
        try {
            await fetch('/api/warehouse/user-location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userUpdate)
            });
        } catch (error) {
            console.warn("Failed to sync location with server:", error);
        }
    }

    async fetchNearbyUsers() {
        try {
            const response = await fetch('/api/warehouse/nearby-users');
            const data = await response.json();
            
            if (data.success) {
                // Update local user map
                data.users.forEach(user => {
                    if (user.id !== this.currentUser.id) {
                        this.userLocations.set(user.id, user);
                    }
                });
            }
        } catch (error) {
            console.warn("Failed to fetch nearby users:", error);
        }
    }

    checkNearbyUsers() {
        const currentLocation = this.userLocations.get(this.currentUser.id);
        if (!currentLocation) return;

        const nearbyUsers = [];
        
        this.userLocations.forEach((user, userId) => {
            if (userId === this.currentUser.id) return;
            
            const distance = this.calculateDistance(currentLocation.location, user.location);
            
            if (distance <= this.warningDistance) {
                nearbyUsers.push({
                    ...user,
                    distance: distance,
                    direction: this.calculateDirection(currentLocation.location, user.location)
                });
            }
        });

        if (nearbyUsers.length > 0) {
            this.showSafetyWarning(nearbyUsers);
        }
    }

    calculateDistance(loc1, loc2) {
        // Simple distance calculation - in real app would use warehouse coordinates
        if (!loc1 || !loc2) return Infinity;
        
        // Mock distance based on zone proximity
        if (loc1.zone === loc2.zone) {
            return Math.random() * 5; // Same zone = close
        } else if (loc1.zone.charAt(0) === loc2.zone.charAt(0)) {
            return Math.random() * 15 + 5; // Same area = medium distance
        } else {
            return Math.random() * 30 + 15; // Different area = far
        }
    }

    calculateDirection(from, to) {
        const directions = ['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest'];
        return directions[Math.floor(Math.random() * directions.length)];
    }

    showSafetyWarning(nearbyUsers) {
        // Create warning overlay
        const warning = document.createElement('div');
        warning.className = 'safety-warning-overlay';
        warning.innerHTML = `
            <div class="safety-warning-content">
                <div class="warning-header">
                    ⚠️ <strong>SAFETY ALERT</strong>
                </div>
                <div class="warning-message">
                    ${nearbyUsers.length} worker(s) nearby:
                </div>
                <div class="nearby-users-list">
                    ${nearbyUsers.map(user => `
                        <div class="nearby-user">
                            👤 ${user.name} (${user.role})
                            <div class="user-details">
                                📍 ${user.location.zone} • ${user.distance.toFixed(1)}m ${user.direction}
                                ${user.status === 'navigating' ? '🚶 Moving' : '🛑 Stationary'}
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="warning-actions">
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="warning-dismiss">
                        ✓ Acknowledged
                    </button>
                </div>
            </div>
        `;

        // Add to page
        document.body.appendChild(warning);

        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            if (warning.parentElement) {
                warning.remove();
            }
        }, 10000);

        // Play warning sound
        this.playWarningSound();
    }

    playWarningSound() {
        // Create audio context for warning beep
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn("Could not play warning sound:", error);
        }
    }

    startLocationUpdates() {
        setInterval(() => {
            this.fetchNearbyUsers();
            this.checkNearbyUsers();
        }, this.updateInterval);
    }

    updateLocationDisplay(location) {
        // Update location display in navigation UI
        const locationDisplay = document.getElementById('current-location-display');
        if (locationDisplay) {
            locationDisplay.innerHTML = `
                <div class="location-info">
                    📍 Current Location: <strong>${location.zone}</strong>
                    <div class="location-details">
                        Accuracy: ±${location.accuracy ? location.accuracy.toFixed(1) + 'm' : 'Unknown'}
                        • Updated: ${new Date(location.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            `;
        }
    }

    showZoneSelector() {
        const modal = document.createElement('div');
        modal.className = 'zone-selector-modal';
        modal.innerHTML = `
            <div class="zone-selector-content">
                <h3>📍 Select Your Current Zone</h3>
                <p>GPS unavailable. Please select your warehouse zone:</p>
                <div class="zone-grid">
                    ${this.generateZoneButtons()}
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="cancel-btn">Cancel</button>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    generateZoneButtons() {
        const zones = ['A', 'B', 'C', 'D', 'E'];
        let buttons = '';
        
        zones.forEach(zone => {
            for (let aisle = 1; aisle <= 5; aisle++) {
                buttons += `
                    <button class="zone-btn" onclick="warehouseTracker.selectZone('${zone}-${aisle.toString().padStart(2, '0')}-01')">
                        ${zone}-${aisle.toString().padStart(2, '0')}
                    </button>
                `;
            }
        });
        
        return buttons;
    }

    selectZone(zone) {
        this.updateUserLocation({
            zone: zone,
            timestamp: Date.now(),
            accuracy: null,
            manual: true
        });
        
        // Close zone selector
        const modal = document.querySelector('.zone-selector-modal');
        if (modal) modal.remove();
    }

    setupSafetyWarnings() {
        // Add CSS for warning overlays
        const style = document.createElement('style');
        style.textContent = `
            .safety-warning-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: warningPulse 1s ease-in-out infinite alternate;
            }

            .safety-warning-content {
                background: linear-gradient(135deg, #ff4444, #cc0000);
                color: white;
                padding: 24px;
                border-radius: 16px;
                max-width: 400px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(255, 68, 68, 0.3);
                border: 2px solid #ff6666;
            }

            .warning-header {
                font-size: 20px;
                margin-bottom: 16px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }

            .warning-message {
                font-size: 16px;
                margin-bottom: 16px;
            }

            .nearby-users-list {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 12px;
                margin: 16px 0;
            }

            .nearby-user {
                margin: 8px 0;
                padding: 8px;
                background: rgba(16,41,67,0.1);
                border-radius: 4px;
            }

            .user-details {
                font-size: 12px;
                opacity: 0.9;
                margin-top: 4px;
            }

            .warning-dismiss {
                background: #22c55e;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                font-size: 14px;
            }

            .warning-dismiss:hover {
                background: #16a34a;
            }

            @keyframes warningPulse {
                0% { backdrop-filter: none; }
                100% { backdrop-filter: none; }
            }

            .zone-selector-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .zone-selector-content {
                background: #1e293b;
                color: white;
                padding: 24px;
                border-radius: 16px;
                max-width: 500px;
                max-height: 80vh;
                overflow-y: auto;
            }

            .zone-grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 8px;
                margin: 16px 0;
            }

            .zone-btn {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }

            .zone-btn:hover {
                background: #2563eb;
            }

            .location-info {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 8px;
                padding: 12px;
                margin: 16px 0;
                color: #f7fbff;
            }

            .location-details {
                font-size: 12px;
                opacity: 0.8;
                margin-top: 4px;
            }
        `;
        
        document.head.appendChild(style);
    }

    // Navigation integration
    startNavigation(destination) {
        this.navigationActive = true;
        console.log(`🧭 Starting navigation to ${destination}`);
        
        // Enhanced safety mode during navigation
        this.warningDistance = 15; // Increase warning distance while moving
        this.updateInterval = 1000; // More frequent updates while navigating
    }

    stopNavigation() {
        this.navigationActive = false;
        console.log("🛑 Navigation stopped");
        
        // Return to normal safety settings
        this.warningDistance = 10;
        this.updateInterval = 2000;
    }
}

// Initialize warehouse user tracking
let warehouseTracker;

document.addEventListener('DOMContentLoaded', function() {
    warehouseTracker = new WarehouseUserTracker();
    
    // Add location display to navigation interfaces
    const navigationContainers = document.querySelectorAll('.navigation-container, .scanner-container');
    navigationContainers.forEach(container => {
        const locationDisplay = document.createElement('div');
        locationDisplay.id = 'current-location-display';
        container.insertBefore(locationDisplay, container.firstChild);
    });
});

// Global functions for navigation integration
window.startWarehouseNavigation = function(destination) {
    if (warehouseTracker) {
        warehouseTracker.startNavigation(destination);
    }
};

window.stopWarehouseNavigation = function() {
    if (warehouseTracker) {
        warehouseTracker.stopNavigation();
    }
};
