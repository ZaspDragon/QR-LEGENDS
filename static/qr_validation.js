class QRValidator {
    static async validateQR(qrData, expectedType = 'any', department = 'general') {
        try {
            const response = await fetch('/api/qr/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    qr_data: qrData,
                    expected_type: expectedType,
                    department: department});});

            const result = await response.json();
            return result;
        } catch (error) {console.error('QR validation error:', error)
            return {
                success: false,
                message: 'QR validation failed'};
        }
    }

    static showErrorMessage(result, container = document.body, position = 'top') {const errorDiv = document.createElement('div')
        errorDiv.className = 'qr-validation-error'

        // Determine error styling based on position
        let positionStyle = ''
        if (position === 'top') {
            positionStyle = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 1000;'} else if (position === 'inline') {positionStyle = 'position: relative margin: 15px 0'}

        errorDiv.style.cssText = `
            ${positionStyle}
            background-color: #f8d7da;
            border: 2px solid #dc3545;
            color: #721c24;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 500px;
            animation: errorPulse 0.5s ease-out;
        `;

        // Get appropriate icon and title
        const {icon, title} = this.getErrorDisplay(result.error_type);

        errorDiv.innerHTML = `
            <div style="text-align: center;">
                <h4 style="margin: 0 0 10px 0;">${icon} ${title}</h4>
                <p style="margin: 0 0 10px 0; font-weight: bold;">${result.message}</p>
                <p style="margin: 0 0 15px 0; font-size: 0.9em; opacity: 0.8;">
                    ${this.getHelpText(result.error_type, result.department)}
                </p>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Dismiss
                </button>
            </div>
        `;

        // Add CSS animation
        if (!document.getElementById('qr-error-styles')) {const style = document.createElement('style')
            style.id = 'qr-error-styles'
            style.textContent = `
                @keyframes errorPulse {
                    0% { transform: scale(0.8) opacity: 0}
                    50% {transform: scale(1.05)}
                    100% {transform: scale(1) opacity: 1}
                }
            `;
            document.head.appendChild(style);
        }

        container.appendChild(errorDiv);

        // Auto-remove after 8 seconds
        setTimeout(() => {if (errorDiv.parentElement) {
                errorDiv.style.animation = 'errorPulse 0.3s ease-out reverse'
                setTimeout(() => errorDiv.remove(), 300)}
        }, 8000);

        return errorDiv;
    }

    static getErrorDisplay(errorType) {
        const displays = {
            'EMPTY_QR': { icon: '📱', title: 'Empty QR Code'},
            'INVALID_FORMAT': { icon: '🔧', title: 'Damaged QR Code'},
            'UNKNOWN_TYPE': { icon: '❓', title: 'Unknown QR Type'},
            'WRONG_DEPARTMENT': { icon: '🏢', title: 'Wrong QR Type'},
            'ITEM_NOT_FOUND': { icon: '📦', title: 'Item Not Found'},
            'EXTERNAL_QR': { icon: '🌐', title: 'External QR Code'},
            'NETWORK_ERROR': { icon: '📡', title: 'Connection Error'}
        };

        return displays[errorType] || { icon: '⚠️', title: 'QR Code Error'};
    }

    static getHelpText(errorType, department) {const helpTexts = {
            'receiving': 'Scan Purchase Order (PO) or Item QR codes for receiving operations',
            'transfers': 'Scan Transfer Ticket or Location QR codes for transfer operations',
            'inventory': 'Scan Item or Location QR codes for inventory management',
            'order_picking': 'Scan Order or Item QR codes for picking operations',
            'problem_solving': 'Scan any warehouse QR code or create a damage report'};

        if (errorType === 'EXTERNAL_QR') {return 'This appears to be a website, contact, or WiFi QR code. Please use warehouse inventory QR codes only.'}

        return helpTexts[department] || 'Please scan a valid warehouse QR code';
    }

    static createSuccessMessage(message, container = document.body) {const successDiv = document.createElement('div')
        successDiv.style.cssText = `
            position: fixed
            top: 20px
            left: 50%;
            transform: translateX(-50%);
            background-color: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            animation: successSlide 0.4s ease-out;
        `;

        successDiv.innerHTML = `
            <div style="text-align: center;">
                <h4 style="margin: 0 0 5px 0;">✅ Success</h4>
                <p style="margin: 0;">${message}</p>
            </div>
        `;

        container.appendChild(successDiv);

        setTimeout(() => {if (successDiv.parentElement) {
                successDiv.style.animation = 'successSlide 0.3s ease-out reverse'
                setTimeout(() => successDiv.remove(), 300)}
        }, 3000);

        return successDiv;
    }
}

// Make QRValidator globally available
window.QRValidator = QRValidator;