
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from backup_service import auto_backup_trigger

class ProjectManagementModule:
    """Project Management module for QRLegends ERP Ultra"""
    
    def __init__(self):
        self.data_dir = 'data/project_management'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data storage
        self.projects = self.load_data('projects.json', {})
        self.tasks = self.load_data('tasks.json', {})
        self.resources = self.load_data('resources.json', {})
        self.time_tracking = self.load_data('time_tracking.json', {})
        self.project_costs = self.load_data('project_costs.json', {})
        self.milestones = self.load_data('milestones.json', {})
        
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

    def create_project(self, company_id: str, project_data: Dict[str, Any]) -> str:
        """Create new project"""
        project_id = str(uuid.uuid4())
        
        project = {
            'project_id': project_id,
            'company_id': company_id,
            'project_name': project_data.get('project_name'),
            'description': project_data.get('description'),
            'project_manager': project_data.get('project_manager'),
            'client_id': project_data.get('client_id'),
            'start_date': project_data.get('start_date'),
            'end_date': project_data.get('end_date'),
            'budget': {
                'total_budget': project_data.get('total_budget', 0),
                'labor_budget': project_data.get('labor_budget', 0),
                'material_budget': project_data.get('material_budget', 0),
                'overhead_budget': project_data.get('overhead_budget', 0)
            },
            'status': 'planning',  # planning, active, on_hold, completed, cancelled
            'priority': project_data.get('priority', 'medium'),
            'team_members': project_data.get('team_members', []),
            'phases': project_data.get('phases', []),
            'deliverables': project_data.get('deliverables', []),
            'risks': project_data.get('risks', []),
            'created_at': datetime.now().isoformat(),
            'progress_percentage': 0
        }
        
        self.projects[project_id] = project
        self.save_data('projects.json', self.projects)
        
        auto_backup_trigger.log_change(company_id, 'project_created', {
            'project_id': project_id,
            'project_name': project_data.get('project_name'),
            'action': 'create_project',
            'source': 'project_management'
        })
        
        return project_id

    def create_task(self, company_id: str, task_data: Dict[str, Any]) -> str:
        """Create project task"""
        task_id = str(uuid.uuid4())
        
        task = {
            'task_id': task_id,
            'company_id': company_id,
            'project_id': task_data.get('project_id'),
            'task_name': task_data.get('task_name'),
            'description': task_data.get('description'),
            'assigned_to': task_data.get('assigned_to'),
            'start_date': task_data.get('start_date'),
            'due_date': task_data.get('due_date'),
            'estimated_hours': task_data.get('estimated_hours', 0),
            'actual_hours': 0,
            'priority': task_data.get('priority', 'medium'),
            'status': 'not_started',  # not_started, in_progress, completed, blocked
            'completion_percentage': 0,
            'dependencies': task_data.get('dependencies', []),
            'subtasks': task_data.get('subtasks', []),
            'attachments': task_data.get('attachments', []),
            'comments': [],
            'created_at': datetime.now().isoformat(),
            'created_by': task_data.get('created_by')
        }
        
        self.tasks[task_id] = task
        self.save_data('tasks.json', self.tasks)
        
        # Update project progress
        self.update_project_progress(task_data.get('project_id'))
        
        return task_id

    def log_time_entry(self, company_id: str, time_data: Dict[str, Any]) -> str:
        """Log time spent on project/task"""
        entry_id = str(uuid.uuid4())
        
        time_entry = {
            'entry_id': entry_id,
            'company_id': company_id,
            'project_id': time_data.get('project_id'),
            'task_id': time_data.get('task_id'),
            'employee_id': time_data.get('employee_id'),
            'date': time_data.get('date', datetime.now().isoformat()[:10]),
            'hours_worked': time_data.get('hours_worked'),
            'billable_hours': time_data.get('billable_hours'),
            'hourly_rate': time_data.get('hourly_rate', 0),
            'description': time_data.get('description'),
            'activity_type': time_data.get('activity_type'),  # design, development, testing, etc.
            'created_at': datetime.now().isoformat()
        }
        
        if company_id not in self.time_tracking:
            self.time_tracking[company_id] = []
        
        self.time_tracking[company_id].append(time_entry)
        self.save_data('time_tracking.json', self.time_tracking)
        
        # Update task actual hours
        if time_data.get('task_id'):
            self.update_task_hours(time_data.get('task_id'), time_data.get('hours_worked', 0))
        
        return entry_id

    def update_task_hours(self, task_id: str, additional_hours: float):
        """Update task actual hours"""
        if task_id in self.tasks:
            self.tasks[task_id]['actual_hours'] += additional_hours
            self.save_data('tasks.json', self.tasks)

    def update_project_progress(self, project_id: str):
        """Calculate and update project progress"""
        if not project_id or project_id not in self.projects:
            return
        
        # Get all tasks for project
        project_tasks = [
            task for task in self.tasks.values()
            if task.get('project_id') == project_id
        ]
        
        if not project_tasks:
            return
        
        # Calculate weighted progress
        total_estimated_hours = sum(task.get('estimated_hours', 0) for task in project_tasks)
        if total_estimated_hours == 0:
            # If no estimated hours, use simple task count
            completed_tasks = len([task for task in project_tasks if task.get('status') == 'completed'])
            progress = (completed_tasks / len(project_tasks)) * 100
        else:
            # Weighted by estimated hours
            weighted_progress = 0
            for task in project_tasks:
                task_weight = task.get('estimated_hours', 0) / total_estimated_hours
                task_progress = task.get('completion_percentage', 0)
                weighted_progress += task_weight * task_progress
            progress = weighted_progress
        
        self.projects[project_id]['progress_percentage'] = round(progress, 2)
        self.save_data('projects.json', self.projects)

    def get_project_budget_analysis(self, project_id: str) -> Dict[str, Any]:
        """Analyze project budget vs actual costs"""
        if project_id not in self.projects:
            return {'error': 'Project not found'}
        
        project = self.projects[project_id]
        company_id = project['company_id']
        
        # Get time entries for project
        project_time = []
        if company_id in self.time_tracking:
            project_time = [
                entry for entry in self.time_tracking[company_id]
                if entry.get('project_id') == project_id
            ]
        
        # Calculate actual labor costs
        actual_labor_cost = sum(
            entry.get('hours_worked', 0) * entry.get('hourly_rate', 0)
            for entry in project_time
        )
        
        # Get material costs (would integrate with procurement)
        actual_material_cost = 0  # Placeholder
        
        # Get overhead costs
        actual_overhead_cost = 0  # Placeholder
        
        total_actual_cost = actual_labor_cost + actual_material_cost + actual_overhead_cost
        
        budget = project.get('budget', {})
        total_budget = budget.get('total_budget', 0)
        
        return {
            'project_id': project_id,
            'project_name': project.get('project_name'),
            'budget': {
                'total_budget': total_budget,
                'labor_budget': budget.get('labor_budget', 0),
                'material_budget': budget.get('material_budget', 0),
                'overhead_budget': budget.get('overhead_budget', 0)
            },
            'actual_costs': {
                'total_actual': total_actual_cost,
                'labor_actual': actual_labor_cost,
                'material_actual': actual_material_cost,
                'overhead_actual': actual_overhead_cost
            },
            'variance': {
                'total_variance': total_budget - total_actual_cost,
                'variance_percentage': ((total_budget - total_actual_cost) / total_budget * 100) if total_budget > 0 else 0
            },
            'progress_percentage': project.get('progress_percentage', 0),
            'analysis_date': datetime.now().isoformat()
        }

    def get_resource_utilization(self, company_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyze resource utilization across projects"""
        # Get time entries in date range
        company_time = self.time_tracking.get(company_id, [])
        period_time = [
            entry for entry in company_time
            if start_date <= entry.get('date', '') <= end_date
        ]
        
        # Group by employee
        employee_utilization = {}
        for entry in period_time:
            emp_id = entry.get('employee_id')
            if emp_id not in employee_utilization:
                employee_utilization[emp_id] = {
                    'employee_id': emp_id,
                    'total_hours': 0,
                    'billable_hours': 0,
                    'projects': set(),
                    'activities': {}
                }
            
            util = employee_utilization[emp_id]
            util['total_hours'] += entry.get('hours_worked', 0)
            util['billable_hours'] += entry.get('billable_hours', 0)
            util['projects'].add(entry.get('project_id'))
            
            activity = entry.get('activity_type', 'other')
            util['activities'][activity] = util['activities'].get(activity, 0) + entry.get('hours_worked', 0)
        
        # Convert sets to lists for JSON serialization
        for emp_id, util in employee_utilization.items():
            util['projects'] = list(util['projects'])
            util['project_count'] = len(util['projects'])
            util['utilization_rate'] = (util['billable_hours'] / util['total_hours'] * 100) if util['total_hours'] > 0 else 0
        
        return {
            'period': {'start_date': start_date, 'end_date': end_date},
            'employee_utilization': employee_utilization,
            'summary': {
                'total_employees': len(employee_utilization),
                'total_hours_logged': sum(util['total_hours'] for util in employee_utilization.values()),
                'total_billable_hours': sum(util['billable_hours'] for util in employee_utilization.values())
            }
        }

    def generate_gantt_data(self, project_id: str) -> Dict[str, Any]:
        """Generate Gantt chart data for project"""
        if project_id not in self.projects:
            return {'error': 'Project not found'}
        
        project = self.projects[project_id]
        project_tasks = [
            task for task in self.tasks.values()
            if task.get('project_id') == project_id
        ]
        
        gantt_tasks = []
        for task in project_tasks:
            gantt_task = {
                'id': task['task_id'],
                'name': task['task_name'],
                'start': task.get('start_date'),
                'end': task.get('due_date'),
                'progress': task.get('completion_percentage', 0),
                'dependencies': task.get('dependencies', []),
                'assigned_to': task.get('assigned_to'),
                'status': task.get('status'),
                'estimated_hours': task.get('estimated_hours', 0),
                'actual_hours': task.get('actual_hours', 0)
            }
            gantt_tasks.append(gantt_task)
        
        return {
            'project_id': project_id,
            'project_name': project.get('project_name'),
            'project_start': project.get('start_date'),
            'project_end': project.get('end_date'),
            'tasks': gantt_tasks,
            'generated_at': datetime.now().isoformat()
        }

# Global Project Management instance
project_management_module = ProjectManagementModule()
