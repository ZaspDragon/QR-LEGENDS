
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from backup_service import auto_backup_trigger

class SalesPadModule:
    """SalesPad-style front-end sales & order management layer"""
    
    def __init__(self):
        self.data_dir = 'data/salespad'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data storage
        self.sales_quotes = self.load_data('sales_quotes.json', {})
        self.sales_orders = self.load_data('sales_orders.json', {})
        self.invoices = self.load_data('invoices.json', {})
        self.customer_interactions = self.load_data('customer_interactions.json', {})
        self.pricing_rules = self.load_data('pricing_rules.json', {})
        self.payment_records = self.load_data('payment_records.json', {})
        
    def load_data(self, filename: str, default: Any) -> Any:
        """Load data from JSON file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return default
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default
    
    def save_data(self, filename: str, data: Any):
        """Save data to JSON file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filename}: {e}")
    
    # Order Management
    def create_sales_quote(self, company_id: str, quote_data: Dict[str, Any]) -> str:
        """Create sales quote"""
        quote_id = str(uuid.uuid4())
        quote_record = {
            'quote_id': quote_id,
            'quote_number': quote_data.get('quote_number', f"QT-{datetime.now().strftime('%Y%m%d')}-{quote_id[:8]}"),
            'company_id': company_id,
            'customer_id': quote_data.get('customer_id'),
            'sales_rep': quote_data.get('sales_rep'),
            'quote_date': datetime.now().isoformat(),
            'expiry_date': quote_data.get('expiry_date'),
            'items': quote_data.get('items', []),  # [{item_id, quantity, unit_price, discount}]
            'subtotal': quote_data.get('subtotal', 0),
            'tax_amount': quote_data.get('tax_amount', 0),
            'total_amount': quote_data.get('total_amount', 0),
            'status': 'draft',  # draft, sent, accepted, rejected, expired
            'notes': quote_data.get('notes', ''),
            'converted_to_order': False,
            'order_id': None
        }
        
        self.sales_quotes[quote_id] = quote_record
        self.save_data('sales_quotes.json', self.sales_quotes)
        
        # Log change for backup
        auto_backup_trigger.log_change(company_id, 'sales_quote_created', {
            'quote_id': quote_id,
            'quote_number': quote_record['quote_number'],
            'customer_id': quote_data.get('customer_id'),
            'total_amount': quote_data.get('total_amount', 0),
            'action': 'create_sales_quote',
            'source': 'salespad'
        })
        
        return quote_id
    
    def convert_quote_to_order(self, quote_id: str) -> Optional[str]:
        """Convert sales quote to sales order"""
        if quote_id not in self.sales_quotes:
            return None
        
        quote = self.sales_quotes[quote_id]
        
        # Create sales order from quote
        order_id = str(uuid.uuid4())
        order_record = {
            'order_id': order_id,
            'order_number': f"SO-{datetime.now().strftime('%Y%m%d')}-{order_id[:8]}",
            'company_id': quote['company_id'],
            'customer_id': quote['customer_id'],
            'sales_rep': quote['sales_rep'],
            'quote_id': quote_id,
            'order_date': datetime.now().isoformat(),
            'items': quote['items'].copy(),
            'subtotal': quote['subtotal'],
            'tax_amount': quote['tax_amount'],
            'total_amount': quote['total_amount'],
            'status': 'pending',  # pending, picking, shipped, delivered, invoiced
            'fulfillment': {
                'pick_priority': 'normal',
                'pick_status': 'not_started',
                'partial_shipments_allowed': True,
                'shipped_items': [],
                'backorder_items': []
            },
            'shipping_info': {
                'address': '',
                'method': '',
                'tracking_number': '',
                'shipped_date': None
            }
        }
        
        self.sales_orders[order_id] = order_record
        self.save_data('sales_orders.json', self.sales_orders)
        
        # Update quote
        quote['status'] = 'accepted'
        quote['converted_to_order'] = True
        quote['order_id'] = order_id
        self.save_data('sales_quotes.json', self.sales_quotes)
        
        # Log change for backup
        auto_backup_trigger.log_change(quote['company_id'], 'quote_converted_to_order', {
            'quote_id': quote_id,
            'order_id': order_id,
            'order_number': order_record['order_number'],
            'action': 'convert_quote_to_order',
            'source': 'salespad'
        })
        
        return order_id
    
    def check_stock_availability(self, items: List[Dict[str, Any]], company_id: str) -> Dict[str, Any]:
        """Check real-time stock availability from WMS"""
        # This would integrate with your WMS inventory system
        # For now, simulate stock checking
        availability_report = {
            'all_in_stock': True,
            'item_availability': [],
            'backorder_required': False,
            'checked_at': datetime.now().isoformat()
        }
        
        for item in items:
            item_id = item.get('item_id')
            requested_qty = item.get('quantity', 0)
            
            # Simulate stock check (in production, query your WMS)
            available_qty = 100  # Placeholder
            
            item_status = {
                'item_id': item_id,
                'requested_quantity': requested_qty,
                'available_quantity': available_qty,
                'in_stock': available_qty >= requested_qty,
                'shortage': max(0, requested_qty - available_qty)
            }
            
            availability_report['item_availability'].append(item_status)
            
            if not item_status['in_stock']:
                availability_report['all_in_stock'] = False
                availability_report['backorder_required'] = True
        
        return availability_report
    
    def generate_pick_ticket(self, order_id: str) -> Dict[str, Any]:
        """Generate pick ticket for WMS"""
        if order_id not in self.sales_orders:
            return {'error': 'Order not found'}
        
        order = self.sales_orders[order_id]
        
        pick_ticket = {
            'pick_ticket_id': str(uuid.uuid4()),
            'order_id': order_id,
            'order_number': order['order_number'],
            'customer_id': order['customer_id'],
            'pick_priority': order['fulfillment']['pick_priority'],
            'items_to_pick': order['items'],
            'created_at': datetime.now().isoformat(),
            'status': 'pending_pick',
            'assigned_picker': None,
            'auto_generated': True,
            'wave_id': None
        }
        
        # Update order status
        order['fulfillment']['pick_status'] = 'pick_ticket_generated'
        order['status'] = 'picking'
        self.save_data('sales_orders.json', self.sales_orders)
        
        # Log the pick ticket generation for backup
        auto_backup_trigger.log_change(order['company_id'], 'pick_ticket_generated', {
            'pick_ticket_id': pick_ticket['pick_ticket_id'],
            'order_id': order_id,
            'order_number': order['order_number'],
            'customer_id': order['customer_id'],
            'items_count': len(order['items']),
            'action': 'generate_pick_ticket',
            'source': 'salespad_auto'
        })
        
        return pick_ticket
    
    def get_orders_for_date(self, company_id: str, target_date: str) -> List[Dict[str, Any]]:
        """Get all orders for a specific date"""
        orders_for_date = []
        
        for order_id, order in self.sales_orders.items():
            if (order.get('company_id') == company_id and 
                order.get('order_date', '').startswith(target_date)):
                orders_for_date.append({
                    'order_id': order_id,
                    'order_data': order
                })
        
        return orders_for_date
    
    def get_pending_orders(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all pending orders ready for picking"""
        pending_orders = []
        
        for order_id, order in self.sales_orders.items():
            if (order.get('company_id') == company_id and 
                order.get('status') in ['pending', 'approved'] and
                order['fulfillment'].get('pick_status') in ['not_started', 'pending']):
                pending_orders.append({
                    'order_id': order_id,
                    'order_data': order
                })
        
        return pending_orders
    
    # Customer Relationship Management
    def log_customer_interaction(self, company_id: str, interaction_data: Dict[str, Any]) -> str:
        """Log customer interaction"""
        interaction_id = str(uuid.uuid4())
        interaction = {
            'interaction_id': interaction_id,
            'company_id': company_id,
            'customer_id': interaction_data.get('customer_id'),
            'interaction_type': interaction_data.get('type'),  # email, call, meeting, note
            'subject': interaction_data.get('subject'),
            'description': interaction_data.get('description'),
            'sales_rep': interaction_data.get('sales_rep'),
            'interaction_date': datetime.now().isoformat(),
            'follow_up_required': interaction_data.get('follow_up_required', False),
            'follow_up_date': interaction_data.get('follow_up_date'),
            'attachments': interaction_data.get('attachments', [])
        }
        
        if company_id not in self.customer_interactions:
            self.customer_interactions[company_id] = []
        
        self.customer_interactions[company_id].append(interaction)
        self.save_data('customer_interactions.json', self.customer_interactions)
        
        return interaction_id
    
    # Pricing & Discounts
    def create_pricing_rule(self, company_id: str, pricing_data: Dict[str, Any]) -> str:
        """Create customer-specific pricing rule"""
        rule_id = str(uuid.uuid4())
        rule = {
            'rule_id': rule_id,
            'company_id': company_id,
            'rule_name': pricing_data.get('rule_name'),
            'rule_type': pricing_data.get('type'),  # customer_specific, volume_based, promo_code
            'customer_id': pricing_data.get('customer_id'),
            'item_id': pricing_data.get('item_id'),
            'conditions': {
                'min_quantity': pricing_data.get('min_quantity', 0),
                'max_quantity': pricing_data.get('max_quantity'),
                'promo_code': pricing_data.get('promo_code'),
                'valid_from': pricing_data.get('valid_from'),
                'valid_until': pricing_data.get('valid_until')
            },
            'pricing': {
                'discount_type': pricing_data.get('discount_type'),  # percentage, fixed_amount
                'discount_value': pricing_data.get('discount_value', 0),
                'special_price': pricing_data.get('special_price')
            },
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        if company_id not in self.pricing_rules:
            self.pricing_rules[company_id] = []
        
        self.pricing_rules[company_id].append(rule)
        self.save_data('pricing_rules.json', self.pricing_rules)
        
        return rule_id
    
    def calculate_pricing(self, company_id: str, customer_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate pricing with applicable discounts"""
        pricing_summary = {
            'subtotal': 0,
            'total_discount': 0,
            'final_total': 0,
            'applied_rules': [],
            'item_pricing': []
        }
        
        company_rules = self.pricing_rules.get(company_id, [])
        
        for item in items:
            item_id = item.get('item_id')
            quantity = item.get('quantity', 1)
            base_price = item.get('base_price', 0)
            
            item_subtotal = base_price * quantity
            item_discount = 0
            applied_rules = []
            
            # Check for applicable pricing rules
            for rule in company_rules:
                if self._rule_applies(rule, customer_id, item_id, quantity):
                    discount = self._calculate_rule_discount(rule, item_subtotal, quantity)
                    if discount > item_discount:  # Use best discount
                        item_discount = discount
                        applied_rules = [rule['rule_id']]
            
            final_price = item_subtotal - item_discount
            
            pricing_summary['item_pricing'].append({
                'item_id': item_id,
                'quantity': quantity,
                'base_price': base_price,
                'subtotal': item_subtotal,
                'discount': item_discount,
                'final_price': final_price,
                'applied_rules': applied_rules
            })
            
            pricing_summary['subtotal'] += item_subtotal
            pricing_summary['total_discount'] += item_discount
        
        pricing_summary['final_total'] = pricing_summary['subtotal'] - pricing_summary['total_discount']
        
        return pricing_summary
    
    def _rule_applies(self, rule: Dict[str, Any], customer_id: str, item_id: str, quantity: int) -> bool:
        """Check if pricing rule applies to current item/customer"""
        # Customer-specific rules
        if rule.get('customer_id') and rule['customer_id'] != customer_id:
            return False
        
        # Item-specific rules
        if rule.get('item_id') and rule['item_id'] != item_id:
            return False
        
        # Quantity conditions
        conditions = rule.get('conditions', {})
        min_qty = conditions.get('min_quantity', 0)
        max_qty = conditions.get('max_quantity')
        
        if quantity < min_qty:
            return False
        
        if max_qty and quantity > max_qty:
            return False
        
        # Date validity
        valid_from = conditions.get('valid_from')
        valid_until = conditions.get('valid_until')
        now = datetime.now().isoformat()
        
        if valid_from and now < valid_from:
            return False
        
        if valid_until and now > valid_until:
            return False
        
        return True
    
    def _calculate_rule_discount(self, rule: Dict[str, Any], subtotal: float, quantity: int) -> float:
        """Calculate discount amount based on rule"""
        pricing = rule.get('pricing', {})
        discount_type = pricing.get('discount_type')
        discount_value = pricing.get('discount_value', 0)
        
        if discount_type == 'percentage':
            return subtotal * (discount_value / 100)
        elif discount_type == 'fixed_amount':
            return min(discount_value * quantity, subtotal)
        
        return 0
    
    # Invoicing & Payments
    def generate_invoice(self, order_id: str) -> str:
        """Generate invoice from sales order"""
        if order_id not in self.sales_orders:
            return None
        
        order = self.sales_orders[order_id]
        
        invoice_id = str(uuid.uuid4())
        invoice = {
            'invoice_id': invoice_id,
            'invoice_number': f"INV-{datetime.now().strftime('%Y%m%d')}-{invoice_id[:8]}",
            'company_id': order['company_id'],
            'customer_id': order['customer_id'],
            'order_id': order_id,
            'invoice_date': datetime.now().isoformat(),
            'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'items': order['items'].copy(),
            'subtotal': order['subtotal'],
            'tax_amount': order['tax_amount'],
            'total_amount': order['total_amount'],
            'payment_status': 'pending',
            'paid_amount': 0,
            'payment_history': []
        }
        
        self.invoices[invoice_id] = invoice
        self.save_data('invoices.json', self.invoices)
        
        # Update order status
        order['status'] = 'invoiced'
        self.save_data('sales_orders.json', self.sales_orders)
        
        return invoice_id
    
    def record_payment(self, invoice_id: str, payment_data: Dict[str, Any]) -> str:
        """Record payment against invoice"""
        if invoice_id not in self.invoices:
            return None
        
        invoice = self.invoices[invoice_id]
        payment_id = str(uuid.uuid4())
        
        payment_record = {
            'payment_id': payment_id,
            'invoice_id': invoice_id,
            'amount': payment_data.get('amount'),
            'payment_method': payment_data.get('method'),  # stripe, paypal, ach, check
            'payment_date': datetime.now().isoformat(),
            'reference_number': payment_data.get('reference_number'),
            'notes': payment_data.get('notes', '')
        }
        
        # Update invoice
        invoice['payment_history'].append(payment_record)
        invoice['paid_amount'] += payment_data.get('amount', 0)
        
        if invoice['paid_amount'] >= invoice['total_amount']:
            invoice['payment_status'] = 'paid'
        elif invoice['paid_amount'] > 0:
            invoice['payment_status'] = 'partial'
        
        self.invoices[invoice_id] = invoice
        self.save_data('invoices.json', self.invoices)
        
        # Store payment record
        if invoice['company_id'] not in self.payment_records:
            self.payment_records[invoice['company_id']] = []
        
        self.payment_records[invoice['company_id']].append(payment_record)
        self.save_data('payment_records.json', self.payment_records)
        
        return payment_id
    
    # Sales Reporting
    def get_sales_by_rep_report(self, company_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """Generate sales by rep report"""
        rep_sales = {}
        
        for order in self.sales_orders.values():
            if (order.get('company_id') == company_id and 
                date_from <= order.get('order_date', '') <= date_to):
                
                rep = order.get('sales_rep', 'Unassigned')
                
                if rep not in rep_sales:
                    rep_sales[rep] = {
                        'sales_rep': rep,
                        'order_count': 0,
                        'total_sales': 0,
                        'average_order_value': 0
                    }
                
                rep_sales[rep]['order_count'] += 1
                rep_sales[rep]['total_sales'] += order.get('total_amount', 0)
        
        # Calculate averages
        for rep_data in rep_sales.values():
            if rep_data['order_count'] > 0:
                rep_data['average_order_value'] = rep_data['total_sales'] / rep_data['order_count']
        
        return sorted(rep_sales.values(), key=lambda x: x['total_sales'], reverse=True)
    
    def get_profit_margin_report(self, company_id: str) -> Dict[str, Any]:
        """Calculate profit margins per order/product"""
        # This would integrate with cost data from ERP
        # For now, provide structure for profit analysis
        return {
            'company_id': company_id,
            'report_date': datetime.now().isoformat(),
            'overall_margin': 0,  # Would calculate from cost vs sale price
            'product_margins': [],  # Per product analysis
            'order_margins': []  # Per order analysis
        }
    
    def get_quotes_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all sales quotes for a company"""
        return [q for q in self.sales_quotes.values() if q.get('company_id') == company_id]
    
    def get_orders_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all sales orders for a company"""
        return [o for o in self.sales_orders.values() if o.get('company_id') == company_id]

# Global SalesPad instance
salespad_module = SalesPadModule()
