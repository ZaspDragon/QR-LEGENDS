// Universal QR Button Fixer - Ensures all QR buttons work across all pages
console.log('🔧 QR Button Fixer Loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Fixing QR buttons across the page...');

    // Wait for QR Camera Scanner to load
    let retryCount = 0;
    const maxRetries = 10;

    function ensureQRScanner() {
        if (window.QRCameraScanner) {
            console.log('✅ QR Camera Scanner found, fixing buttons...');
            fixAllQRButtons();
        } else if (retryCount < maxRetries) {
            retryCount++;
            console.log(`⏳ Waiting for QR Scanner... (${retryCount}/${maxRetries})`);
            setTimeout(ensureQRScanner, 500);
        } else {
            console.log('❌ QR Scanner not available, creating fallback...');
            createFallbackScanner();
            fixAllQRButtons();
        }
    }

    ensureQRScanner();
});

function createFallbackScanner() {
    window.QRCameraScanner = {
        openScanner: function(callback) {
            const mockQR = prompt('QR Scanner not available. Enter QR data manually:');
            if (mockQR && callback) {
                callback(mockQR);
            }
        }
    };
    console.log('📱 Fallback QR Scanner created');
}

function fixAllQRButtons() {
    console.log('🔧 Starting QR button fixes...');

    // Fix all orange scan buttons
    const orangeButtons = document.querySelectorAll('button[style*="background: #ff6b35"], button[style*="background:#ff6b35"], .scan-btn, .orange-btn');
    orangeButtons.forEach(button => {
        if (button.textContent.includes('Scan') || button.textContent.includes('📷')) {
            fixScanButton(button);
        }
    });

    // Fix buttons by common text patterns
    const scanButtons = document.querySelectorAll('button');
    scanButtons.forEach(button => {
        const text = button.textContent.toLowerCase();
        if (text.includes('scan qr') || text.includes('📷') || text.includes('camera') || text.includes('scanner')) {
            fixScanButton(button);
        }
    });

    // Fix buttons with specific onclick functions
    fixSpecificButtons();

    // Fix generate buttons
    fixGenerateButtons();

    console.log('✅ QR button fixes applied');
}

function fixScanButton(button) {
    // Remove existing event listeners
    const newButton = button.cloneNode(true);
    button.parentNode.replaceChild(newButton, button);

    // Add universal QR scanner
    newButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        console.log('🎯 QR Scan button clicked');

        if (window.QRCameraScanner) {
            window.QRCameraScanner.openScanner(function(result) {
                console.log('📱 QR Scanned:', result);

                // Try to find related input field
                const parentForm = newButton.closest('form') || newButton.closest('.form-group') || newButton.closest('div');
                if (parentForm) {
                    const inputs = parentForm.querySelectorAll('input[type="text"], input[type="number"], textarea');
                    if (inputs.length > 0) {
                        inputs[0].value = result;
                        inputs[0].focus();
                    }
                }

                alert(`QR Code Scanned: ${result}`);
            });
        } else {
            console.error('QR Scanner not available');
            alert('QR Scanner not available. Please refresh the page.');
        }
    });

    // Ensure button is visible and styled properly
    if (!newButton.style.background || newButton.style.background === 'none') {
        newButton.style.background = '#ff6b35';
        newButton.style.color = 'white';
        newButton.style.border = 'none';
        newButton.style.borderRadius = '8px';
        newButton.style.padding = '8px 16px';
        newButton.style.cursor = 'pointer';
    }
}

function fixSpecificButtons() {
    // Fix buttons with specific IDs or classes
    const buttonSelectors = [
        '#scanLocationBtn',
        '#scanItemBtn', 
        '#scanContainerBtn',
        '#scanPOBtn',
        '#scanTransferBtn',
        '.scan-location-btn',
        '.scan-item-btn',
        '.scan-container-btn',
        '.scan-po-btn'
    ];

    buttonSelectors.forEach(selector => {
        const buttons = document.querySelectorAll(selector);
        buttons.forEach(button => fixScanButton(button));
    });
}

function fixGenerateButtons() {
    console.log('🔧 Fixing generate buttons...');

    // Fix Generate PO QR Code buttons
    const generatePOButtons = document.querySelectorAll('button');
    generatePOButtons.forEach(button => {
        const text = button.textContent;
        if (text.includes('Generate PO QR') || text.includes('Generate Purchase Order QR')) {
            button.onclick = function(e) {
                e.preventDefault();
                generatePOQRCode();
            };
        } else if (text.includes('Generate SPO QR') || text.includes('Generate Special Purchase Order QR')) {
            button.onclick = function(e) {
                e.preventDefault();
                generateSPOQRCode();
            };
        } else if (text.includes('Generate Transfer') && text.includes('QR')) {
            button.onclick = function(e) {
                e.preventDefault();
                generateTransferPOQR();
            };
        } else if (text.includes('Generate') && text.includes('QR')) {
            button.onclick = function(e) {
                e.preventDefault();
                generateGenericQR();
            };
        }
    });
}

// QR Generation Functions
async function generatePOQRCode() {
    try {
        console.log('🔄 Generating Purchase Order QR...');

        const response = await fetch('/api/qr/purchase-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                po_number: `PO-${Date.now()}`,
                supplier: 'Demo Supplier',
                priority: 'Normal'
            })
        });

        const data = await response.json();

        if (data.success) {
            console.log('✅ PO QR generated:', data.po_number);
            displayGeneratedQR(data.qr_image, `Purchase Order: ${data.po_number}`);
        } else {
            console.error('❌ Failed to generate PO QR:', data.error);
            showError('Failed to generate Purchase Order QR code');
        }
    } catch (error) {
        console.error('❌ PO QR generation error:', error);
        showError('Error generating Purchase Order QR code');
    }
}

async function generateSPOQRCode() {
    try {
        const spoInput = document.querySelector('input[placeholder*="SPO"], input[name*="spo"], #spoNumber, #spo_number');
        const spoNumber = spoInput?.value || prompt('Enter SPO Number:') || `SPO-${Date.now()}`;

        const response = await fetch('/api/qr/special-purchase-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                spo_number: spoNumber,
                priority: 'High'
            })
        });

        const result = await response.json();
        if (result.success) {
            displayGeneratedQR(result.qr_image, `SPO: ${result.spo_number}`);
        } else {
            alert('Error generating SPO QR: ' + result.error);
        }
    } catch (error) {
        console.error('Error generating SPO QR:', error);
        alert('Error generating SPO QR code');
    }
}

async function generateTransferPOQR() {
    try {
        const transferInput = document.querySelector('input[placeholder*="Transfer"], input[name*="transfer"], #transferNumber, #transfer_number');
        const transferNumber = transferInput?.value || prompt('Enter Transfer Number:') || `XFR-${Date.now()}`;

        const response = await fetch('/api/qr/transfer-purchase-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                transfer_number: transferNumber,
                transfer_type: 'Standard Transfer'
            })
        });

        const result = await response.json();
        if (result.success) {
            displayGeneratedQR(result.qr_image, `Transfer: ${result.transfer_number}`);
        } else {
            alert('Error generating Transfer QR: ' + result.error);
        }
    } catch (error) {
        console.error('Error generating Transfer QR:', error);
        alert('Error generating Transfer QR code');
    }
}

async function generateGenericQR() {
    try {
        console.log('🔄 Generating Generic QR...');

        const response = await fetch('/api/qr/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                qr_data: `GENERIC-${Date.now()}`,
                type: 'generic'
            })
        });

        const data = await response.json();

        if (data.success) {
            console.log('✅ Generic QR generated');
            displayGeneratedQR(data.qr_image, `QR Code: ${data.qr_data}`);
        } else {
            console.error('❌ Failed to generate Generic QR:', data.error);
            showError('Failed to generate QR code');
        }
    } catch (error) {
        console.error('❌ Generic QR generation error:', error);
        showError('Error generating QR code');
    }
}

function displayGeneratedQR(qrImage, label) {
    console.log('📊 Displaying QR:', label);

    // Remove any existing QR displays
    const existingDisplays = document.querySelectorAll('.qr-display, #qr-display, .qr-result');
    existingDisplays.forEach(display => display.remove());

    // Create new display area
    const displayArea = document.createElement('div');
    displayArea.className = 'qr-display generated-qr-display';
    displayArea.id = 'current-qr-display';
    displayArea.style.cssText = `
        background: white;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin: 25px auto;
        max-width: 450px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 3px solid #3b82f6;
        position: relative;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    // Add animation styles
    if (!document.querySelector('#qr-display-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'qr-display-styles';
        styleSheet.textContent = `
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .qr-btn {
                background: #10b981;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                margin: 8px;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .qr-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .qr-btn.print { background: #10b981; }
            .qr-btn.download { background: #3b82f6; }
            .qr-btn.close { background: #ef4444; }
        `;
        document.head.appendChild(styleSheet);
    }

    const qrId = `qr_${Date.now()}`;
    const escapedImage = qrImage.replace(/'/g, "\\'");
    const escapedLabel = label.replace(/'/g, "\\'");

    displayArea.innerHTML = `
        <div style="border-bottom: 2px solid #e5e7eb; padding-bottom: 15px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #1f2937; font-size: 20px;">QR LEGENDS</h3>
            <h4 style="margin: 5px 0; color: #374151;">${label}</h4>
        </div>
        <div style="background: #f9fafb; padding: 20px; border-radius: 12px; margin: 15px 0;">
            <img id="${qrId}" src="${qrImage}" alt="Generated QR Code" style="max-width: 280px; margin: 10px 0; border: 2px solid #d1d5db; border-radius: 8px;">
        </div>
        <div style="color: #6b7280; font-size: 12px; margin: 10px 0;">
            Generated: ${new Date().toLocaleString()}<br>
            Scan for current data
        </div>
        <div style="margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 15px;">
            <button class="qr-btn print" onclick="printQRCode('${escapedImage}', '${escapedLabel}')">
                🖨️ Print QR
            </button>
            <button class="qr-btn download" onclick="downloadQRCode('${escapedImage}', '${escapedLabel}')">
                💾 Download
            </button>
            <button class="qr-btn close" onclick="closeQRDisplay()">
                ✖️ Close
            </button>
        </div>
    `;

    // Insert into the page
    const targetContainer = document.querySelector('.container, .main-content, .content') || document.body;
    targetContainer.appendChild(displayArea);

    // Scroll to QR display
    displayArea.scrollIntoView({ behavior: 'smooth', block: 'center' });

    console.log('✅ QR displayed with working print button');
}

function displayQRCode(qrData, qrImage, containerId = 'qr-display') {
    let container = document.getElementById(containerId);
    if (!container) {
        container = document.createElement('div');
        container.id = containerId;
        container.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            text-align: center;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }

    container.innerHTML = `
        <div style="margin-bottom: 15px;">
            <h3 style="margin: 0 0 10px 0; color: #333;">QR Code Generated</h3>
            <p style="margin: 0; color: #666; font-size: 14px;">${qrData}</p>
        </div>
        <div style="margin: 20px 0;">
            <img id="current-qr-image" src="${qrImage}" style="max-width: 200px; height: auto; border: 2px solid #ddd; border-radius: 5px;" />
        </div>
        <div style="display: flex; gap: 10px; justify-content: center;">
            <button onclick="printCurrentQRCode()" style="
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
            ">🖨️ Print</button>
            <button onclick="document.getElementById('${containerId}').remove()" style="
                background: #6b7280;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
            ">Close</button>
        </div>
    `;

    // Store current QR data globally for printing
    window.currentQRData = qrData;
    window.currentQRImage = qrImage;

    console.log('✅ QR Code displayed successfully');
}

function printCurrentQRCode() {
    if (!window.currentQRImage || !window.currentQRData) {
        console.error('❌ No QR code to print');
        return;
    }

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>QR Code - ${window.currentQRData}</title>
                <style>
                    body { text-align: center; font-family: Arial, sans-serif; margin: 40px; }
                    .qr-container { border: 2px solid #000; padding: 20px; display: inline-block; }
                    img { display: block; margin: 20px auto; max-width: 300px; }
                    .qr-data { font-size: 12px; margin-top: 10px; word-break: break-all; max-width: 300px; }
                </style>
            </head>
            <body>
                <div class="qr-container">
                    <h2>QR Code</h2>
                    <img src="${window.currentQRImage}" />
                    <div class="qr-data">${window.currentQRData}</div>
                </div>
                <script>
                    window.onload = function() {
                        window.print();
                        window.close();
                    }
                </script>
            </body>
        </html>
    `);
    printWindow.document.close();

    console.log('🖨️ Print window opened');
}

function printQR(qrImage, label) {
    try {
        console.log('🖨️ Printing QR:', label);

        const printWindow = window.open('', '_blank', 'width=600,height=400');

        if (!printWindow) {
            alert('Pop-up blocked. Please allow pop-ups for printing.');
            return;
        }

        printWindow.document.write(`
            <html>
            <head>
                <title>Print ${label}</title>
                <style>
                    @page {
                        size: A4;
                        margin: 0.5in;
                    }
                    body { 
                        text-align: center; 
                        padding: 20px; 
                        font-family: Arial, sans-serif;
                        background: white;
                        color: black;
                    }
                    h2 { 
                        margin-bottom: 20px; 
                        color: #333;
                        font-size: 24px;
                    }
                    img { 
                        margin: 20px 0; 
                        max-width: 300px;
                        border: 2px solid #333;
                        padding: 10px;
                    }
                    .label-info {
                        font-size: 14px;
                        margin: 10px 0;
                        color: #666;
                    }
                    .qr-container {
                        border: 3px solid #000;
                        padding: 20px;
                        margin: 20px auto;
                        max-width: 400px;
                        background: white;
                    }
                    @media print {
                        body { margin: 0; }
                        .qr-container { 
                            page-break-inside: avoid;
                            margin: 0 auto;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="qr-container">
                    <h2>QR LEGENDS</h2>
                    <h3>${label}</h3>
                    <img src="${qrImage}" alt="QR Code">
                    <div class="label-info">
                        Generated: ${new Date().toLocaleString()}<br>
                        Scan for current data
                    </div>
                </div>
            </body>
            </html>
        `);

        printWindow.document.close();

        // Wait for content to load then print
        printWindow.onload = function() {
            setTimeout(function() {
                printWindow.focus();
                printWindow.print();
                // Don't auto-close, let user close manually
            }, 1000);
        };

    } catch (error) {
        console.error('Print error:', error);
        alert('Print failed. Please try again or save the QR code image manually.');
    }
}

function downloadQR(qrImage, label) {
    try {
        const link = document.createElement('a');
        link.href = qrImage;
        link.download = `${label.replace(/[^a-zA-Z0-9]/g, '_')}.png`;
        link.click();
        console.log(`💾 Downloaded QR: ${label}`);
    } catch (error) {
        console.error('Download error:', error);
        alert('Download failed. Please right-click the QR code and save manually.');
    }
}

// Enhanced print and download functions
function printQRCode(qrImage, label) {
    try {
        console.log('🖨️ Printing QR Code:', label);

        const printWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');

        if (!printWindow) {
            alert('Pop-up blocked! Please allow pop-ups to print QR codes.');
            return;
        }

        const printContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Print QR Code - ${label}</title>
                <style>
                    @page {
                        size: A4;
                        margin: 0.75in;
                    }
                    body {
                        font-family: 'Arial', sans-serif;
                        background: white;
                        color: black;
                        margin: 0;
                        padding: 20px;
                        text-align: center;
                    }
                    .qr-label {
                        border: 3px solid #000;
                        padding: 30px;
                        margin: 20px auto;
                        max-width: 500px;
                        background: white;
                        page-break-inside: avoid;
                    }
                    .qr-title {
                        font-size: 28px;
                        font-weight: bold;
                        margin-bottom: 10px;
                        color: #000;
                    }
                    .qr-subtitle {
                        font-size: 20px;
                        margin-bottom: 20px;
                        color: #333;
                    }
                    .qr-image {
                        margin: 20px 0;
                        border: 2px solid #ccc;
                        padding: 15px;
                        background: white;
                    }
                    .qr-info {
                        font-size: 14px;
                        margin-top: 15px;
                        color: #666;
                        line-height: 1.4;
                    }
                    @media print {
                        body { margin: 0; padding: 10px; }
                        .qr-label { margin: 10px auto; }
                    }
                </style>
            </head>
            <body>
                <div class="qr-label">
                    <div class="qr-title">QR LEGENDS</div>
                    <div class="qr-subtitle">${label}</div>
                    <div class="qr-image">
                        <img src="${qrImage}" style="max-width: 250px; height: auto;" alt="QR Code">
                    </div>
                    <div class="qr-info">
                        Generated: ${new Date().toLocaleString()}<br>
                        Scan with QR Legends app for live data<br>
                        QR Legends Warehouse Management System
                    </div>
                </div>
            </body>
            </html>
        `;

        printWindow.document.write(printContent);
        printWindow.document.close();

        // Enhanced print handling
        printWindow.onload = function() {
            setTimeout(function() {
                printWindow.focus();
                printWindow.print();

                // Handle print dialog events
                printWindow.onafterprint = function() {
                    console.log('✅ Print completed');
                };

                printWindow.onbeforeprint = function() {
                    console.log('🖨️ Print dialog opened');
                };

            }, 800);
        };

        // Fallback for browsers that don't support onload properly
        setTimeout(function() {
            if (printWindow && !printWindow.closed) {
                printWindow.focus();
                printWindow.print();
            }
        }, 1500);

    } catch (error) {
        console.error('Print error:', error);
        alert('Print failed. Please save the QR code image and print manually.');
    }
}

function downloadQRCode(qrImage, label) {
    try {
        console.log('💾 Downloading QR Code:', label);

        // Create download link
        const link = document.createElement('a');
        link.href = qrImage;
        link.download = `QR_${label.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}.png`;

        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log('✅ QR Code download triggered');

        // Show success message
        const successMsg = document.createElement('div');
        successMsg.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-weight: 600;
        `;
        successMsg.textContent = '✅ QR Code downloaded!';
        document.body.appendChild(successMsg);

        setTimeout(() => {
            successMsg.remove();
        }, 3000);

    } catch (error) {
        console.error('Download error:', error);
        alert('Download failed. Please right-click the QR code image and save manually.');
    }
}

function closeQRDisplay() {
    const displays = document.querySelectorAll('.qr-display, #current-qr-display');
    displays.forEach(display => {
        display.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => display.remove(), 300);
    });
}

// Add slideOut animation
if (!document.querySelector('#qr-close-styles')) {
    const closeStyles = document.createElement('style');
    closeStyles.id = 'qr-close-styles';
    closeStyles.textContent = `
        @keyframes slideOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-20px); }
        }
    `;
    document.head.appendChild(closeStyles);
}

// Add global QR generation functions
window.generatePOQRCode = generatePOQRCode;
window.generateSPOQRCode = generateSPOQRCode;
window.generateTransferPOQR = generateTransferPOQR;
window.generateGenericQR = generateGenericQR;
window.printQRCode = printQRCode;
window.downloadQRCode = downloadQRCode;
window.closeQRDisplay = closeQRDisplay;

// Legacy compatibility functions
window.generatePOQR = generatePOQRCode;
window.generateSPOQR = generateSPOQRCode;
window.printQR = printQRCode;
window.downloadQR = downloadQR;

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        padding: 12px 16px;
        border-radius: 6px;
        z-index: 10001;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 3000);
}

function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #22c55e;
        color: white;
        padding: 12px 16px;
        border-radius: 6px;
        z-index: 10001;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);

    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 3000);
}

console.log('✅ QR Button Fixer Ready with Enhanced Print!');