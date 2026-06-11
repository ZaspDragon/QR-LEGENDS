# QR Legends Responsive Design System

## Overview
The QR Legends platform now automatically detects your device type (mobile, tablet, desktop) and adjusts the layout, sizing, and touch interactions accordingly.

## Automatic Device Detection

### Mobile Devices (< 768px width)
- ✅ Larger touch targets (minimum 44x44px)
- ✅ Full-width buttons and cards
- ✅ Single-column layout
- ✅ Larger font sizes (16px) to prevent zoom on iOS
- ✅ Simplified navigation with mobile menu
- ✅ Optimized spacing and padding

### Tablet Devices (768px - 1023px width)
- ✅ 2-column grid layouts
- ✅ Touch-friendly buttons (42px minimum height)
- ✅ Balanced spacing for comfortable reading
- ✅ Responsive navigation

### Desktop Devices (>= 1024px width)
- ✅ Full multi-column layouts
- ✅ Desktop navigation bar
- ✅ Hover effects and interactions
- ✅ Optimal spacing for large screens

## Touch Device Optimization
- ✅ Automatically detects touch capabilities
- ✅ Larger tap targets on touch devices
- ✅ Active/pressed states instead of hover effects
- ✅ Prevents accidental zooming
- ✅ Touch-optimized scrolling

## Features

### Automatic Sizing
The system automatically:
- Adjusts font sizes based on screen size
- Resizes buttons and interactive elements
- Reorganizes layouts (columns to rows on mobile)
- Optimizes image sizes
- Prevents horizontal scrolling

### Responsive Navigation
- Desktop: Full navigation bar
- Mobile: Hamburger menu with mobile-optimized navigation
- Tablet: Condensed navigation with essential items

### Device-Specific Classes
The system adds CSS classes to the body element:
- `.device-mobile` - For mobile devices
- `.device-tablet` - For tablet devices  
- `.device-desktop` - For desktop devices
- `.touch-device` - For touch-enabled devices
- `.no-touch` - For mouse/keyboard devices

### JavaScript API
Access device information anywhere in your code:
```javascript
window.QRLegends.device = {
    type: 'mobile' | 'tablet' | 'desktop',
    isMobile: boolean,
    isTablet: boolean,
    isDesktop: boolean,
    isTouch: boolean,
    width: number,
    height: number
}
```

## Orientation Support
- Automatically adjusts when device is rotated
- Optimizes layouts for portrait and landscape modes
- Debounced resize handling for smooth transitions

## Print Optimization
- Clean print styles (removes navigation, buttons, etc.)
- Black text on white background for printing
- Optimized for paper output

## Browser Support
- ✅ iOS Safari
- ✅ Android Chrome
- ✅ Desktop Chrome, Firefox, Safari, Edge
- ✅ iPad and tablet browsers

## Automatic Loading
The responsive design system is automatically loaded on every page through the `auto_theme_injector.js` script - no manual setup required!

## Testing Different Devices
1. Open browser developer tools (F12)
2. Click the device toolbar icon
3. Select different device presets (iPhone, iPad, etc.)
4. Watch the layout automatically adjust!

## Performance
- Debounced resize events (250ms) for optimal performance
- Minimal CSS overhead
- Efficient device detection
- No external dependencies required
