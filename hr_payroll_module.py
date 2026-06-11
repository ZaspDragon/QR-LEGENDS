
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from backup_service import auto_backup_trigger

class HRPayrollModule:
    """Human Resources & Payroll module for QRLegends ERP Ultra"""
    
    def __init__(self):
        self.data_dir = 'data/hr_payroll'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data storage
        self.employee_records = self.load_data('employee_records.json', {})
        self.payroll_records = self.load_data('payroll_records.json', {})
        self.time_attendance = self.load_data('time_attendance.json', {})
        self.benefits_plans = self.load_data('benefits_plans.json', {})
        self.performance_reviews = self.load_data('performance_reviews.json', {})
        self.training_records = self.load_data('training_records.json', {})
        self.workforce_planning = self.load_data('workforce_planning.json', {})
        
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

    def create_employee_record(self, company_id: str, employee_data: Dict[str, Any]) -> str:
        """Create comprehensive employee record"""
        employee_id = str(uuid.uuid4())
        
        record = {
            'employee_id': employee_id,
            'company_id': company_id,
            'personal_info': {
                'first_name': employee_data.get('first_name'),
                'last_name': employee_data.get('last_name'),
                'email': employee_data.get('email'),
                'phone': employee_data.get('phone'),
                'address': employee_data.get('address'),
                'emergency_contact': employee_data.get('emergency_contact')
            },
            'employment_info': {
                'hire_date': employee_data.get('hire_date', datetime.now().isoformat()),
                'position': employee_data.get('position'),
                'department': employee_data.get('department'),
                'manager_id': employee_data.get('manager_id'),
                'employment_type': employee_data.get('employment_type', 'full_time'),
                'salary': employee_data.get('salary', 0),
                'pay_frequency': employee_data.get('pay_frequency', 'bi_weekly')
            },
            'benefits': {
                'health_plan': employee_data.get('health_plan'),
                'dental_plan': employee_data.get('dental_plan'),
                'vision_plan': employee_data.get('vision_plan'),
                'retirement_plan': employee_data.get('retirement_plan'),
                'vacation_days': employee_data.get('vacation_days', 15),
                'sick_days': employee_data.get('sick_days', 10)
            },
            'tax_info': {
                'tax_id': employee_data.get('tax_id'),
                'filing_status': employee_data.get('filing_status'),
                'allowances': employee_data.get('allowances', 0),
                'state': employee_data.get('state')
            },
            'onboarding_status': 'pending',
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.employee_records[employee_id] = record
        self.save_data('employee_records.json', self.employee_records)
        
        auto_backup_trigger.log_change(company_id, 'hr_employee_created', {
            'employee_id': employee_id,
            'name': f"{employee_data.get('first_name')} {employee_data.get('last_name')}",
            'action': 'create_employee_record',
            'source': 'hr_payroll'
        })
        
        return employee_id

    def process_payroll(self, company_id: str, pay_period_start: str, pay_period_end: str) -> str:
        """Process payroll for all employees"""
        payroll_id = str(uuid.uuid4())
        
        # Get all employees for company
        company_employees = [
            emp for emp in self.employee_records.values()
            if emp.get('company_id') == company_id and emp.get('status') == 'active'
        ]
        
        payroll_records = []
        total_gross = 0
        total_net = 0
        
        for employee in company_employees:
            # Calculate pay based on time & attendance
            hours_worked = self.calculate_hours_worked(employee['employee_id'], pay_period_start, pay_period_end)
            
            gross_pay = self.calculate_gross_pay(employee, hours_worked)
            deductions = self.calculate_deductions(employee, gross_pay)
            net_pay = gross_pay - sum(deductions.values())
            
            payroll_record = {
                'employee_id': employee['employee_id'],
                'employee_name': f"{employee['personal_info']['first_name']} {employee['personal_info']['last_name']}",
                'hours_worked': hours_worked,
                'gross_pay': gross_pay,
                'deductions': deductions,
                'net_pay': net_pay,
                'pay_date': datetime.now().isoformat()
            }
            
            payroll_records.append(payroll_record)
            total_gross += gross_pay
            total_net += net_pay
        
        payroll_batch = {
            'payroll_id': payroll_id,
            'company_id': company_id,
            'pay_period_start': pay_period_start,
            'pay_period_end': pay_period_end,
            'processed_date': datetime.now().isoformat(),
            'employee_records': payroll_records,
            'totals': {
                'total_gross': total_gross,
                'total_net': total_net,
                'employee_count': len(payroll_records)
            },
            'status': 'processed'
        }
        
        self.payroll_records[payroll_id] = payroll_batch
        self.save_data('payroll_records.json', self.payroll_records)
        
        return payroll_id

    def calculate_hours_worked(self, employee_id: str, start_date: str, end_date: str) -> float:
        """Calculate total hours worked in pay period"""
        # Get time entries for employee in date range
        employee_time = self.time_attendance.get(employee_id, [])
        
        total_hours = 0
        for entry in employee_time:
            entry_date = entry.get('date', '')
            if start_date <= entry_date <= end_date:
                total_hours += entry.get('hours_worked', 0)
        
        return total_hours

    def calculate_gross_pay(self, employee: Dict[str, Any], hours_worked: float) -> float:
        """Calculate gross pay including overtime"""
        employment_info = employee.get('employment_info', {})
        salary = employment_info.get('salary', 0)
        pay_frequency = employment_info.get('pay_frequency', 'bi_weekly')
        
        if employment_info.get('employment_type') == 'hourly':
            regular_hours = min(hours_worked, 40)
            overtime_hours = max(hours_worked - 40, 0)
            
            regular_pay = regular_hours * salary
            overtime_pay = overtime_hours * salary * 1.5
            
            return regular_pay + overtime_pay
        else:
            # Salaried employee
            if pay_frequency == 'bi_weekly':
                return salary / 26
            elif pay_frequency == 'monthly':
                return salary / 12
            else:
                return salary / 52  # weekly

    def calculate_deductions(self, employee: Dict[str, Any], gross_pay: float) -> Dict[str, float]:
        """Calculate tax and benefit deductions"""
        deductions = {}
        
        # Federal tax (simplified calculation)
        deductions['federal_tax'] = gross_pay * 0.22
        
        # State tax (simplified)
        deductions['state_tax'] = gross_pay * 0.05
        
        # Social Security
        deductions['social_security'] = gross_pay * 0.062
        
        # Medicare
        deductions['medicare'] = gross_pay * 0.0145
        
        # Health insurance (if enrolled)
        benefits = employee.get('benefits', {})
        if benefits.get('health_plan'):
            deductions['health_insurance'] = 150.00  # Bi-weekly premium
        
        # 401k contribution (if enrolled)
        if benefits.get('retirement_plan'):
            deductions['retirement_401k'] = gross_pay * 0.06
        
        return deductions

    def forecast_workforce_needs(self, company_id: str, months_ahead: int = 6) -> Dict[str, Any]:
        """AI-powered workforce planning"""
        # Get current workforce
        current_employees = [
            emp for emp in self.employee_records.values()
            if emp.get('company_id') == company_id and emp.get('status') == 'active'
        ]
        
        # Analyze by department
        dept_analysis = {}
        for employee in current_employees:
            dept = employee.get('employment_info', {}).get('department', 'Unknown')
            if dept not in dept_analysis:
                dept_analysis[dept] = {
                    'current_count': 0,
                    'avg_salary': 0,
                    'total_salary': 0
                }
            
            dept_analysis[dept]['current_count'] += 1
            salary = employee.get('employment_info', {}).get('salary', 0)
            dept_analysis[dept]['total_salary'] += salary
        
        # Calculate averages and forecasts
        for dept, data in dept_analysis.items():
            if data['current_count'] > 0:
                data['avg_salary'] = data['total_salary'] / data['current_count']
                
                # Simple growth forecast (would use ML in production)
                data['projected_growth'] = data['current_count'] * 0.1  # 10% growth
                data['hiring_budget'] = data['projected_growth'] * data['avg_salary']
        
        return {
            'forecast_date': datetime.now().isoformat(),
            'months_ahead': months_ahead,
            'department_analysis': dept_analysis,
            'total_current_employees': len(current_employees),
            'projected_total_employees': len(current_employees) * 1.1
        }

# Global HR instance
hr_payroll_module = HRPayrollModule()
