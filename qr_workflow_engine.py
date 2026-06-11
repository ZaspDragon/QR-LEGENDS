
import json
import hmac
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import base64

class QRWorkflowEngine:
    """QR-First workflow engine for all warehouse processes"""
    
    def __init__(self, secret_key: str = "qr-legends-hmac-key"):
        self.secret_key = secret_key
        self.scan_cache = {}  # For idempotency
        
    def sign_qr_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sign QR payload with HMAC for tamper protection"""
        payload_copy = payload.copy()
        if 'sig' in payload_copy:
            del payload_copy['sig']
        
        # Add timestamp if not present
        if 'ts' not in payload_copy:
            payload_copy['ts'] = int(datetime.now().timestamp() * 1000)
        
        # Create canonical string and sign
        canonical = json.dumps(payload_copy, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            self.secret_key.encode(), 
            canonical.encode(), 
            hashlib.sha256
        ).digest()
        
        payload_copy['sig'] = base64.b64encode(signature).decode()
        return payload_copy
    
    def verify_qr_payload(self, payload: Dict[str, Any]) -> bool:
        """Verify QR payload signature"""
        if 'sig' not in payload:
            return False
        
        received_sig = payload['sig']
        payload_copy = payload.copy()
        del payload_copy['sig']
        
        canonical = json.dumps(payload_copy, sort_keys=True, separators=(',', ':'))
        expected_sig = base64.b64encode(
            hmac.new(self.secret_key.encode(), canonical.encode(), hashlib.sha256).digest()
        ).decode()
        
        return hmac.compare_digest(received_sig, expected_sig)
    
    def process_scan(self, scan_id: str, qr_payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process QR scan with idempotency"""
        # Check for duplicate scan
        if scan_id in self.scan_cache:
            return {'success': True, 'duplicate': True, 'result': self.scan_cache[scan_id]}
        
        # Verify signature
        if not self.verify_qr_payload(qr_payload):
            return {'success': False, 'error': 'Invalid QR signature'}
        
        # Route by QR type
        qr_type = qr_payload.get('type')
        result = self._route_scan_by_type(qr_type, qr_payload, user_id)
        
        # Cache result for idempotency
        self.scan_cache[scan_id] = result
        
        return {'success': True, 'result': result}
    
    def _route_scan_by_type(self, qr_type: str, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Route scan processing by QR type"""
        processors = {
            'LPN': self._process_lpn_scan,
            'LOC': self._process_location_scan,
            'ORDER': self._process_order_scan,
            'ASN': self._process_asn_scan,
            'TASK': self._process_task_scan,
            'EQUIPMENT': self._process_equipment_scan,
            'INCIDENT': self._process_incident_scan,
            'USER': self._process_user_scan,
            'VEHICLE': self._process_vehicle_scan
        }
        
        processor = processors.get(qr_type, self._process_unknown_scan)
        return processor(payload, user_id)
    
    def _process_lpn_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process LPN scan - confirm pick, putaway, receive"""
        lpn_id = payload.get('id')
        location = payload.get('loc')
        
        return {
            'action': 'lpn_scanned',
            'lpn_id': lpn_id,
            'current_location': location,
            'suggested_actions': ['confirm_pick', 'confirm_putaway', 'move_lpn'],
            'system_message': f"LPN {lpn_id} scanned at {location}"
        }
    
    def _process_location_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process location scan - set user position, show bin contents"""
        loc_id = payload.get('loc')
        zone = payload.get('zone')
        kind = payload.get('kind')
        
        return {
            'action': 'location_scanned',
            'location_id': loc_id,
            'zone': zone,
            'kind': kind,
            'user_position_updated': True,
            'navigation_anchor': {'loc': loc_id, 'coordinates': payload.get('coordinates')},
            'system_message': f"Position updated to {loc_id}"
        }
    
    def _process_order_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process order scan - start picking workflow"""
        order_id = payload.get('order_id')
        customer = payload.get('customer')
        priority = payload.get('priority', 'NORMAL')
        
        return {
            'action': 'order_started',
            'order_id': order_id,
            'customer': customer,
            'priority': priority,
            'workflow': 'picking',
            'next_steps': ['scan_pick_location', 'scan_lpn'],
            'system_message': f"Started picking order {order_id} for {customer}"
        }
    
    def _process_asn_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process ASN scan - start receiving workflow"""
        asn_id = payload.get('asn_id')
        vendor = payload.get('vendor')
        dock = payload.get('dock')
        
        return {
            'action': 'asn_started',
            'asn_id': asn_id,
            'vendor': vendor,
            'dock': dock,
            'workflow': 'receiving',
            'next_steps': ['scan_carton', 'create_lpn', 'scan_putaway_location'],
            'system_message': f"Started receiving ASN {asn_id} from {vendor}"
        }
    
    def _process_task_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process task scan - accept and start task"""
        task_id = payload.get('task_id')
        task_kind = payload.get('task_kind')
        entity_id = payload.get('entity_id')
        
        return {
            'action': 'task_accepted',
            'task_id': task_id,
            'task_kind': task_kind,
            'entity_id': entity_id,
            'assigned_to': user_id,
            'workflow': task_kind.lower(),
            'system_message': f"Accepted {task_kind} task {task_id}"
        }
    
    def _process_equipment_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process equipment scan - safety check, usage log"""
        equip_id = payload.get('equip_id')
        kind = payload.get('kind')
        last_maint = payload.get('last_maint')
        
        return {
            'action': 'equipment_scanned',
            'equipment_id': equip_id,
            'kind': kind,
            'safety_check_required': True,
            'last_maintenance': last_maint,
            'system_message': f"Equipment {equip_id} ready for use"
        }
    
    def _process_incident_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process incident scan - log safety/quality issue"""
        incident_id = payload.get('incident_id')
        level = payload.get('level', 'INFO')
        
        return {
            'action': 'incident_reported',
            'incident_id': incident_id,
            'level': level,
            'reporter': user_id,
            'requires_photo': True,
            'escalate_to_channel': 'ch-exceptions' if level == 'CRITICAL' else 'ch-safety',
            'system_message': f"Incident {incident_id} reported - {level} priority"
        }
    
    def _process_user_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process user scan - timeclock, handoff"""
        scanned_user_id = payload.get('user_id')
        name = payload.get('name')
        role = payload.get('role')
        
        return {
            'action': 'user_scanned',
            'scanned_user': scanned_user_id,
            'name': name,
            'role': role,
            'actions': ['start_dm', 'handoff_task', 'clock_in_out'],
            'system_message': f"Scanned user badge for {name}"
        }
    
    def _process_vehicle_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process vehicle scan - dock assignment, manifest"""
        vehicle_id = payload.get('vehicle_id')
        plate = payload.get('plate')
        carrier = payload.get('carrier')
        dock = payload.get('dock')
        
        return {
            'action': 'vehicle_scanned',
            'vehicle_id': vehicle_id,
            'plate': plate,
            'carrier': carrier,
            'dock': dock,
            'actions': ['start_loading', 'generate_manifest', 'complete_shipment'],
            'system_message': f"Vehicle {plate} at dock {dock}"
        }
    
    def _process_unknown_scan(self, payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Process unknown QR type"""
        return {
            'action': 'unknown_qr',
            'payload': payload,
            'system_message': f"Unknown QR type: {payload.get('type', 'None')}"
        }

# Global instance
qr_engine = QRWorkflowEngine()
