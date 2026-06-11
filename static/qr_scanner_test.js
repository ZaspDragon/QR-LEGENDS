
// QR Scanner Test Utility
console.log('🧪 QR Scanner Test Utility Loading...');

function testQRScanner() {
    console.log('🧪 Testing QR Scanner Components...');
    
    // Test 1: Check if QRCameraScanner exists
    const hasQRCameraScanner = typeof window.QRCameraScanner !== 'undefined';
    console.log(`📱 QRCameraScanner: ${hasQRCameraScanner ? 'Available' : 'Missing'}`);
    
    // Test 2: Check global functions
    const hasStartQRCamera = typeof window.startQRCamera === 'function';
    console.log(`📷 startQRCamera: ${hasStartQRCamera ? 'Available' : 'Missing'}`);
    
    // Test 3: Check scanner modal
    const scannerModal = document.getElementById('qr-scanner-modal');
    console.log(`🎯 Scanner Modal: ${scannerModal ? 'Found' : 'Not Found'}`);
    
    // Test 4: Test camera permissions
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        console.log('📹 Camera API: Available');
        
        // Test camera access
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                console.log('✅ Camera permission granted');
                stream.getTracks().forEach(track => track.stop());
            })
            .catch(error => {
                console.log('❌ Camera permission denied or no camera:', error.message);
            });
    } else {
        console.log('❌ Camera API not available');
    }
    
    // Overall status
    const isWorking = hasQRCameraScanner && hasStartQRCamera;
    console.log(`🔍 QR Scanner Status: ${isWorking ? '✅ Working' : '❌ Issues Detected'}`);
    
    return {
        hasQRCameraScanner,
        hasStartQRCamera,
        hasModal: !!scannerModal,
        hasCameraAPI: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        isWorking
    };
}

// Auto-test on load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(testQRScanner, 1000);
});

// Make test function globally available
window.testQRScanner = testQRScanner;

console.log('🧪 QR Scanner Test Utility Ready!');
