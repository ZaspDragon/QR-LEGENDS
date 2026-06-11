import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from backup_service import auto_backup_trigger

class ERPCore:
    """ERP Core module for business-wide data, purchasing, and financial flows"""

    def __init__(self):
        self.data_dir = 'data/erp'
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize data storage
        self.customers = self.load_data('customers.json', {})
        self.suppliers = self.load_data('suppliers.json', {})
        self.item_master = self.load_data('item_master.json', {})
        self.chart_of_accounts = self.load_data('chart_of_accounts.json', {})
        self.purchase_orders = self.load_data('purchase_orders.json', {})
        self.supplier_invoices = self.load_data('supplier_invoices.json', {})
        self.financial_transactions = self.load_data('financial_transactions.json', [])
        self.receiving_transactions = self.load_data('receiving_transactions.json', {})
        self.in_transit_items = self.load_data('in_transit_items.json', {})
        self.receiving_variances = self.load_data('receiving_variances.json', {})

        # NEW: Receiving slot allocations and putaway assignments
        self.receiving_slot_allocations = self.load_data('receiving_slot_allocations.json', {})
        self.putaway_assignments = self.load_data('putaway_assignments.json', {})
        self.warehouse_slots = self.load_data('warehouse_slots.json', {})


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

    def save_data(self, filename: str, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False

    # Master Data Management
    def add_customer(self, company_id: str, customer_data: Dict[str, Any]) -> str:
        """Add new customer to database"""
        customer_id = str(uuid.uuid4())
        customer_record = {
            'customer_id': customer_id,
            'company_id': company_id,
            'company_name': customer_data.get('company_name'),
            'contact_info': {
                'primary_contact': customer_data.get('primary_contact'),
                'email': customer_data.get('email'),
                'phone': customer_data.get('phone'),
                'address': customer_data.get('address')
            },
            'credit_terms': customer_data.get('credit_terms', 'Net 30'),
            'credit_limit': customer_data.get('credit_limit', 0),
            'order_history': [],
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        self.customers[customer_id] = customer_record
        self.save_data('customers.json', self.customers)

        # Log change for backup
        auto_backup_trigger.log_change(company_id, 'customer_added', {
            'customer_id': customer_id,
            'company_name': customer_data.get('company_name'),
            'action': 'add_customer',
            'source': 'erp_core'
        })

        return customer_id

    def add_supplier(self, company_id: str, supplier_data: Dict[str, Any]) -> str:
        """Add new supplier to database"""
        supplier_id = str(uuid.uuid4())
        supplier_record = {
            'supplier_id': supplier_id,
            'company_id': company_id,
            'vendor_name': supplier_data.get('vendor_name'),
            'contact_info': {
                'primary_contact': supplier_data.get('primary_contact'),
                'email': supplier_data.get('email'),
                'phone': supplier_data.get('phone'),
                'address': supplier_data.get('address')
            },
            'payment_terms': supplier_data.get('payment_terms', 'Net 30'),
            'product_catalog': supplier_data.get('product_catalog', []),
            'performance_metrics': {
                'on_time_delivery_rate': 100.0,
                'defect_rate': 0.0,
                'total_orders': 0,
                'on_time_orders': 0
            },
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        self.suppliers[supplier_id] = supplier_record
        self.save_data('suppliers.json', self.suppliers)

        # Log change for backup
        auto_backup_trigger.log_change(company_id, 'supplier_added', {
            'supplier_id': supplier_id,
            'vendor_name': supplier_data.get('vendor_name'),
            'action': 'add_supplier',
            'source': 'erp_core'
        })

        return supplier_id

    def add_item_master(self, company_id: str, item_data: Dict[str, Any]) -> str:
        """Add item to master catalog"""
        item_id = str(uuid.uuid4())
        item_record = {
            'item_id': item_id,
            'company_id': company_id,
            'sku': item_data.get('sku'),
            'barcode_qr': item_data.get('barcode_qr'),
            'item_name': item_data.get('item_name'),
            'description': item_data.get('description'),
            'dimensions': {
                'length': item_data.get('length', 0),
                'width': item_data.get('width', 0),
                'height': item_data.get('height', 0),
                'weight': item_data.get('weight', 0)
            },
            'cost_info': {
                'unit_cost': item_data.get('unit_cost', 0),
                'landed_cost': item_data.get('landed_cost', 0),
                'default_supplier_id': item_data.get('default_supplier_id')
            },
            'category': item_data.get('category'),
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        self.item_master[item_id] = item_record
        self.save_data('item_master.json', self.item_master)

        # Log change for backup
        auto_backup_trigger.log_change(company_id, 'item_master_added', {
            'item_id': item_id,
            'item_name': item_data.get('item_name'),
            'sku': item_data.get('sku'),
            'action': 'add_item_master',
            'source': 'erp_core'
        })

        return item_id

    # Procurement & Supply Chain
    def create_purchase_order(self, company_id: str, po_data: Dict[str, Any]) -> str:
        """Create purchase order"""
        po_id = str(uuid.uuid4())
        
        # Get supplier name if supplier_id is provided
        supplier_name = 'Unknown Supplier'
        supplier_id = po_data.get('supplier_id')
        if supplier_id and supplier_id in self.suppliers:
            supplier_name = self.suppliers[supplier_id].get('vendor_name', 'Unknown Supplier')
        
        po_record = {
            'po_id': po_id,
            'po_number': po_data.get('po_number', f"PO-{datetime.now().strftime('%Y%m%d')}-{po_id[:8]}"),
            'company_id': company_id,
            'supplier_id': supplier_id,
            'supplier_name': supplier_name,
            'order_date': datetime.now().isoformat(),
            'expected_delivery': po_data.get('expected_delivery'),
            'items': po_data.get('items', []),  # [{item_id, quantity, unit_price}]
            'subtotal': po_data.get('subtotal', 0),
            'freight_cost': po_data.get('freight_cost', 0),
            'tax_amount': po_data.get('tax_amount', 0),
            'total_amount': po_data.get('total_amount', 0),
            'status': 'pending_approval',
            'approval_workflow': {
                'created_by': po_data.get('created_by'),
                'approved_by': None,
                'approval_date': None
            },
            'receiving_status': 'pending'
        }

        self.purchase_orders[po_id] = po_record
        self.save_data('purchase_orders.json', self.purchase_orders)

        # Log change for backup
        auto_backup_trigger.log_change(company_id, 'purchase_order_created', {
            'po_id': po_id,
            'po_number': po_record['po_number'],
            'supplier_id': po_data.get('supplier_id'),
            'total_amount': po_data.get('total_amount', 0),
            'action': 'create_purchase_order',
            'source': 'erp_core'
        })

        # NEW: Trigger slot allocation when PO is created
        if po_data.get('items'):
            self.allocate_receiving_slot(po_record['po_number'], company_id, po_data['items'])

        return po_id

    def approve_purchase_order(self, po_id: str, approved_by: str) -> bool:
        """Approve purchase order"""
        if po_id in self.purchase_orders:
            self.purchase_orders[po_id]['status'] = 'approved'
            self.purchase_orders[po_id]['approval_workflow']['approved_by'] = approved_by
            self.purchase_orders[po_id]['approval_workflow']['approval_date'] = datetime.now().isoformat()
            self.purchase_orders[po_id]['receiving_status'] = 'pending' # Ready for receiving

            self.save_data('purchase_orders.json', self.purchase_orders)

            # Log change for backup
            auto_backup_trigger.log_change(
                self.purchase_orders[po_id]['company_id'],
                'purchase_order_approved',
                {
                    'po_id': po_id,
                    'approved_by': approved_by,
                    'action': 'approve_purchase_order',
                    'source': 'erp_core'
                }
            )

            # NEW: Trigger slot allocation upon PO approval if not already done
            po_data = self.purchase_orders[po_id]
            if po_data.get('items') and not self.find_allocation_by_po(po_data['po_number']):
                self.allocate_receiving_slot(po_data['po_number'], po_data['company_id'], po_data['items'])


            return True
        return False

    def update_supplier_performance(self, supplier_id: str, delivery_on_time: bool, defects: int = 0):
        """Update supplier performance metrics"""
        if supplier_id in self.suppliers:
            metrics = self.suppliers[supplier_id]['performance_metrics']
            metrics['total_orders'] += 1

            if delivery_on_time:
                metrics['on_time_orders'] += 1

            metrics['on_time_delivery_rate'] = (metrics['on_time_orders'] / metrics['total_orders']) * 100

            if defects > 0:
                # Simple defect rate calculation
                metrics['defect_rate'] = min(metrics['defect_rate'] + (defects * 0.1), 100.0)

            self.save_data('suppliers.json', self.suppliers)

    # Financial Integration
    def record_financial_transaction(self, company_id: str, transaction_data: Dict[str, Any]) -> str:
        """Record financial transaction"""
        transaction_id = str(uuid.uuid4())
        transaction = {
            'transaction_id': transaction_id,
            'company_id': company_id,
            'transaction_type': transaction_data.get('type'),  # 'sale', 'purchase', 'payment', 'receipt'
            'amount': transaction_data.get('amount'),
            'reference_id': transaction_data.get('reference_id'),  # PO ID, Invoice ID, etc.
            'account_code': transaction_data.get('account_code'),
            'description': transaction_data.get('description'),
            'transaction_date': datetime.now().isoformat(),
            'created_by': transaction_data.get('created_by')
        }

        self.financial_transactions.append(transaction)
        self.save_data('financial_transactions.json', self.financial_transactions)

        # Log change for backup
        auto_backup_trigger.log_change(company_id, 'financial_transaction', {
            'transaction_id': transaction_id,
            'type': transaction_data.get('type'),
            'amount': transaction_data.get('amount'),
            'action': 'record_financial_transaction',
            'source': 'erp_core'
        })

        return transaction_id

    # Receiving Transactions
    def add_receiving_transaction(self, company_id: str, transaction_data: Dict[str, Any]) -> str:
        """Add a new receiving transaction"""
        transaction_id = f"RCV{datetime.now().strftime('%Y%m%d')}-{len(self.receiving_transactions) + 1:06d}"

        transaction = {
            'id': transaction_id,
            'company_id': company_id,
            'date': transaction_data.get('date', datetime.now().isoformat()),
            'po_number': transaction_data.get('po_number'),
            'supplier_id': transaction_data.get('supplier_id'),
            'items': transaction_data.get('items', []),
            'received_by': transaction_data.get('received_by'),
            'total_value': transaction_data.get('total_value', 0),
            'status': transaction_data.get('status', 'completed'),
            'notes': transaction_data.get('notes', ''),
            'created_at': datetime.now().isoformat()
        }

        self.receiving_transactions[transaction_id] = transaction
        self.save_data('receiving_transactions.json', self.receiving_transactions)

        # Update inventory based on received items
        for item in transaction['items']:
            self.update_inventory_from_receiving(company_id, item)

        return transaction_id

    def get_receiving_transactions_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all receiving transactions for a company"""
        return [
            transaction for transaction in self.receiving_transactions.values()
            if transaction.get('company_id') == company_id
        ]

    def add_in_transit_item(self, company_id: str, item_data: Dict[str, Any]) -> str:
        """Add an item to in-transit tracking"""
        item_id = f"IT{datetime.now().strftime('%Y%m%d')}-{len(self.in_transit_items) + 1:06d}"

        item = {
            'id': item_id,
            'company_id': company_id,
            'po_number': item_data.get('po_number'),
            'item_number': item_data.get('item_number'),
            'description': item_data.get('description'),
            'quantity': item_data.get('quantity'),
            'supplier_id': item_data.get('supplier_id'),
            'ship_date': item_data.get('ship_date'),
            'expected_date': item_data.get('expected_date'),
            'carrier': item_data.get('carrier'),
            'tracking_number': item_data.get('tracking_number'),
            'status': item_data.get('status', 'shipped'),
            'created_at': datetime.now().isoformat()
        }

        self.in_transit_items[item_id] = item
        self.save_data('in_transit_items.json', self.in_transit_items)

        return item_id

    def get_in_transit_items_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all in-transit items for a company"""
        return [
            item for item in self.in_transit_items.values()
            if item.get('company_id') == company_id
        ]

    def update_in_transit_status(self, item_id: str, new_status: str) -> bool:
        """Update the status of an in-transit item"""
        if item_id in self.in_transit_items:
            self.in_transit_items[item_id]['status'] = new_status
            self.in_transit_items[item_id]['updated_at'] = datetime.now().isoformat()
            self.save_data('in_transit_items.json', self.in_transit_items)
            return True
        return False

    def update_inventory_from_receiving(self, company_id: str, item_data: Dict[str, Any]):
        """Update inventory quantities based on received items"""
        item_number = item_data.get('item_number')
        received_qty = item_data.get('received_qty', 0)

        # Find the item in item master
        for item_id, item in self.item_master.items():
            if (item.get('company_id') == company_id and
                item.get('item_number') == item_number): # Assuming item_number is a key in item_data and item_master

                current_qty = item.get('quantity_on_hand', 0)
                item['quantity_on_hand'] = current_qty + received_qty
                item['last_received'] = datetime.now().isoformat()
                break

        self.save_data('item_master.json', self.item_master)

    def record_receiving_variance(self, company_id: str, variance_data: Dict[str, Any]) -> str:
        """Record a receiving variance"""
        variance_id = f"VAR{datetime.now().strftime('%Y%m%d')}-{len(self.receiving_variances) + 1:06d}"

        variance = {
            'id': variance_id,
            'company_id': company_id,
            'date': variance_data.get('date', datetime.now().isoformat()),
            'po_number': variance_data.get('po_number'),
            'item_number': variance_data.get('item_number'),
            'expected_qty': variance_data.get('expected_qty'),
            'received_qty': variance_data.get('received_qty'),
            'variance': variance_data.get('variance'),
            'variance_percent': variance_data.get('variance_percent'),
            'reason': variance_data.get('reason'),
            'status': variance_data.get('status', 'pending_review'),
            'created_at': datetime.now().isoformat()
        }

        self.receiving_variances[variance_id] = variance
        self.save_data('receiving_variances.json', self.receiving_variances)

        return variance_id


    # NEW: Receiving slot allocation methods
    def allocate_receiving_slot(self, po_number: str, company_id: str, items: List[Dict]) -> Dict[str, Any]:
        """Pre-allocate receiving slots when PO is created/approved"""
        allocation_id = f"RSA-{datetime.now().strftime('%Y%m%d')}-{len(self.receiving_slot_allocations) + 1:06d}"

        # Find available receiving slots
        available_slots = self.get_available_receiving_slots(company_id)

        slot_assignments = []
        for item in items:
            # Determine slot based on item characteristics
            required_slot_type = self.determine_slot_type(item)
            allocated_slot = self.find_best_slot(available_slots, required_slot_type, item.get('quantity', 0))

            if allocated_slot:
                slot_assignments.append({
                    'item_number': item.get('item_number'),
                    'description': item.get('description'),
                    'expected_qty': item.get('quantity', 0),
                    'allocated_slot': allocated_slot['slot_id'],
                    'slot_type': allocated_slot['slot_type'],
                    'capacity': allocated_slot['capacity']
                })
                # Mark slot as reserved
                available_slots.remove(allocated_slot)

        allocation = {
            'allocation_id': allocation_id,
            'po_number': po_number,
            'company_id': company_id,
            'status': 'allocated',
            'allocated_date': datetime.now().isoformat(),
            'expected_arrival': self.get_po_expected_date(po_number),
            'slot_assignments': slot_assignments,
            'notes': f"Auto-allocated for PO {po_number}"
        }

        self.receiving_slot_allocations[allocation_id] = allocation
        self.save_data('receiving_slot_allocations.json', self.receiving_slot_allocations)

        return allocation

    def record_received_items(self, po_number: str, company_id: str, received_items: List[Dict], received_by: str) -> Dict[str, Any]:
        """Record items as received and create putaway assignments"""
        transaction_id = f"RCV-{datetime.now().strftime('%Y%m%d')}-{len(self.receiving_transactions) + 1:06d}"

        # Find the slot allocation for this PO
        allocation = self.find_allocation_by_po(po_number)

        receiving_details = []
        putaway_tasks = []

        for received_item in received_items:
            item_number = received_item.get('item_number')
            received_qty = received_item.get('received_qty', 0)

            # Find the allocated slot for this item
            allocated_slot = None
            if allocation:
                for assignment in allocation.get('slot_assignments', []):
                    if assignment['item_number'] == item_number:
                        allocated_slot = assignment['allocated_slot']
                        break

            # Record variance if quantities don't match
            expected_qty = received_item.get('expected_qty', 0)
            variance = received_qty - expected_qty

            receiving_detail = {
                'item_number': item_number,
                'description': received_item.get('description'),
                'expected_qty': expected_qty,
                'received_qty': received_qty,
                'variance': variance,
                'receiving_slot': allocated_slot,
                'condition': received_item.get('condition', 'good'),
                'lot_number': received_item.get('lot_number'),
                'expiry_date': received_item.get('expiry_date')
            }
            receiving_details.append(receiving_detail)

            # Create putaway assignment
            if received_qty > 0:
                putaway_task = self.create_putaway_assignment(
                    item_number, received_qty, allocated_slot,
                    transaction_id, company_id, received_item
                )
                putaway_tasks.append(putaway_task)

        # Create receiving transaction record
        transaction = {
            'transaction_id': transaction_id,
            'po_number': po_number,
            'company_id': company_id,
            'received_date': datetime.now().isoformat(),
            'received_by': received_by,
            'status': 'received',
            'items': receiving_details,
            'putaway_assignments': [task['assignment_id'] for task in putaway_tasks],
            'total_items': len(receiving_details),
            'variance_count': len([item for item in receiving_details if item['variance'] != 0])
        }

        self.receiving_transactions[transaction_id] = transaction
        self.save_data('receiving_transactions.json', self.receiving_transactions)

        # Update PO receiving status
        if po_number in self.purchase_orders:
            self.purchase_orders[po_number]['receiving_status'] = 'received'
            self.save_data('purchase_orders.json', self.purchase_orders)

        return {
            'transaction': transaction,
            'putaway_tasks': putaway_tasks
        }

    def create_putaway_assignment(self, item_number: str, quantity: int, from_slot: str,
                                transaction_id: str, company_id: str, item_details: Dict) -> Dict[str, Any]:
        """Create putaway assignment to move items from receiving to storage"""
        assignment_id = f"PUT-{datetime.now().strftime('%Y%m%d')}-{len(self.putaway_assignments) + 1:06d}"

        # Determine best storage location
        target_location = self.find_optimal_storage_location(item_number, quantity, company_id)

        assignment = {
            'assignment_id': assignment_id,
            'transaction_id': transaction_id,
            'company_id': company_id,
            'item_number': item_number,
            'description': item_details.get('description'),
            'quantity': quantity,
            'from_location': from_slot,
            'to_location': target_location,
            'status': 'pending',
            'priority': self.calculate_putaway_priority(item_details),
            'created_date': datetime.now().isoformat(),
            'assigned_to': None,
            'completed_date': None,
            'notes': f"Putaway from receiving transaction {transaction_id}"
        }

        self.putaway_assignments[assignment_id] = assignment
        self.save_data('putaway_assignments.json', self.putaway_assignments)

        return assignment

    def get_available_receiving_slots(self, company_id: str) -> List[Dict]:
        """Get list of available receiving dock slots"""
        # Initialize default slots if none exist
        if not self.warehouse_slots:
            self.initialize_default_slots(company_id)

        available_slots = []
        for slot_id, slot in self.warehouse_slots.items():
            if (slot.get('company_id') == company_id and
                slot.get('zone') == 'receiving' and
                slot.get('status') == 'available'):
                available_slots.append(slot)

        return available_slots

    def initialize_default_slots(self, company_id: str):
        """Initialize default warehouse slots"""
        receiving_slots = [
            {'slot_id': f'RCV-DOCK-{i:02d}', 'slot_type': 'standard', 'capacity': 50}
            for i in range(1, 11)
        ]
        receiving_slots.extend([
            {'slot_id': f'RCV-BULK-{i:02d}', 'slot_type': 'bulk', 'capacity': 200}
            for i in range(1, 4)
        ])

        for slot_config in receiving_slots:
            slot_id = f"{company_id}-{slot_config['slot_id']}"
            self.warehouse_slots[slot_id] = {
                'slot_id': slot_id,
                'company_id': company_id,
                'zone': 'receiving',
                'slot_type': slot_config['slot_type'],
                'capacity': slot_config['capacity'],
                'current_occupancy': 0,
                'status': 'available',
                'location_details': {
                    'aisle': 'RCV',
                    'bay': slot_config['slot_id'].split('-')[-1],
                    'level': '1'
                }
            }

        self.save_data('warehouse_slots.json', self.warehouse_slots)

    def determine_slot_type(self, item: Dict) -> str:
        """Determine what type of receiving slot an item needs"""
        quantity = item.get('quantity', 0)
        item_type = item.get('category', '').lower()

        if quantity > 100 or 'bulk' in item_type:
            return 'bulk'
        elif 'hazardous' in item_type or 'chemical' in item_type:
            return 'hazmat'
        else:
            return 'standard'

    def find_best_slot(self, available_slots: List[Dict], required_type: str, quantity: int) -> Optional[Dict]:
        """Find the best available slot for an item"""
        suitable_slots = [
            slot for slot in available_slots
            if slot['slot_type'] == required_type and slot['capacity'] >= quantity
        ]

        if not suitable_slots:
            # Fallback to any available slot with sufficient capacity
            suitable_slots = [
                slot for slot in available_slots
                if slot['capacity'] >= quantity
            ]

        return suitable_slots[0] if suitable_slots else None

    def find_allocation_by_po(self, po_number: str) -> Optional[Dict]:
        """Find slot allocation for a purchase order"""
        for allocation in self.receiving_slot_allocations.values():
            if allocation.get('po_number') == po_number:
                return allocation
        return None

    def find_optimal_storage_location(self, item_number: str, quantity: int, company_id: str) -> str:
        """Find optimal storage location for putaway"""
        # This would integrate with your existing inventory location logic
        # For now, return a default location pattern
        return f"A-{item_number[-2:]}-01"

    def calculate_putaway_priority(self, item_details: Dict) -> int:
        """Calculate putaway priority (1=highest, 5=lowest)"""
        category = item_details.get('category', '').lower()

        if 'perishable' in category or 'refrigerated' in category:
            return 1
        elif 'fast_moving' in category:
            return 2
        elif 'hazardous' in category:
            return 1
        else:
            return 3

    def get_po_expected_date(self, po_number: str) -> str:
        """Get expected delivery date for PO"""
        for po in self.purchase_orders.values():
            if po.get('po_number') == po_number: # Changed key from 'id' to 'po_number'
                return po.get('expected_delivery', datetime.now().isoformat())
        return datetime.now().isoformat()


    # Reporting & Analytics
    def get_purchase_vs_usage_report(self, company_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate purchase vs usage trend report"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get recent purchase orders
        recent_pos = [
            po for po in self.purchase_orders.values()
            if (po.get('company_id') == company_id and
                datetime.fromisoformat(po['order_date']) > cutoff_date)
        ]

        # Calculate totals
        total_purchased = sum(po.get('total_amount', 0) for po in recent_pos)

        # Get financial transactions for usage estimation
        recent_transactions = [
            t for t in self.financial_transactions
            if (t.get('company_id') == company_id and
                datetime.fromisoformat(t['transaction_date']) > cutoff_date and
                t.get('transaction_type') == 'sale')
        ]

        total_sales = sum(t.get('amount', 0) for t in recent_transactions)

        return {
            'report_period_days': days,
            'total_purchased': total_purchased,
            'total_sales': total_sales,
            'purchase_orders_count': len(recent_pos),
            'sales_transactions_count': len(recent_transactions),
            'purchase_to_sales_ratio': total_purchased / max(total_sales, 1),
            'generated_at': datetime.now().isoformat()
        }

    def get_supplier_spend_analysis(self, company_id: str) -> List[Dict[str, Any]]:
        """Generate supplier spend analysis"""
        supplier_spend = {}

        for po in self.purchase_orders.values():
            if po.get('company_id') == company_id:
                supplier_id = po.get('supplier_id')
                if supplier_id:
                    if supplier_id not in supplier_spend:
                        supplier_info = self.suppliers.get(supplier_id, {})
                        supplier_spend[supplier_id] = {
                            'supplier_id': supplier_id,
                            'vendor_name': supplier_info.get('vendor_name', 'Unknown'),
                            'total_spend': 0,
                            'order_count': 0,
                            'average_order_value': 0,
                            'performance_metrics': supplier_info.get('performance_metrics', {})
                        }

                    supplier_spend[supplier_id]['total_spend'] += po.get('total_amount', 0)
                    supplier_spend[supplier_id]['order_count'] += 1

        # Calculate averages
        for supplier_data in supplier_spend.values():
            if supplier_data['order_count'] > 0:
                supplier_data['average_order_value'] = supplier_data['total_spend'] / supplier_data['order_count']

        # Sort by total spend (descending)
        return sorted(supplier_spend.values(), key=lambda x: x['total_spend'], reverse=True)

    def get_company_erp_data(self, company_id: str) -> Dict[str, Any]:
        """Get ERP data for a specific company"""
        return {
            'customers': self.get_customers_by_company(company_id),
            'suppliers': self.get_suppliers_by_company(company_id),
            'items': self.get_items_by_company(company_id),
            'purchase_orders': self.get_purchase_orders_by_company(company_id),
            'financial_summary': self.get_financial_summary(company_id),
            'receiving_transactions': self.get_receiving_transactions_by_company(company_id),
            'in_transit_items': self.get_in_transit_items_by_company(company_id),
            'receiving_slot_allocations': self.get_receiving_slot_allocations(company_id),
            'putaway_assignments': self.get_pending_putaway_tasks(company_id)
        }

    # Helper methods for get_company_erp_data (assuming these exist in the original code or are implied)
    def get_customers_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        return [c for c in self.customers.values() if c.get('company_id') == company_id]

    def get_suppliers_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        return [s for s in self.suppliers.values() if s.get('company_id') == company_id]

    def get_items_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        return [i for i in self.item_master.values() if i.get('company_id') == company_id]

    def get_purchase_orders_by_company(self, company_id: str) -> List[Dict[str, Any]]:
        return [po for po in self.purchase_orders.values() if po.get('company_id') == company_id]

    def get_financial_summary(self, company_id: str) -> Dict[str, Any]:
        # This is a placeholder, a real implementation would aggregate financial data
        total_in = sum(t['amount'] for t in self.financial_transactions if t.get('company_id') == company_id and t.get('transaction_type') in ['receipt', 'sale'])
        total_out = sum(t['amount'] for t in self.financial_transactions if t.get('company_id') == company_id and t.get('transaction_type') in ['purchase', 'payment'])
        return {'total_income': total_in, 'total_expenses': total_out}

    # NEW: Additional methods for new functionalities
    def get_pending_putaway_tasks(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all pending putaway assignments"""
        return [
            task for task in self.putaway_assignments.values()
            if task.get('company_id') == company_id and task.get('status') == 'pending'
        ]

    def get_receiving_slot_allocations(self, company_id: str) -> List[Dict[str, Any]]:
        """Get all slot allocations for a company"""
        return [
            allocation for allocation in self.receiving_slot_allocations.values()
            if allocation.get('company_id') == company_id
        ]

    def update_putaway_status(self, assignment_id: str, status: str, assigned_to: str = None) -> bool:
        """Update putaway assignment status"""
        if assignment_id in self.putaway_assignments:
            self.putaway_assignments[assignment_id]['status'] = status
            if assigned_to:
                self.putaway_assignments[assignment_id]['assigned_to'] = assigned_to
            if status == 'completed':
                self.putaway_assignments[assignment_id]['completed_date'] = datetime.now().isoformat()

            self.save_data('putaway_assignments.json', self.putaway_assignments)
            return True
        return False

    # Update/Delete methods for master data
    def update_customer(self, customer_id: str, company_id: str, customer_data: Dict[str, Any]) -> bool:
        """Update existing customer"""
        if customer_id not in self.customers:
            return False
        
        if self.customers[customer_id].get('company_id') != company_id:
            return False
        
        self.customers[customer_id].update({
            'company_name': customer_data.get('company_name', self.customers[customer_id].get('company_name')),
            'contact_info': {
                'primary_contact': customer_data.get('primary_contact', self.customers[customer_id].get('contact_info', {}).get('primary_contact')),
                'email': customer_data.get('email', self.customers[customer_id].get('contact_info', {}).get('email')),
                'phone': customer_data.get('phone', self.customers[customer_id].get('contact_info', {}).get('phone')),
                'address': customer_data.get('address', self.customers[customer_id].get('contact_info', {}).get('address'))
            },
            'credit_terms': customer_data.get('credit_terms', self.customers[customer_id].get('credit_terms')),
            'credit_limit': customer_data.get('credit_limit', self.customers[customer_id].get('credit_limit')),
            'status': customer_data.get('status', self.customers[customer_id].get('status')),
            'updated_at': datetime.now().isoformat()
        })
        
        self.save_data('customers.json', self.customers)
        auto_backup_trigger.log_change(company_id, 'customer_updated', {
            'customer_id': customer_id,
            'action': 'update_customer'
        })
        return True

    def delete_customer(self, customer_id: str, company_id: str) -> bool:
        """Delete customer (soft delete by setting status to 'deleted')"""
        if customer_id not in self.customers:
            return False
        
        if self.customers[customer_id].get('company_id') != company_id:
            return False
        
        self.customers[customer_id]['status'] = 'deleted'
        self.customers[customer_id]['deleted_at'] = datetime.now().isoformat()
        
        self.save_data('customers.json', self.customers)
        auto_backup_trigger.log_change(company_id, 'customer_deleted', {
            'customer_id': customer_id,
            'action': 'delete_customer'
        })
        return True

    def update_supplier(self, supplier_id: str, company_id: str, supplier_data: Dict[str, Any]) -> bool:
        """Update existing supplier"""
        if supplier_id not in self.suppliers:
            return False
        
        if self.suppliers[supplier_id].get('company_id') != company_id:
            return False
        
        self.suppliers[supplier_id].update({
            'vendor_name': supplier_data.get('vendor_name', self.suppliers[supplier_id].get('vendor_name')),
            'contact_info': {
                'primary_contact': supplier_data.get('primary_contact', self.suppliers[supplier_id].get('contact_info', {}).get('primary_contact')),
                'email': supplier_data.get('email', self.suppliers[supplier_id].get('contact_info', {}).get('email')),
                'phone': supplier_data.get('phone', self.suppliers[supplier_id].get('contact_info', {}).get('phone')),
                'address': supplier_data.get('address', self.suppliers[supplier_id].get('contact_info', {}).get('address'))
            },
            'payment_terms': supplier_data.get('payment_terms', self.suppliers[supplier_id].get('payment_terms')),
            'product_catalog': supplier_data.get('product_catalog', self.suppliers[supplier_id].get('product_catalog')),
            'status': supplier_data.get('status', self.suppliers[supplier_id].get('status')),
            'updated_at': datetime.now().isoformat()
        })
        
        self.save_data('suppliers.json', self.suppliers)
        auto_backup_trigger.log_change(company_id, 'supplier_updated', {
            'supplier_id': supplier_id,
            'action': 'update_supplier'
        })
        return True

    def delete_supplier(self, supplier_id: str, company_id: str) -> bool:
        """Delete supplier (soft delete)"""
        if supplier_id not in self.suppliers:
            return False
        
        if self.suppliers[supplier_id].get('company_id') != company_id:
            return False
        
        self.suppliers[supplier_id]['status'] = 'deleted'
        self.suppliers[supplier_id]['deleted_at'] = datetime.now().isoformat()
        
        self.save_data('suppliers.json', self.suppliers)
        auto_backup_trigger.log_change(company_id, 'supplier_deleted', {
            'supplier_id': supplier_id,
            'action': 'delete_supplier'
        })
        return True

    def update_item_master(self, item_id: str, company_id: str, item_data: Dict[str, Any]) -> bool:
        """Update existing item in master catalog"""
        if item_id not in self.item_master:
            return False
        
        if self.item_master[item_id].get('company_id') != company_id:
            return False
        
        self.item_master[item_id].update({
            'sku': item_data.get('sku', self.item_master[item_id].get('sku')),
            'barcode_qr': item_data.get('barcode_qr', self.item_master[item_id].get('barcode_qr')),
            'item_name': item_data.get('item_name', self.item_master[item_id].get('item_name')),
            'description': item_data.get('description', self.item_master[item_id].get('description')),
            'dimensions': {
                'length': item_data.get('length', self.item_master[item_id].get('dimensions', {}).get('length', 0)),
                'width': item_data.get('width', self.item_master[item_id].get('dimensions', {}).get('width', 0)),
                'height': item_data.get('height', self.item_master[item_id].get('dimensions', {}).get('height', 0)),
                'weight': item_data.get('weight', self.item_master[item_id].get('dimensions', {}).get('weight', 0))
            },
            'cost_info': {
                'unit_cost': item_data.get('unit_cost', self.item_master[item_id].get('cost_info', {}).get('unit_cost', 0)),
                'landed_cost': item_data.get('landed_cost', self.item_master[item_id].get('cost_info', {}).get('landed_cost', 0)),
                'default_supplier_id': item_data.get('default_supplier_id', self.item_master[item_id].get('cost_info', {}).get('default_supplier_id'))
            },
            'category': item_data.get('category', self.item_master[item_id].get('category')),
            'status': item_data.get('status', self.item_master[item_id].get('status')),
            'updated_at': datetime.now().isoformat()
        })
        
        self.save_data('item_master.json', self.item_master)
        auto_backup_trigger.log_change(company_id, 'item_master_updated', {
            'item_id': item_id,
            'action': 'update_item_master'
        })
        return True

    def delete_item_master(self, item_id: str, company_id: str) -> bool:
        """Delete item from master catalog (soft delete)"""
        if item_id not in self.item_master:
            return False
        
        if self.item_master[item_id].get('company_id') != company_id:
            return False
        
        self.item_master[item_id]['status'] = 'deleted'
        self.item_master[item_id]['deleted_at'] = datetime.now().isoformat()
        
        self.save_data('item_master.json', self.item_master)
        auto_backup_trigger.log_change(company_id, 'item_master_deleted', {
            'item_id': item_id,
            'action': 'delete_item_master'
        })
        return True

# Global ERP instance
erp_core = ERPCore()