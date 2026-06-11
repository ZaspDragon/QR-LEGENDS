from flask import Blueprint, request, jsonify
import json
from datetime import datetime
from erp_core import erp_core
from salespad_module import salespad_module

# Create Blueprint for ERP/SalesPad API endpoints
integration_bp = Blueprint('integration', __name__)

def get_current_user():
    """Get current user data from session"""
    from flask import session
    
    if 'user_id' in session and 'authenticated' in session:
        return {
            'user_id': session.get('user_id'),
            'company_id': session.get('company_id'),
            'username': session.get('username'),
            'role': session.get('role')
        }
    return None

# ERP Core Endpoints
@integration_bp.route('/api/erp/customers', methods=['GET', 'POST'])
def manage_customers():
    if request.method == 'GET':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            customers = erp_core.get_customers_by_company(user['company_id'])
            return jsonify({
                'success': True,
                'customers': customers
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            customer_id = erp_core.add_customer(user['company_id'], data)

            return jsonify({
                'success': True,
                'customer_id': customer_id,
                'message': 'Customer added successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/customers/<customer_id>', methods=['PUT', 'DELETE'])
def update_delete_customer(customer_id):
    if request.method == 'PUT':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            success = erp_core.update_customer(customer_id, user['company_id'], data)

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Customer updated successfully'
                })
            else:
                return jsonify({'error': 'Customer not found or access denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            success = erp_core.delete_customer(customer_id, user['company_id'])

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Customer deleted successfully'
                })
            else:
                return jsonify({'error': 'Customer not found or access denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/suppliers', methods=['GET', 'POST'])
def manage_suppliers():
    if request.method == 'GET':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            suppliers = erp_core.get_suppliers_by_company(user['company_id'])
            return jsonify({
                'success': True,
                'suppliers': suppliers
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            supplier_id = erp_core.add_supplier(user['company_id'], data)

            return jsonify({
                'success': True,
                'supplier_id': supplier_id,
                'message': 'Supplier added successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/suppliers/<supplier_id>', methods=['PUT', 'DELETE'])
def update_delete_supplier(supplier_id):
    if request.method == 'PUT':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            success = erp_core.update_supplier(supplier_id, user['company_id'], data)

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Supplier updated successfully'
                })
            else:
                return jsonify({'error': 'Supplier not found or access denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            success = erp_core.delete_supplier(supplier_id, user['company_id'])

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Supplier deleted successfully'
                })
            else:
                return jsonify({'error': 'Supplier not found or access denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/items', methods=['GET', 'POST'])
def manage_items():
    if request.method == 'GET':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            items = erp_core.get_items_by_company(user['company_id'])
            return jsonify({
                'success': True,
                'items': items
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            item_id = erp_core.add_item_master(user['company_id'], data)

            return jsonify({
                'success': True,
                'item_id': item_id,
                'message': 'Item added to master catalog'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/items/<item_id>', methods=['PUT', 'DELETE'])
def update_delete_item(item_id):
    if request.method == 'PUT':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            success = erp_core.update_item_master(item_id, user['company_id'], data)

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Item updated successfully'
                })
            else:
                return jsonify({'error': 'Item not found or access denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            success = erp_core.delete_item_master(item_id, user['company_id'])

            if success:
                return jsonify({
                    'success': True,
                    'message': 'Item deleted successfully'
                })
            else:
                return jsonify({'error': 'Item not found or access denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/purchase-orders', methods=['POST'])
def create_purchase_order():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        data['created_by'] = user['user_id']
        po_id = erp_core.create_purchase_order(user['company_id'], data)

        return jsonify({
            'success': True,
            'po_id': po_id,
            'message': 'Purchase order created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/purchase-orders/<po_id>/approve', methods=['POST'])
def approve_purchase_order(po_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        success = erp_core.approve_purchase_order(po_id, user['user_id'])

        if success:
            return jsonify({
                'success': True,
                'message': 'Purchase order approved'
            })
        else:
            return jsonify({'error': 'Purchase order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/reports/purchase-vs-usage', methods=['GET'])
def get_purchase_vs_usage_report():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        days = request.args.get('days', 30, type=int)
        report = erp_core.get_purchase_vs_usage_report(user['company_id'], days)

        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/reports/supplier-spend', methods=['GET'])
def get_supplier_spend_analysis():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        analysis = erp_core.get_supplier_spend_analysis(user['company_id'])

        return jsonify({'supplier_analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ERP Receiving Transactions endpoints
@integration_bp.route('/api/erp/receiving-transactions', methods=['GET'])
def get_receiving_transactions():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        transactions = erp_core.get_receiving_transactions_by_company(user['company_id'])
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/receiving-transactions', methods=['POST'])
def add_receiving_transaction():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        transaction_id = erp_core.add_receiving_transaction(user['company_id'], data)

        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'message': 'Receiving transaction recorded successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/in-transit-items', methods=['GET'])
def get_in_transit_items():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        items = erp_core.get_in_transit_items_by_company(user['company_id'])
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/in-transit-items', methods=['POST'])
def add_in_transit_item():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        item_id = erp_core.add_in_transit_item(user['company_id'], data)

        return jsonify({
            'success': True,
            'item_id': item_id,
            'message': 'In-transit item added successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/in-transit-items/<item_id>/status', methods=['PUT'])
def update_in_transit_status(item_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        new_status = data.get('status')

        success = erp_core.update_in_transit_status(item_id, new_status)

        if success:
            return jsonify({
                'success': True,
                'message': 'In-transit status updated successfully'
            })
        else:
            return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/erp/receiving-variances', methods=['POST'])
def record_receiving_variance():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        variance_id = erp_core.record_receiving_variance(user['company_id'], data)

        return jsonify({
            'success': True,
            'variance_id': variance_id,
            'message': 'Receiving variance recorded successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SalesPad Module Endpoints
@integration_bp.route('/api/salespad/quotes', methods=['GET', 'POST'])
def manage_sales_quotes():
    if request.method == 'GET':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            quotes = salespad_module.get_quotes_by_company(user['company_id'])
            return jsonify({
                'success': True,
                'quotes': quotes
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            data['sales_rep'] = user['user_id']
            quote_id = salespad_module.create_sales_quote(user['company_id'], data)

            return jsonify({
                'success': True,
                'quote_id': quote_id,
                'message': 'Sales quote created successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/orders', methods=['GET'])
def get_sales_orders():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        orders = salespad_module.get_orders_by_company(user['company_id'])
        return jsonify({
            'success': True,
            'orders': orders
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/quotes/<quote_id>/convert', methods=['POST'])
def convert_quote_to_order(quote_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        order_id = salespad_module.convert_quote_to_order(quote_id)

        if order_id:
            return jsonify({
                'success': True,
                'order_id': order_id,
                'message': 'Quote converted to order successfully'
            })
        else:
            return jsonify({'error': 'Quote not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/stock-check', methods=['POST'])
def check_stock_availability():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        items = data.get('items', [])

        availability = salespad_module.check_stock_availability(items, user['company_id'])

        return jsonify(availability)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/orders/<order_id>/pick-ticket', methods=['POST'])
def generate_pick_ticket(order_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        pick_ticket = salespad_module.generate_pick_ticket(order_id)

        return jsonify(pick_ticket)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/customer-interactions', methods=['POST'])
def log_customer_interaction():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        data['sales_rep'] = user['user_id']
        interaction_id = salespad_module.log_customer_interaction(user['company_id'], data)

        return jsonify({
            'success': True,
            'interaction_id': interaction_id,
            'message': 'Customer interaction logged'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/pricing-rules', methods=['POST'])
def create_pricing_rule():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        rule_id = salespad_module.create_pricing_rule(user['company_id'], data)

        return jsonify({
            'success': True,
            'rule_id': rule_id,
            'message': 'Pricing rule created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/pricing/calculate', methods=['POST'])
def calculate_pricing():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        customer_id = data.get('customer_id')
        items = data.get('items', [])

        pricing = salespad_module.calculate_pricing(user['company_id'], customer_id, items)

        return jsonify(pricing)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/invoices', methods=['POST'])
def generate_invoice():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        order_id = data.get('order_id')

        invoice_id = salespad_module.generate_invoice(order_id)

        if invoice_id:
            return jsonify({
                'success': True,
                'invoice_id': invoice_id,
                'message': 'Invoice generated successfully'
            })
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/payments', methods=['POST'])
def record_payment():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        invoice_id = data.get('invoice_id')

        payment_id = salespad_module.record_payment(invoice_id, data)

        if payment_id:
            return jsonify({
                'success': True,
                'payment_id': payment_id,
                'message': 'Payment recorded successfully'
            })
        else:
            return jsonify({'error': 'Invoice not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/salespad/reports/sales-by-rep', methods=['GET'])
def get_sales_by_rep_report():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        if not date_from or not date_to:
            return jsonify({'error': 'date_from and date_to parameters required'}), 400

        report = salespad_module.get_sales_by_rep_report(user['company_id'], date_from, date_to)

        return jsonify({'sales_by_rep': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Integration Sync Endpoints
@integration_bp.route('/api/integration/sync-inventory', methods=['POST'])
def sync_inventory_to_erp():
    """Sync WMS inventory data to ERP item master"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        # This would sync inventory items from main.py to ERP item master
        from main import inventory_items

        synced_items = 0
        for item_id, item_data in inventory_items.items():
            if isinstance(item_data, dict) and item_data.get('company_id') == user['company_id']:
                # Convert WMS item to ERP item master format
                erp_item_data = {
                    'sku': item_data.get('item_name', item_id),
                    'barcode_qr': item_data.get('qr_code', ''),
                    'item_name': item_data.get('item_name', ''),
                    'description': item_data.get('description', ''),
                    'length': item_data.get('length', 0),
                    'width': item_data.get('width', 0),
                    'height': item_data.get('height', 0),
                    'weight': item_data.get('weight', 0),
                    'unit_cost': item_data.get('cost', 0),
                    'category': item_data.get('category', 'General')
                }

                erp_core.add_item_master(user['company_id'], erp_item_data)
                synced_items += 1

        return jsonify({
            'success': True,
            'synced_items': synced_items,
            'message': f'Synced {synced_items} items to ERP'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integration_bp.route('/api/integration/export-quickbooks', methods=['GET'])
def export_to_quickbooks():
    """Export financial data to QuickBooks format"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        # Generate CSV export for QuickBooks
        transactions = erp_core.financial_transactions
        company_transactions = [
            t for t in transactions 
            if t.get('company_id') == user['company_id']
        ]

        # Convert to QuickBooks CSV format
        csv_data = "Date,Type,Num,Name,Memo,Account,Amount\n"
        for trans in company_transactions:
            csv_data += f"{trans['transaction_date']},{trans['transaction_type']},{trans['transaction_id']},Customer,{trans['description']},{trans['account_code']},{trans['amount']}\n"

        return jsonify({
            'success': True,
            'csv_data': csv_data,
            'record_count': len(company_transactions),
            'export_date': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ERP Analytics endpoints
@integration_bp.route('/api/erp/analytics/purchase', methods=['GET'])
def get_purchase_analytics():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        report = erp_core.get_purchase_analytics(user['company_id'])

        return jsonify({'purchase_analytics': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500