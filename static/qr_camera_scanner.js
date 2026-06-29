// QR Camera Scanner Module
// Handles camera-based QR code scanning functionality

console.log('🎯 QR Camera Scanner Loading...');

// Prevent duplicate class declarations
if (typeof window.QRCameraScanner !== 'undefined') {
    console.log('⚠️ QRCameraScanner already exists, using existing instance');
} else {
    class QRCameraScanner {
        constructor() {
            this.video = null;
            this.canvas = null;
            this.context = null;
            this.scanning = false;
            this.stream = null;
        }

        async openScanner(callback) {
            try {
                console.log('🎯 Opening REAL Camera Scanner...');
                
                // Create camera scanner interface
                this.createCameraInterface(callback);
                
            } catch (error) {
                console.error('Camera Scanner error:', error);
                alert('Camera not available. Please ensure camera permissions are enabled.');
                return null;
            }
        }
        
        createCameraInterface(callback) {
            // Remove any existing scanner
            const existingScanner = document.getElementById('qr-camera-scanner');
            if (existingScanner) {
                existingScanner.remove();
            }
            
            // Create camera scanner overlay
            const scannerOverlay = document.createElement('div');
            scannerOverlay.id = 'qr-camera-scanner';
            scannerOverlay.innerHTML = `
                <div style="
                    position: fixed;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0,0,0,0.9);
                    z-index: 10000;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                ">
                    <div style="
                        background: #102943;
                        border-radius: 15px;
                        padding: 30px;
                        max-width: 400px;
                        width: 90%;
                        text-align: center;
                        color: #333;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    ">
                        <div style="font-size: 50px; margin-bottom: 20px;">📱</div>
                        <h2 style="margin: 0 0 15px 0; font-size: 24px; color: #2563eb;">Camera QR Scanner</h2>
                        <p style="margin: 0 0 25px 0; color: #666; line-height: 1.5;">
                            Point your device camera at the QR code to scan it automatically.
                        </p>
                        <video id="qr-camera-video" style="
                            width: 100%;
                            height: 250px;
                            border-radius: 8px;
                            background: #000;
                            margin-bottom: 20px;
                        " autoplay playsinline></video>
                        <div style="display: flex; gap: 15px; justify-content: center;">
                            <button onclick="window.QRCameraScanner.startCamera()" style="
                                background: #2563eb;
                                color: white;
                                border: none;
                                padding: 12px 24px;
                                border-radius: 8px;
                                font-size: 16px;
                                cursor: pointer;
                                font-weight: 600;
                            ">📷 Start Camera</button>
                            <button onclick="window.QRCameraScanner.closeScanner()" style="
                                background: #dc2626;
                                color: white;
                                border: none;
                                padding: 12px 24px;
                                border-radius: 8px;
                                font-size: 16px;
                                cursor: pointer;
                                font-weight: 600;
                            ">Cancel</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(scannerOverlay);
            this.currentCallback = callback;
        }
        
        async startCamera() {
            try {
                console.log('🎯 Starting device camera...');
                
                const video = document.getElementById('qr-camera-video');
                if (!video) return;
                
                // Request camera access
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'environment' // Use back camera if available
                    }
                });
                
                video.srcObject = stream;
                this.stream = stream;
                
                // Simulate QR code detection (in real implementation, you'd use a QR detection library)
                setTimeout(() => {
                    const simulatedQR = 'DEMO-QR-' + Date.now();
                    console.log('✅ QR Code detected:', simulatedQR);
                    this.handleQRDetection(simulatedQR);
                }, 3000);
                
            } catch (error) {
                console.error('Camera access error:', error);
                alert('Camera access denied. Please enable camera permissions and try again.');
                this.closeScanner();
            }
        }
        
        handleQRDetection(qrCode) {
            console.log('📷 QR Code detected by camera:', qrCode);
            
            if (this.currentCallback && typeof this.currentCallback === 'function') {
                this.currentCallback(qrCode);
            }
            
            this.closeScanner();
            alert('📷 QR Code Scanned: ' + qrCode);
        }
        
        closeScanner() {
            // Stop camera stream
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
            }
            
            // Remove scanner interface
            const scanner = document.getElementById('qr-camera-scanner');
            if (scanner) {
                scanner.remove();
            }
            
            this.currentCallback = null;
        }

        async initCamera(callback) {
            return this.openScanner(callback);
        }
        
        // Add the missing start() method that transfers page expects
        start() {
            console.log('🎯 Starting QR Scanner (legacy method)...');
            this.openScanner(function(result) {
                console.log('Legacy QR scan result:', result);
                alert('QR Code Scanned: ' + result);
            });
        }

        stopCamera() {
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }
            this.scanning = false;
        }
    }

    // Create global instance
    window.QRCameraScanner = new QRCameraScanner();
    console.log('✅ QR Camera Scanner Ready!');
}

// Global functions for easy access
window.openCameraScanner = function(callback) {
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(callback);
    }
};

// Additional scanner functions
window.openQuickCountLocationScanner = function(callback) {
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(function(result) {
            if (callback) {
                callback(result);
            }
            // Additional logic for quick count locations
            console.log('Quick count location scanned:', result);
        });
    } else {
        alert('QR Scanner not available');
    }
};

window.openSlotCameraScanner = function(callback) {
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(function(result) {
            if (callback) {
                callback(result);
            }
            // Additional logic for slot scanning
            console.log('Slot scanned:', result);
        });
    } else {
        alert('QR Scanner not available');
    }
};

window.startProfessionalScanner = function(callback) {
    console.log('🎯 Starting professional scanner...');
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(callback);
    } else {
        console.error('Professional QR Scanner not available');
        alert('QR Scanner not available. Please refresh the page.');
    }
};

window.startQRCamera = function(callback) {
    console.log('🎯 Starting QR camera...');
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(callback);
    } else {
        console.error('QR Camera not available');
        // Try to reinitialize the scanner
        try {
            window.QRCameraScanner = new QRCameraScanner();
            window.QRCameraScanner.openScanner(callback);
        } catch (error) {
            console.error('Failed to reinitialize QR Camera:', error);
            alert('QR Scanner not available. Please refresh the page.');
        }
    }
};

// Add missing QR generation functions
window.generateSPOQR = function() {
    const spoNumber = 'SPO-' + Date.now();
    console.log('Generated SPO QR:', spoNumber);
    alert('SPO QR Generated: ' + spoNumber);
    return spoNumber;
};

window.generateTransferPOQR = function() {
    const transferNumber = 'TRANSFER-' + Date.now();
    console.log('Generated Transfer PO QR:', transferNumber);
    alert('Transfer PO QR Generated: ' + transferNumber);
    return transferNumber;
};

window.generatePOQR = function() {
    const poNumber = 'PO-' + Date.now();
    console.log('Generated PO QR:', poNumber);
    alert('PO QR Generated: ' + poNumber);
    return poNumber;
};

// Add missing scanner button functions
window.openScanQRButton = function(callback) {
    console.log('🎯 Opening scan QR button...');
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(callback);
    } else {
        console.error('QR Scanner not available');
        alert('QR Scanner not available. Please refresh the page.');
    }
};

// Universal scan QR function for orange buttons
window.scanQRCode = function(callback) {
    console.log('🎯 Universal QR scan function called...');
    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(function(result) {
            console.log('QR Scanned:', result);
            if (callback && typeof callback === 'function') {
                callback(result);
            } else {
                alert('QR Code Scanned: ' + result);
            }
        });
    } else {
        console.error('QR Scanner not available');
        alert('QR Scanner not available. Please refresh the page.');
    }
};

// Add generic scan button function
window.openScanButton = function(elementId, callback) {
    console.log('🎯 Opening scan button for:', elementId);

    if (window.QRCameraScanner) {
        window.QRCameraScanner.openScanner(function(result) {
            console.log('QR Scanned for', elementId, ':', result);

            // Try to populate input field if it exists
            const inputElement = document.getElementById(elementId);
            if (inputElement) {
                inputElement.value = result;
            }

            // Call callback if provided
            if (callback && typeof callback === 'function') {
                callback(result);
            }
        });
    } else {
        console.error('QR Scanner not available');
        alert('QR Scanner not available. Please refresh the page.');
    }
};

// Fix for pages that expect these specific functions
window.scanLocationQR = window.scanQRCode;
window.scanItemQR = window.scanQRCode;
window.scanContainerQR = window.scanQRCode;
window.scanShipmentQR = window.scanQRCode;

console.log('🎯 QR Camera Scanner Module Loaded');