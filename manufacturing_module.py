
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from backup_service import auto_backup_trigger

class ManufacturingModule:
    """Manufacturing & Production module for QRLegends ERP Ultra"""
    
    def __init__(self):
        self.data_dir = 'data/manufacturing'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data storage
        self.bills_of_materials = self.load_data('bills_of_materials.json', {})
        self.production_orders = self.load_data('production_orders.json', {})
        self.work_centers = self.load_data('work_centers.json', {})
        self.quality_control = self.load_data('quality_control.json', {})
        self.machine_data = self.load_data('machine_data.json', {})
        self.production_schedules = self.load_data('production_schedules.json', {})
        
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

    def create_bill_of_materials(self, company_id: str, bom_data: Dict[str, Any]) -> str:
        """Create Bill of Materials for a product"""
        bom_id = str(uuid.uuid4())
        
        bom = {
            'bom_id': bom_id,
            'company_id': company_id,
            'product_id': bom_data.get('product_id'),
            'product_name': bom_data.get('product_name'),
            'version': bom_data.get('version', '1.0'),
            'components': bom_data.get('components', []),  # [{component_id, quantity, unit, cost}]
            'labor_requirements': bom_data.get('labor_requirements', []),
            'machine_requirements': bom_data.get('machine_requirements', []),
            'total_material_cost': self.calculate_material_cost(bom_data.get('components', [])),
            'estimated_labor_hours': bom_data.get('estimated_labor_hours', 0),
            'setup_time_minutes': bom_data.get('setup_time_minutes', 0),
            'production_time_minutes': bom_data.get('production_time_minutes', 0),
            'quality_checks': bom_data.get('quality_checks', []),
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.bills_of_materials[bom_id] = bom
        self.save_data('bills_of_materials.json', self.bills_of_materials)
        
        auto_backup_trigger.log_change(company_id, 'manufacturing_bom_created', {
            'bom_id': bom_id,
            'product_name': bom_data.get('product_name'),
            'action': 'create_bill_of_materials',
            'source': 'manufacturing'
        })
        
        return bom_id

    def create_production_order(self, company_id: str, order_data: Dict[str, Any]) -> str:
        """Create production order"""
        po_id = str(uuid.uuid4())
        
        production_order = {
            'production_order_id': po_id,
            'po_number': f"PO-{datetime.now().strftime('%Y%m%d')}-{po_id[:8]}",
            'company_id': company_id,
            'product_id': order_data.get('product_id'),
            'bom_id': order_data.get('bom_id'),
            'quantity_to_produce': order_data.get('quantity_to_produce'),
            'priority': order_data.get('priority', 'normal'),
            'scheduled_start': order_data.get('scheduled_start'),
            'scheduled_end': order_data.get('scheduled_end'),
            'actual_start': None,
            'actual_end': None,
            'work_center_id': order_data.get('work_center_id'),
            'assigned_operator': order_data.get('assigned_operator'),
            'material_allocations': [],
            'production_steps': self.generate_production_steps(order_data.get('bom_id')),
            'quality_checkpoints': [],
            'status': 'scheduled',  # scheduled, in_progress, completed, on_hold
            'completion_percentage': 0,
            'created_at': datetime.now().isoformat()
        }
        
        self.production_orders[po_id] = production_order
        self.save_data('production_orders.json', self.production_orders)
        
        return po_id

    def generate_production_steps(self, bom_id: str) -> List[Dict[str, Any]]:
        """Generate production steps from BOM"""
        if not bom_id or bom_id not in self.bills_of_materials:
            return []
        
        bom = self.bills_of_materials[bom_id]
        steps = []
        
        # Material preparation step
        steps.append({
            'step_id': str(uuid.uuid4()),
            'step_number': 1,
            'description': 'Material Preparation & Setup',
            'estimated_minutes': bom.get('setup_time_minutes', 30),
            'required_materials': bom.get('components', []),
            'quality_check_required': True,
            'status': 'pending'
        })
        
        # Production steps
        labor_reqs = bom.get('labor_requirements', [])
        for i, labor in enumerate(labor_reqs):
            steps.append({
                'step_id': str(uuid.uuid4()),
                'step_number': i + 2,
                'description': labor.get('operation', f'Production Step {i+1}'),
                'estimated_minutes': labor.get('time_minutes', 60),
                'skill_required': labor.get('skill_level'),
                'machine_required': labor.get('machine_id'),
                'quality_check_required': labor.get('quality_check', False),
                'status': 'pending'
            })
        
        # Final inspection
        steps.append({
            'step_id': str(uuid.uuid4()),
            'step_number': len(steps) + 1,
            'description': 'Final Quality Inspection & Packaging',
            'estimated_minutes': 15,
            'quality_check_required': True,
            'status': 'pending'
        })
        
        return steps

    def update_production_progress(self, po_id: str, step_id: str, status: str, actual_minutes: int = None) -> bool:
        """Update production step progress"""
        if po_id not in self.production_orders:
            return False
        
        production_order = self.production_orders[po_id]
        
        # Update step status
        for step in production_order['production_steps']:
            if step['step_id'] == step_id:
                step['status'] = status
                step['actual_minutes'] = actual_minutes
                step['completed_at'] = datetime.now().isoformat()
                break
        
        # Calculate overall completion
        total_steps = len(production_order['production_steps'])
        completed_steps = len([s for s in production_order['production_steps'] if s['status'] == 'completed'])
        completion_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        
        production_order['completion_percentage'] = completion_percentage
        
        # Update overall status
        if completion_percentage == 100:
            production_order['status'] = 'completed'
            production_order['actual_end'] = datetime.now().isoformat()
        elif completion_percentage > 0:
            production_order['status'] = 'in_progress'
            if not production_order['actual_start']:
                production_order['actual_start'] = datetime.now().isoformat()
        
        self.save_data('production_orders.json', self.production_orders)
        return True

    def record_quality_check(self, company_id: str, qc_data: Dict[str, Any]) -> str:
        """Record quality control inspection"""
        qc_id = str(uuid.uuid4())
        
        quality_record = {
            'qc_id': qc_id,
            'company_id': company_id,
            'production_order_id': qc_data.get('production_order_id'),
            'product_id': qc_data.get('product_id'),
            'inspector': qc_data.get('inspector'),
            'inspection_date': datetime.now().isoformat(),
            'inspection_type': qc_data.get('inspection_type'),  # incoming, in_process, final
            'test_results': qc_data.get('test_results', []),
            'measurements': qc_data.get('measurements', {}),
            'defects_found': qc_data.get('defects_found', []),
            'pass_fail_status': qc_data.get('pass_fail_status'),
            'notes': qc_data.get('notes', ''),
            'photos': qc_data.get('photos', []),
            'corrective_actions': qc_data.get('corrective_actions', [])
        }
        
        self.quality_control[qc_id] = quality_record
        self.save_data('quality_control.json', self.quality_control)
        
        return qc_id

    def calculate_material_cost(self, components: List[Dict[str, Any]]) -> float:
        """Calculate total material cost for BOM"""
        total_cost = 0
        for component in components:
            quantity = component.get('quantity', 0)
            unit_cost = component.get('unit_cost', 0)
            total_cost += quantity * unit_cost
        return total_cost

    def get_production_schedule(self, company_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Get production schedule with capacity planning"""
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        # Get scheduled production orders
        scheduled_orders = [
            order for order in self.production_orders.values()
            if (order.get('company_id') == company_id and 
                order.get('status') in ['scheduled', 'in_progress'] and
                order.get('scheduled_start') and
                datetime.fromisoformat(order['scheduled_start']) <= end_date)
        ]
        
        # Group by work center
        work_center_schedule = {}
        for order in scheduled_orders:
            wc_id = order.get('work_center_id', 'unassigned')
            if wc_id not in work_center_schedule:
                work_center_schedule[wc_id] = []
            work_center_schedule[wc_id].append(order)
        
        return {
            'schedule_date': datetime.now().isoformat(),
            'days_ahead': days_ahead,
            'total_orders': len(scheduled_orders),
            'work_center_schedule': work_center_schedule,
            'capacity_utilization': self.calculate_capacity_utilization(work_center_schedule)
        }

    def calculate_capacity_utilization(self, work_center_schedule: Dict[str, List]) -> Dict[str, float]:
        """Calculate capacity utilization per work center"""
        utilization = {}
        
        for wc_id, orders in work_center_schedule.items():
            total_scheduled_hours = 0
            for order in orders:
                # Sum estimated time for all production steps
                for step in order.get('production_steps', []):
                    total_scheduled_hours += step.get('estimated_minutes', 0) / 60
            
            # Assume 8 hours/day, 5 days/week capacity
            available_hours = 8 * 5 * 4  # 4 weeks
            utilization[wc_id] = (total_scheduled_hours / available_hours) * 100 if available_hours > 0 else 0
        
        return utilization

# Global Manufacturing instance
manufacturing_module = ManufacturingModule()
