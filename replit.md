# Overview

QR Legends is a comprehensive warehouse management system (WMS) and enterprise resource planning (ERP) platform built with Flask and Python. It provides QR code-first workflows for all warehouse operations including receiving, putaway, picking, packing, shipping, and inventory management. The platform integrates modular ERP components for finance, HR, manufacturing, and project management, alongside core WMS functionalities. Its purpose is to streamline supply chain operations, enhance efficiency through mobile-native QR scanning, and offer a unified platform for enterprise resource planning with a focus on data integrity and security.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Framework
- **Backend**: Flask web application with Python 3.x.
- **Frontend**: HTML/CSS/JavaScript with Flask-served templates.
- **Session Management**: Flask sessions for authentication and state.
- **CORS Support**: Flask-CORS for cross-origin requests.

## Data Storage
- **File-based JSON Storage**: All business data is stored in organized JSON files within the file system (`data/` directory and subdirectories).
- **No Database Dependency**: Utilizes the file system for persistence.
- **Backup System**: Automated backup service with change tracking and audit logs.

## Authentication & Security
- **Multi-tenant Architecture**: Company-based data isolation.
- **Role-based Access**: Supports Admin, Manager, Worker, and Auditor roles, with dynamic widget filtering based on role and department.
- **Password Hashing**: SHA-256 and Werkzeug for credential protection.
- **QR Code Security**: HMAC signing for tamper-proof QR payloads.
- **Demo Auto-Login Routes**: Provides routes for instant access to demo environments.

## QR Code System
- **QR-First Workflows**: All warehouse operations are designed around QR code scanning.
- **Mobile-Native**: Camera-based scanning is used without dedicated hardware.
- **Workflow Engine**: Centralized QR processing with signed payloads and idempotency.
- **Label Generation**: Dynamic QR code and label creation using PIL/qrcode.

## Modular Architecture
- **Core WMS**: Inventory, receiving, shipping, picking, transfers.
- **ERP Modules**: Financial management, procurement, customer/supplier management, HR/Payroll, Manufacturing, Project Management, SalesPad-style sales.
- **ASN Module**: Advanced Shipping Notice management with vendor integration.
- **Integration Layer**: APIs and connectors for external systems.

## API Design
- **RESTful Endpoints**: JSON-based APIs for all operations.
- **Integration Blueprint**: Separate Flask blueprint for ERP and external integrations.
- **Webhook Support**: Event-driven integrations for backup service notifications.

## Warehouse Operations
- **Dual-Path Receiving System**: Supports both PO-based and ASN-based receiving with variance tracking and putaway label generation.
- **Navigation System**: A* pathfinding for warehouse routing with 3D coordinate support.
- **Exception Handling**: Centralized damage reporting and variance tracking.
- **Real-time Tracking**: Live inventory and order status updates.
- **Dedicated Job Pages**: Five mobile-first job pages for Manager, Inventory Data Analyst, Stock Mover, Transfer Picker, and Order Picker roles, accessible via `/job_<role>` routes.

## Known Bugs Fixed
- **Critical: `inject_dark_theme` str.replace bug** — `html_content.replace('<head>', '<head>' + theme_injection)` was replacing ALL occurrences of `<head>`, including ones inside JavaScript strings (e.g., `'<html><head><title>...'` in `printLabel` function). The injected `</script>` tags inside JS strings caused the browser's HTML parser to prematurely close the `<script>` block, treating the subsequent JavaScript as HTML. This produced a literal `<img src="' + qrImageSrc + '"` DOM element that caused 500 errors. Fixed by using `replace('<head>', ..., 1)` (replace only the first occurrence).
- **Catch-all route returned 500 for NotFound** — Updated to detect `werkzeug.exceptions.NotFound` and return proper 404 responses.
- **Missing API endpoints** — Added 5 API endpoints (`/api/job_manager_data`, `/api/job_analyst_data`, `/api/job_stock_mover_data`, `/api/job_transfer_picker_data`, `/api/job_order_picker_data`) before the catch-all route to prevent 500 errors.

## User Interface
- **Personalized Employee Dashboard**: Role-based dashboards showing employee-specific information and company/team metrics.
- **Role-specific Views**: Tailored experiences for different user types, including dynamic widget filtering based on role and department.
- **Hierarchical Sidebar Navigation**: Collapsible sidebar with main departments and mini sub-tabs, customizable by users.
- **Mobile Responsive Design**: Optimized for warehouse devices with touch-friendly interfaces, responsive tables, and mobile navigation.
- **Progressive Disclosure**: Simplified navigation with contextual access to features.

# External Dependencies

## Core Libraries
- **Flask**: Web framework.
- **Flask-CORS**: Cross-origin request handling.
- **Flask-Session**: Session management.
- **Werkzeug**: Security utilities.
- **Pillow**: Image processing for QR codes and labels.
- **qrcode**: QR code generation.
- **requests**: HTTP client for external API calls.

## Integration Targets
- **ERP Systems**: SAP, Oracle, NetSuite, Infor (via APIs).
- **Accounting**: QuickBooks, Xero, Sage.
- **E-commerce**: Shopify, Amazon.
- **Shipping**: UPS, FedEx, DHL.
- **Communication**: Email/SMS services.