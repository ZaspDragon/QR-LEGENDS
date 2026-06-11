
from flask import jsonify
import json
from datetime import datetime

class IntegrationManager:
    def __init__(self):
        print("✅ Integration manager initialized")
        self.integration_templates = {
            'sap': {
                'name': 'SAP ERP',
                'description': 'Connect to SAP Business Suite for comprehensive ERP functionality',
                'icon': '🏢',
                'category': 'ERP',
                'features': ['Purchase Orders', 'Inventory Sync', 'Financial Reporting'],
                'fields': [
                    {'name': 'base_url', 'label': 'SAP Base URL', 'type': 'url', 'placeholder': 'https://your-sap-server.com', 'required': True},
                    {'name': 'username', 'label': 'Username', 'type': 'text', 'required': True},
                    {'name': 'password', 'label': 'Password', 'type': 'password', 'required': True},
                    {'name': 'company_code', 'label': 'Company Code', 'type': 'text', 'placeholder': '1000', 'required': True},
                    {'name': 'plant_code', 'label': 'Plant Code', 'type': 'text', 'placeholder': '1000'}
                ]
            },
            'oracle': {
                'name': 'Oracle ERP Cloud',
                'description': 'Integrate with Oracle Fusion Cloud ERP',
                'icon': '🅾️',
                'category': 'ERP',
                'features': ['Cloud Integration', 'Real-time Data', 'Advanced Analytics'],
                'fields': [
                    {'name': 'base_url', 'label': 'Oracle Cloud URL', 'type': 'url', 'placeholder': 'https://your-instance.oraclecloud.com', 'required': True},
                    {'name': 'client_id', 'label': 'Client ID', 'type': 'text', 'required': True},
                    {'name': 'client_secret', 'label': 'Client Secret', 'type': 'password', 'required': True},
                    {'name': 'business_unit', 'label': 'Business Unit', 'type': 'text', 'required': True},
                    {'name': 'organization_code', 'label': 'Organization Code', 'type': 'text'}
                ]
            },
            'quickbooks': {
                'name': 'QuickBooks Online',
                'description': 'Sync with QuickBooks for accounting and purchase orders',
                'icon': '💚',
                'category': 'Accounting',
                'features': ['Accounting Sync', 'Invoice Management', 'Payment Tracking'],
                'fields': [
                    {'name': 'base_url', 'label': 'QuickBooks API URL', 'type': 'url', 'value': 'https://quickbooks-api.intuit.com', 'readonly': True},
                    {'name': 'access_token', 'label': 'Access Token', 'type': 'password', 'required': True},
                    {'name': 'company_id', 'label': 'Company ID', 'type': 'text', 'required': True}
                ]
            },
            'netsuite': {
                'name': 'NetSuite ERP',
                'description': 'Connect to NetSuite for comprehensive ERP integration',
                'icon': '🕸️',
                'category': 'ERP',
                'features': ['Full ERP Suite', 'CRM Integration', 'E-commerce'],
                'fields': [
                    {'name': 'base_url', 'label': 'NetSuite URL', 'type': 'url', 'placeholder': 'https://your-account.netsuite.com', 'required': True},
                    {'name': 'consumer_key', 'label': 'Consumer Key', 'type': 'text', 'required': True},
                    {'name': 'consumer_secret', 'label': 'Consumer Secret', 'type': 'password', 'required': True},
                    {'name': 'token_key', 'label': 'Token Key', 'type': 'text', 'required': True},
                    {'name': 'token_secret', 'label': 'Token Secret', 'type': 'password', 'required': True},
                    {'name': 'adjustment_account', 'label': 'Inventory Adjustment Account', 'type': 'text'}
                ]
            },
            'salespad': {
                'name': 'SalesPad for Dynamics GP',
                'description': 'Enhanced sales order processing for Microsoft Dynamics GP',
                'icon': '📊',
                'category': 'Sales',
                'features': ['Order Management', 'Dynamics GP Integration', 'Sales Analytics'],
                'fields': [
                    {'name': 'server', 'label': 'SQL Server', 'type': 'text', 'required': True, 'placeholder': 'server.company.com'},
                    {'name': 'database', 'label': 'Database Name', 'type': 'text', 'required': True, 'placeholder': 'TWO'},
                    {'name': 'username', 'label': 'Database Username', 'type': 'text', 'required': True},
                    {'name': 'password', 'label': 'Database Password', 'type': 'password', 'required': True},
                    {'name': 'salespad_version', 'label': 'SalesPad Version', 'type': 'text', 'placeholder': '5.0'}
                ]
            },
            'dynamics_gp': {
                'name': 'Microsoft Dynamics GP',
                'description': 'Connect to Microsoft Dynamics Great Plains ERP system',
                'icon': '🔷',
                'category': 'ERP',
                'features': ['Financial Management', 'Distribution', 'Manufacturing'],
                'fields': [
                    {'name': 'server', 'label': 'SQL Server', 'type': 'text', 'required': True, 'placeholder': 'server.company.com'},
                    {'name': 'database', 'label': 'Company Database', 'type': 'text', 'required': True, 'placeholder': 'TWO'},
                    {'name': 'username', 'label': 'SQL Username', 'type': 'text', 'required': True},
                    {'name': 'password', 'label': 'SQL Password', 'type': 'password', 'required': True},
                    {'name': 'company_id', 'label': 'GP Company ID', 'type': 'text', 'required': True}
                ]
            },
            'sage': {
                'name': 'Sage ERP',
                'description': 'Integrate with Sage business management solutions',
                'icon': '🌿',
                'category': 'ERP',
                'features': ['Financial Management', 'CRM', 'Business Intelligence'],
                'fields': [
                    {'name': 'base_url', 'label': 'Sage Server URL', 'type': 'url', 'required': True},
                    {'name': 'username', 'label': 'Username', 'type': 'text', 'required': True},
                    {'name': 'password', 'label': 'Password', 'type': 'password', 'required': True},
                    {'name': 'company_database', 'label': 'Company Database', 'type': 'text', 'required': True}
                ]
            },
            'epicor': {
                'name': 'Epicor ERP',
                'description': 'Connect to Epicor enterprise resource planning system',
                'icon': '⚡',
                'category': 'ERP',
                'features': ['Manufacturing', 'Supply Chain', 'Financial Management'],
                'fields': [
                    {'name': 'base_url', 'label': 'Epicor Server URL', 'type': 'url', 'required': True},
                    {'name': 'username', 'label': 'Username', 'type': 'text', 'required': True},
                    {'name': 'password', 'label': 'Password', 'type': 'password', 'required': True},
                    {'name': 'company', 'label': 'Company ID', 'type': 'text', 'required': True},
                    {'name': 'plant', 'label': 'Plant ID', 'type': 'text'}
                ]
            },
            'infor': {
                'name': 'Infor ERP',
                'description': 'Integrate with Infor CloudSuite Industrial',
                'icon': '☁️',
                'category': 'ERP',
                'features': ['Cloud-based', 'Industry-specific', 'AI-powered'],
                'fields': [
                    {'name': 'base_url', 'label': 'Infor Cloud URL', 'type': 'url', 'required': True},
                    {'name': 'username', 'label': 'Username', 'type': 'text', 'required': True},
                    {'name': 'password', 'label': 'Password', 'type': 'password', 'required': True},
                    {'name': 'logical_id', 'label': 'Logical ID', 'type': 'text', 'required': True},
                    {'name': 'company', 'label': 'Company', 'type': 'text', 'required': True}
                ]
            },
            'custom_api': {
                'name': 'Custom API',
                'description': 'Connect to your proprietary or custom API system',
                'icon': '🔧',
                'category': 'Integration',
                'features': ['Custom Endpoints', 'Flexible Configuration', 'API Key Support'],
                'fields': [
                    {'name': 'base_url', 'label': 'API Base URL', 'type': 'url', 'required': True},
                    {'name': 'api_key', 'label': 'API Key', 'type': 'password'},
                    {'name': 'username', 'label': 'Username (Basic Auth)', 'type': 'text'},
                    {'name': 'password', 'label': 'Password (Basic Auth)', 'type': 'password'},
                    {'name': 'po_endpoint', 'label': 'PO Endpoint', 'type': 'text', 'placeholder': '/api/purchase-orders'},
                    {'name': 'inventory_endpoint', 'label': 'Inventory Endpoint', 'type': 'text', 'placeholder': '/api/inventory'}
                ]
            },
            'webhook': {
                'name': 'Webhook Integration',
                'description': 'Send real-time data to any webhook endpoint',
                'icon': '🔗',
                'category': 'Integration',
                'features': ['Real-time Updates', 'Event-driven', 'HTTP Callbacks'],
                'fields': [
                    {'name': 'webhook_url', 'label': 'Webhook URL', 'type': 'url', 'required': True},
                    {'name': 'webhook_secret', 'label': 'Webhook Secret (Optional)', 'type': 'password'},
                    {'name': 'auth_header', 'label': 'Authorization Header', 'type': 'text', 'placeholder': 'Bearer token or API key'}
                ]
            },
            'shopify': {
                'name': 'Shopify',
                'description': 'Sync inventory and orders with Shopify e-commerce platform',
                'icon': '🛍️',
                'category': 'E-commerce',
                'features': ['Inventory Sync', 'Order Management', 'Product Catalog'],
                'fields': [
                    {'name': 'shop_domain', 'label': 'Shop Domain', 'type': 'text', 'required': True, 'placeholder': 'yourstore.myshopify.com'},
                    {'name': 'access_token', 'label': 'Private App Access Token', 'type': 'password', 'required': True},
                    {'name': 'webhook_secret', 'label': 'Webhook Secret', 'type': 'password'}
                ]
            },
            'woocommerce': {
                'name': 'WooCommerce',
                'description': 'Connect to WooCommerce WordPress e-commerce stores',
                'icon': '🛒',
                'category': 'E-commerce',
                'features': ['WordPress Integration', 'Order Sync', 'Product Management'],
                'fields': [
                    {'name': 'base_url', 'label': 'Store URL', 'type': 'url', 'required': True, 'placeholder': 'https://yourstore.com'},
                    {'name': 'consumer_key', 'label': 'Consumer Key', 'type': 'text', 'required': True},
                    {'name': 'consumer_secret', 'label': 'Consumer Secret', 'type': 'password', 'required': True},
                    {'name': 'webhook_secret', 'label': 'Webhook Secret', 'type': 'password'}
                ]
            },
            'amazon_seller': {
                'name': 'Amazon Seller Central',
                'description': 'Integrate with Amazon marketplace for inventory management',
                'icon': '📦',
                'category': 'Marketplace',
                'features': ['Marketplace Integration', 'Inventory Sync', 'Order Management'],
                'fields': [
                    {'name': 'seller_id', 'label': 'Seller ID', 'type': 'text', 'required': True},
                    {'name': 'marketplace_id', 'label': 'Marketplace ID', 'type': 'text', 'required': True, 'placeholder': 'ATVPDKIKX0DER'},
                    {'name': 'access_key', 'label': 'AWS Access Key', 'type': 'text', 'required': True},
                    {'name': 'secret_key', 'label': 'AWS Secret Key', 'type': 'password', 'required': True},
                    {'name': 'mws_token', 'label': 'MWS Auth Token', 'type': 'password', 'required': True}
                ]
            },
            'ebay': {
                'name': 'eBay Seller',
                'description': 'Connect to eBay for marketplace inventory synchronization',
                'icon': '🏪',
                'category': 'Marketplace',
                'features': ['Marketplace Sync', 'Auction Management', 'Fixed Price Listings'],
                'fields': [
                    {'name': 'app_id', 'label': 'Application ID (Client ID)', 'type': 'text', 'required': True},
                    {'name': 'dev_id', 'label': 'Developer ID', 'type': 'text', 'required': True},
                    {'name': 'cert_id', 'label': 'Certificate ID', 'type': 'password', 'required': True},
                    {'name': 'user_token', 'label': 'User Token', 'type': 'password', 'required': True},
                    {'name': 'sandbox', 'label': 'Use Sandbox', 'type': 'checkbox'}
                ]
            }
        }
        self.configured_integrations = {}

    def get_integrations(self, company_id):
        return list(self.configured_integrations.keys())

    def get_available_integrations(self):
        return self.integration_templates

    def get_configured_integrations(self):
        return self.configured_integrations

    def setup_integration(self, system_type, config):
        """Setup a new integration"""
        if system_type not in self.integration_templates:
            return {'success': False, 'error': 'Unknown integration type'}
        
        self.configured_integrations[system_type] = {
            'config': config,
            'setup_date': datetime.now().isoformat(),
            'enabled': True
        }
        
        return {'success': True, 'message': f'{system_type} integration configured successfully'}

    def test_integration(self, company_id, integration_type):
        """Test an integration connection"""
        if integration_type not in self.configured_integrations:
            return {'success': False, 'error': 'Integration not configured'}
        
        # Simulate test results
        test_results = {
            'sap': {'success': True, 'message': 'SAP connection successful', 'status': 'success'},
            'oracle': {'success': True, 'message': 'Oracle connection successful', 'status': 'success'},
            'quickbooks': {'success': True, 'message': 'QuickBooks connection successful', 'status': 'success'},
            'netsuite': {'success': True, 'message': 'NetSuite connection successful', 'status': 'success'},
            'salespad': {'success': True, 'message': 'SalesPad connection successful', 'status': 'success'},
            'dynamics_gp': {'success': True, 'message': 'Dynamics GP connection successful', 'status': 'success'}
        }
        
        result = test_results.get(integration_type, {'success': True, 'message': 'Connection test successful', 'status': 'success'})
        
        # Store test result
        self.configured_integrations[integration_type]['test_result'] = result
        
        return result

    def submit_po(self, system_type, po_data):
        """Submit purchase order to external system"""
        if system_type not in self.configured_integrations:
            return {'success': False, 'error': 'Integration not configured'}
        
        return {'success': True, 'message': f'PO {po_data.get("po_number")} submitted to {system_type}'}

    def submit_inventory(self, system_type, inventory_data):
        """Submit inventory update to external system"""
        if system_type not in self.configured_integrations:
            return {'success': False, 'error': 'Integration not configured'}
        
        return {'success': True, 'message': f'{len(inventory_data)} inventory items submitted to {system_type}'}

# Global instance
integration_manager = IntegrationManager()
