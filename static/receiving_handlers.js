// Receiving Page Button Handlers
// Mobile Safari Compatible - All functions attached to window object

(function() {
    'use strict';
    
    console.log('Loading receiving handlers...');

    window.startQRScan = function() {
        if (typeof QRCameraScanner !== 'undefined' && QRCameraScanner.openScanner) {
            QRCameraScanner.openScanner(function(qrData) {
                var trackingInput = document.getElementById('trackingInput');
                if (trackingInput) trackingInput.value = qrData;
                alert('QR Code Scanned: ' + qrData);
            });
        } else {
            alert('QR Scanner not available. Please refresh the page.');
        }
    };

    window.testQRCameraScanner = function() {
        if (typeof QRCameraScanner !== 'undefined') {
            alert('QR Camera Scanner is working!');
            QRCameraScanner.openScanner(function(result) {
                alert('Scan result: ' + result);
            });
        } else {
            alert('QR Camera Scanner not found.');
        }
    };

    window.manualEntry = function() {
        var trackingInput = document.getElementById('trackingInput');
        if (trackingInput) {
            trackingInput.focus();
            alert('Enter tracking number in the input field.');
        } else {
            var input = prompt('Enter tracking number:');
            if (input) alert('Manual entry: ' + input);
        }
    };

    window.scanPOForReceiving = function() {
        if (typeof QRCameraScanner !== 'undefined' && QRCameraScanner.openScanner) {
            QRCameraScanner.openScanner(function(scannedData) {
                console.log('PO QR Scanned:', scannedData);
                if (scannedData && scannedData.indexOf('PO_RECEIVING:') === 0) {
                    var poId = scannedData.replace('PO_RECEIVING:', '').trim();
                    window.loadPOForReceiving(poId);
                } else if (scannedData && scannedData.indexOf('PO-') === 0) {
                    window.loadPOForReceiving(scannedData.trim());
                } else {
                    alert('Scanned: ' + scannedData + '\n\nExpected: PO-XXXX format');
                }
            });
        } else {
            var poId = prompt('Enter PO Number:');
            if (poId && poId.trim()) window.loadPOForReceiving(poId.trim());
        }
    };

    window.loadPOList = function() {
        fetch('/api/purchase-orders')
            .then(function(r) { 
                if (!r.ok) throw new Error('Failed to load POs');
                return r.json(); 
            })
            .then(function(data) {
                var pos = data.purchase_orders || [];
                var selector = document.getElementById('po-selector');
                var listSection = document.getElementById('po-list-selector');
                if (selector && listSection) {
                    selector.innerHTML = '<option value="">-- Select PO --</option>';
                    var count = 0;
                    pos.forEach(function(po) {
                        if (po.status === 'pending' || po.status === 'approved' || po.status === 'shipped') {
                            var opt = document.createElement('option');
                            opt.value = po.po_id || po.id;
                            opt.textContent = (po.po_id || po.id) + ' - ' + (po.supplier || 'Unknown');
                            selector.appendChild(opt);
                            count++;
                        }
                    });
                    listSection.style.display = 'block';
                    alert('Found ' + count + ' available POs');
                }
            })
            .catch(function(e) { 
                console.error('Load PO List error:', e);
                alert('Error: ' + e.message); 
            });
    };

    window.loadPOForReceiving = function(poId) {
        if (!poId) { 
            alert('No PO ID provided'); 
            return; 
        }
        fetch('/api/purchase-orders/' + encodeURIComponent(poId))
            .then(function(r) { 
                if (!r.ok) throw new Error('PO not found');
                return r.json(); 
            })
            .then(function(data) {
                var po = data.purchase_order;
                if (po) {
                    var headerEl = document.getElementById('po-header');
                    var supplierEl = document.getElementById('po-supplier');
                    var infoEl = document.getElementById('current-po-info');
                    if (headerEl) headerEl.textContent = 'PO: ' + (po.id || po.po_id);
                    if (supplierEl) supplierEl.textContent = 'Supplier: ' + (po.supplier || 'Unknown');
                    if (infoEl) infoEl.style.display = 'block';
                    alert('Loaded PO: ' + (po.id || po.po_id) + '\nSupplier: ' + (po.supplier || 'Unknown'));
                } else {
                    alert('PO not found: ' + poId);
                }
            })
            .catch(function(e) { 
                console.error('Error loading PO:', e);
                alert('Error: ' + e.message); 
            });
    };

    // QR Code Generation Functions
    window.generatePOQRInline = function() {
        var poNumber = document.getElementById('poNumber').value.trim() || 'PO-' + Date.now();
        var supplier = document.getElementById('poSupplier').value.trim() || 'Default Supplier';
        
        document.getElementById('poNumber').value = poNumber;
        console.log('Generating PO QR:', poNumber);
        
        var displayArea = document.getElementById('po-qr-display');
        displayArea.style.display = 'block';
        displayArea.innerHTML = '<div style="background: white; border: 2px solid #3b82f6; border-radius: 12px; padding: 20px; text-align: center; margin-top: 15px;">' +
            '<h4 style="margin: 0 0 15px 0; color: #1f2937;">Purchase Order: ' + poNumber + '</h4>' +
            '<div id="po-qr-container" style="display: flex; justify-content: center; padding: 15px; background: #f9fafb; border-radius: 8px;">' +
            '<div style="padding: 20px;">Generating QR Code...</div></div>' +
            '<p style="color: #6b7280; font-size: 12px; margin: 10px 0;">Supplier: ' + supplier + '</p></div>';
        
        fetch('/api/generate_qr', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: poNumber, size: 200 })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success && data.qr_image) {
                var container = document.getElementById('po-qr-container');
                container.innerHTML = '<img src="' + data.qr_image + '" style="max-width: 200px; border-radius: 8px;">' +
                    '<div style="margin-top: 15px;">' +
                    '<button onclick="window.closePOQRDisplay()" style="background: #ef4444; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer;">Close</button></div>';
                alert('QR Code generated for: ' + poNumber);
            } else {
                alert('Failed to generate QR code');
            }
        })
        .catch(function(e) { 
            console.error('QR generation error:', e);
            alert('Error generating QR: ' + e.message); 
        });
    };

    window.generateSPOQRInline = function() {
        var spoNumber = document.getElementById('spoNumber').value.trim() || 'SPO-' + Date.now();
        var priority = document.getElementById('spoPriority').value || 'Medium';
        
        document.getElementById('spoNumber').value = spoNumber;
        console.log('Generating SPO QR:', spoNumber);
        
        var displayArea = document.getElementById('spo-qr-display');
        displayArea.style.display = 'block';
        displayArea.innerHTML = '<div style="background: white; border: 2px solid #f59e0b; border-radius: 12px; padding: 20px; text-align: center; margin-top: 15px;">' +
            '<h4 style="margin: 0 0 15px 0; color: #1f2937;">Special Purchase Order: ' + spoNumber + '</h4>' +
            '<div id="spo-qr-container" style="display: flex; justify-content: center; padding: 15px; background: #f9fafb; border-radius: 8px;">' +
            '<div style="padding: 20px;">Generating QR Code...</div></div>' +
            '<p style="color: #6b7280; font-size: 12px; margin: 10px 0;">Priority: ' + priority + '</p></div>';
        
        fetch('/api/generate_qr', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: spoNumber, size: 200 })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success && data.qr_image) {
                var container = document.getElementById('spo-qr-container');
                container.innerHTML = '<img src="' + data.qr_image + '" style="max-width: 200px; border-radius: 8px;">' +
                    '<div style="margin-top: 15px;">' +
                    '<button onclick="window.closeSPOQRDisplay()" style="background: #ef4444; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer;">Close</button></div>';
                alert('QR Code generated for: ' + spoNumber);
            } else {
                alert('Failed to generate QR code');
            }
        })
        .catch(function(e) { alert('Error: ' + e.message); });
    };

    window.generateTransferPOQRInline = function() {
        var transferNumber = document.getElementById('transferPoNumber').value.trim() || 'XFR-' + Date.now();
        var transferType = document.getElementById('transferType').value || 'XFR';
        
        document.getElementById('transferPoNumber').value = transferNumber;
        console.log('Generating Transfer QR:', transferNumber);
        
        var displayArea = document.getElementById('transfer-qr-display');
        displayArea.style.display = 'block';
        displayArea.innerHTML = '<div style="background: white; border: 2px solid #6366f1; border-radius: 12px; padding: 20px; text-align: center; margin-top: 15px;">' +
            '<h4 style="margin: 0 0 15px 0; color: #1f2937;">Transfer: ' + transferNumber + '</h4>' +
            '<div id="transfer-qr-container" style="display: flex; justify-content: center; padding: 15px; background: #f9fafb; border-radius: 8px;">' +
            '<div style="padding: 20px;">Generating QR Code...</div></div>' +
            '<p style="color: #6b7280; font-size: 12px; margin: 10px 0;">Type: ' + transferType + '</p></div>';
        
        fetch('/api/generate_qr', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: transferNumber, size: 200 })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success && data.qr_image) {
                var container = document.getElementById('transfer-qr-container');
                container.innerHTML = '<img src="' + data.qr_image + '" style="max-width: 200px; border-radius: 8px;">' +
                    '<div style="margin-top: 15px;">' +
                    '<button onclick="window.closeTransferQRDisplay()" style="background: #ef4444; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer;">Close</button></div>';
                alert('QR Code generated for: ' + transferNumber);
            } else {
                alert('Failed to generate QR code');
            }
        })
        .catch(function(e) { alert('Error: ' + e.message); });
    };

    // Close functions
    window.closePOQRDisplay = function() {
        var el = document.getElementById('po-qr-display');
        if (el) el.style.display = 'none';
    };

    window.closeSPOQRDisplay = function() {
        var el = document.getElementById('spo-qr-display');
        if (el) el.style.display = 'none';
    };

    window.closeTransferQRDisplay = function() {
        var el = document.getElementById('transfer-qr-display');
        if (el) el.style.display = 'none';
    };

    // Print functions
    window.printPO = function() {
        var poNumber = document.getElementById('poNumber').value.trim();
        if (!poNumber) {
            alert('Please enter a PO number first');
            return;
        }
        alert('Print PO: ' + poNumber + '\n\nPrint functionality will open your browser print dialog.');
        window.print();
    };

    window.printSPO = function() {
        var spoNumber = document.getElementById('spoNumber').value.trim();
        if (!spoNumber) {
            alert('Please enter an SPO number first');
            return;
        }
        alert('Print SPO: ' + spoNumber);
        window.print();
    };

    window.printTransferPO = function() {
        var transferNumber = document.getElementById('transferPoNumber').value.trim();
        if (!transferNumber) {
            alert('Please enter a transfer number first');
            return;
        }
        alert('Print Transfer: ' + transferNumber);
        window.print();
    };

    console.log('Receiving handlers loaded successfully');
})();
