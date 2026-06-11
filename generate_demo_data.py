
import json
import uuid
import random
from datetime import datetime, timedelta
import csv
import hashlib

def hash_password(password):
    """Hash password with salt"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_comprehensive_demo_data():
    """Generate comprehensive demo data for QR Legends presentations"""
    
    # Demo companies
    companies = {
        "demo-company-1": {
            "id": "demo-company-1", 
            "name": "TechFlow Industries",
            "company_name": "TechFlow Industries",
            "username": "techflow_admin",
            "email": "admin@techflow.com",
            "password": hash_password("demo123"),
            "created_at": "2025-01-15T10:00:00.000000",
            "employer_code": "TECH2025",
            "registration_ip": "192.168.1.100",
            "first_login": False,
            "industry": "Manufacturing",
            "phone": "+1-555-0123",
            "website": "https://techflow-industries.com"
        },
        "demo-company-2": {
            "id": "demo-company-2",
            "name": "Global Supply Co",
            "company_name": "Global Supply Co",
            "username": "globalsupply",
            "email": "warehouse@globalsupply.com", 
            "password": hash_password("demo456"),
            "created_at": "2025-02-01T14:30:00.000000",
            "employer_code": "GLBL2025",
            "registration_ip": "192.168.1.101",
            "first_login": False,
            "industry": "Logistics",
            "phone": "+1-555-0456",
            "website": "https://globalsupply.com"
        },
        "demo-company-3": {
            "id": "demo-company-3",
            "name": "Premier Automotive Parts",
            "company_name": "Premier Automotive Parts",
            "username": "premierparts",
            "email": "operations@premierparts.com",
            "password": hash_password("demo789"),
            "created_at": "2025-02-15T09:30:00.000000",
            "employer_code": "AUTO2025",
            "registration_ip": "192.168.1.102",
            "first_login": False,
            "industry": "Automotive",
            "phone": "+1-555-0789",
            "website": "https://premierparts.com"
        }
    }

    # Enhanced employees with more roles and departments
    employees = {
        # TechFlow Industries Team
        "emp-001": {
            "uuid": "emp-001",
            "employee_id": "TF001", 
            "company_id": "demo-company-1",
            "company_name": "TechFlow Industries",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "username": "TF001",
            "department": "receiving",
            "role": "manager",
            "email": "sarah.johnson@techflow.com",
            "password": hash_password("emp123"),
            "created_at": "2025-01-16T09:00:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0124",
            "shift": "day",
            "certification_level": "advanced"
        },
        "emp-002": {
            "uuid": "emp-002", 
            "employee_id": "TF002",
            "company_id": "demo-company-1",
            "company_name": "TechFlow Industries",
            "first_name": "Mike",
            "last_name": "Chen",
            "username": "TF002",
            "department": "inventory",
            "role": "worker",
            "email": "mike.chen@techflow.com",
            "password": hash_password("emp123"),
            "created_at": "2025-01-16T09:15:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0125",
            "shift": "day",
            "certification_level": "intermediate"
        },
        "emp-003": {
            "uuid": "emp-003",
            "employee_id": "TF003", 
            "company_id": "demo-company-1",
            "company_name": "TechFlow Industries",
            "first_name": "Amanda",
            "last_name": "Rodriguez",
            "username": "TF003",
            "department": "order_picking",
            "role": "lead",
            "email": "amanda.rodriguez@techflow.com",
            "password": hash_password("emp123"),
            "created_at": "2025-01-16T09:30:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0126",
            "shift": "day",
            "certification_level": "advanced"
        },
        "emp-004": {
            "uuid": "emp-004",
            "employee_id": "TF004",
            "company_id": "demo-company-1", 
            "company_name": "TechFlow Industries",
            "first_name": "David",
            "last_name": "Thompson",
            "username": "TF004",
            "department": "shipping",
            "role": "lead",
            "email": "david.thompson@techflow.com",
            "password": hash_password("emp123"),
            "created_at": "2025-01-16T10:00:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0127",
            "shift": "day",
            "certification_level": "expert"
        },
        "emp-005": {
            "uuid": "emp-005",
            "employee_id": "TF005",
            "company_id": "demo-company-1",
            "company_name": "TechFlow Industries", 
            "first_name": "Jessica",
            "last_name": "Martinez",
            "username": "TF005",
            "department": "quality_control",
            "role": "supervisor",
            "email": "jessica.martinez@techflow.com",
            "password": hash_password("emp123"),
            "created_at": "2025-01-17T08:00:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0128",
            "shift": "night",
            "certification_level": "expert"
        },
        "emp-006": {
            "uuid": "emp-006",
            "employee_id": "TF006",
            "company_id": "demo-company-1",
            "company_name": "TechFlow Industries",
            "first_name": "Robert",
            "last_name": "Wilson",
            "username": "TF006", 
            "department": "putaway",
            "role": "worker",
            "email": "robert.wilson@techflow.com",
            "password": hash_password("emp123"),
            "created_at": "2025-01-17T08:30:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0129",
            "shift": "evening",
            "certification_level": "beginner"
        },
        # Global Supply Co Team
        "emp-007": {
            "uuid": "emp-007",
            "employee_id": "GS001",
            "company_id": "demo-company-2",
            "company_name": "Global Supply Co",
            "first_name": "Lisa",
            "last_name": "Park",
            "username": "GS001",
            "department": "inventory",
            "role": "admin",
            "email": "lisa.park@globalsupply.com",
            "password": hash_password("emp456"),
            "created_at": "2025-02-02T08:00:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0200",
            "shift": "day",
            "certification_level": "expert"
        },
        # Premier Automotive Parts Team
        "emp-008": {
            "uuid": "emp-008",
            "employee_id": "PA001",
            "company_id": "demo-company-3",
            "company_name": "Premier Automotive Parts",
            "first_name": "Carlos",
            "last_name": "Rivera",
            "username": "PA001",
            "department": "receiving",
            "role": "manager",
            "email": "carlos.rivera@premierparts.com",
            "password": hash_password("emp789"),
            "created_at": "2025-02-16T07:30:00.000000",
            "department_restricted": False,
            "phone": "+1-555-0301",
            "shift": "day",
            "certification_level": "advanced"
        }
    }

    # Enhanced inventory with automotive and tech parts
    inventory_items = {}
    
    # Tech/Industrial Items for TechFlow
    tech_products = [
        {"sku": "TF-MTR-001", "name": "Industrial Servo Motor", "category": "Motors", "price": 1245.99, "qty_range": (5, 150)},
        {"sku": "TF-CTL-002", "name": "PLC Control Module", "category": "Electronics", "price": 875.50, "qty_range": (10, 75)},
        {"sku": "TF-SEN-003", "name": "Proximity Sensor Array", "category": "Sensors", "price": 245.00, "qty_range": (25, 200)},
        {"sku": "TF-VAL-004", "name": "Pneumatic Valve Assembly", "category": "Pneumatics", "price": 189.75, "qty_range": (15, 100)},
        {"sku": "TF-BRG-005", "name": "Heavy Duty Bearing Kit", "category": "Hardware", "price": 156.25, "qty_range": (30, 250)},
        {"sku": "TF-CBL-006", "name": "Industrial Cable Harness", "category": "Electrical", "price": 89.99, "qty_range": (50, 300)},
        {"sku": "TF-FLT-007", "name": "Hydraulic Filter System", "category": "Filters", "price": 325.00, "qty_range": (8, 60)},
        {"sku": "TF-GRD-008", "name": "Safety Guard Assembly", "category": "Safety", "price": 445.50, "qty_range": (12, 80)},
        {"sku": "TF-PMP-009", "name": "High Pressure Pump", "category": "Hydraulics", "price": 1850.00, "qty_range": (3, 25)},
        {"sku": "TF-DSP-010", "name": "HMI Display Panel", "category": "Electronics", "price": 675.99, "qty_range": (6, 40)}
    ]

    # Automotive Parts for Premier Automotive
    auto_products = [
        {"sku": "PA-ENG-001", "name": "Engine Block Assembly", "category": "Engine", "price": 2850.00, "qty_range": (2, 15)},
        {"sku": "PA-BRK-002", "name": "Brake Pad Set - Premium", "category": "Brakes", "price": 125.99, "qty_range": (50, 400)},
        {"sku": "PA-TIR-003", "name": "All-Season Tire 225/60R16", "category": "Tires", "price": 189.95, "qty_range": (20, 150)},
        {"sku": "PA-BAT-004", "name": "Car Battery - 12V AGM", "category": "Electrical", "price": 159.99, "qty_range": (25, 100)},
        {"sku": "PA-FLT-005", "name": "Oil Filter - Multi-Fit", "category": "Filters", "price": 24.99, "qty_range": (100, 800)},
        {"sku": "PA-SPK-006", "name": "Spark Plug Set", "category": "Engine", "price": 45.75, "qty_range": (75, 500)},
        {"sku": "PA-SHK-007", "name": "Shock Absorber Pair", "category": "Suspension", "price": 275.00, "qty_range": (15, 120)},
        {"sku": "PA-RAD-008", "name": "Radiator Assembly", "category": "Cooling", "price": 345.50, "qty_range": (8, 60)},
        {"sku": "PA-ALT-009", "name": "Alternator - 130A", "category": "Electrical", "price": 285.99, "qty_range": (12, 75)},
        {"sku": "PA-EXH-010", "name": "Exhaust System Kit", "category": "Exhaust", "price": 425.00, "qty_range": (6, 45)}
    ]

    # Generate enhanced inventory items
    locations = [
        "A1-B01-L1", "A1-B02-L2", "A1-B03-L3", "A2-B01-L1", "A2-B02-L2", 
        "A2-B03-L3", "A3-B01-L1", "A3-B02-L2", "A4-B01-L1", "A4-B02-L2",
        "A5-B01-L1", "A5-B02-L2", "B1-C01-L1", "B1-C02-L2", "B2-C01-L1"
    ]
    
    statuses = ["available", "allocated", "qa_hold", "damaged", "reserved"]
    
    # TechFlow inventory
    for i, product in enumerate(tech_products):
        for variant in range(random.randint(2, 5)):
            item_id = str(uuid.uuid4())
            inventory_items[item_id] = {
                "id": item_id,
                "company_id": "demo-company-1",
                "static_uid": f"QRL-{item_id[:8]}",
                "item_number": f"{product['sku']}-{variant:02d}",
                "name": product["name"],
                "description": f"{product['name']} - Professional grade industrial component",
                "category": product["category"],
                "quantity": random.randint(*product["qty_range"]),
                "location": random.choice(locations),
                "container_id": f"CNT-TF{i:03d}{variant:02d}",
                "price": product["price"],
                "cost": round(product["price"] * 0.65, 2),
                "uom": "EA",
                "status": random.choice(statuses),
                "source": "demo_data",
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 180))).isoformat(),
                "last_updated": (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat(),
                "last_counted": (datetime.now() - timedelta(days=random.randint(1, 45))).isoformat(),
                "bin_location": random.choice(locations),
                "velocity": random.choice(["fast", "medium", "slow"]),
                "abc_classification": random.choice(["A", "B", "C"])
            }

    # Premier Automotive inventory  
    for i, product in enumerate(auto_products):
        for variant in range(random.randint(3, 7)):
            item_id = str(uuid.uuid4())
            inventory_items[item_id] = {
                "id": item_id,
                "company_id": "demo-company-3",
                "static_uid": f"QRL-{item_id[:8]}",
                "item_number": f"{product['sku']}-{variant:02d}",
                "name": product["name"],
                "description": f"{product['name']} - OEM quality automotive part",
                "category": product["category"], 
                "quantity": random.randint(*product["qty_range"]),
                "location": random.choice(locations),
                "container_id": f"CNT-PA{i:03d}{variant:02d}",
                "price": product["price"],
                "cost": round(product["price"] * 0.58, 2),
                "uom": "EA",
                "status": random.choice(statuses),
                "source": "demo_data",
                "created_at": (datetime.now() - timedelta(days=random.randint(15, 120))).isoformat(),
                "last_updated": (datetime.now() - timedelta(days=random.randint(0, 10))).isoformat(),
                "last_counted": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "bin_location": random.choice(locations),
                "velocity": random.choice(["fast", "medium", "slow"]),
                "abc_classification": random.choice(["A", "B", "C"])
            }

    # Enhanced containers with realistic data
    containers = {}
    container_types = ["standard", "hazmat", "refrigerated", "high_value", "bulk"]
    
    for company_id in ["demo-company-1", "demo-company-2", "demo-company-3"]:
        for i in range(25):  # 25 containers per company
            container_id = f"CNT-{company_id.split('-')[2].upper()[:2]}{i:03d}"
            containers[container_id] = {
                "id": container_id,
                "name": f"Container {container_id}",
                "qr_data": f"CONTAINER:{container_id}",
                "company_id": company_id,
                "status": random.choice(["active", "maintenance", "allocated", "empty"]),
                "type": random.choice(container_types),
                "location": random.choice(locations),
                "capacity": random.randint(50, 500),
                "current_fill": random.randint(0, 450),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "workflow_stage": random.choice(["receiving", "putaway", "picking", "shipping", "inventory_tracking"]),
                "items": [],
                "temperature_controlled": random.choice([True, False]),
                "security_level": random.choice(["standard", "high", "maximum"])
            }

    # Enhanced activity logs with realistic warehouse operations
    activity_logs = {}
    activity_types = [
        "item_received", "item_putaway", "item_picked", "item_shipped", "item_moved",
        "quality_check_passed", "quality_check_failed", "cycle_count_completed", 
        "container_created", "container_moved", "inventory_adjustment", "order_fulfilled",
        "freight_received", "transfer_completed", "damage_reported", "return_processed"
    ]

    for company_id in companies.keys():
        activity_logs[company_id] = []
        
        # Generate 100+ activities per company
        for _ in range(random.randint(100, 200)):
            activity_date = datetime.now() - timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            activity_type = random.choice(activity_types)
            employee_ids = [emp["uuid"] for emp in employees.values() if emp["company_id"] == company_id]
            
            activity_logs[company_id].append({
                "id": str(uuid.uuid4()),
                "type": activity_type,
                "message": f"{activity_type.replace('_', ' ').title()} - Operation completed successfully",
                "timestamp": activity_date.isoformat(),
                "user_id": random.choice(employee_ids) if employee_ids else "system",
                "severity": random.choice(["info", "success", "warning", "error"]),
                "department": random.choice(["receiving", "putaway", "picking", "shipping", "quality_control"]),
                "details": {
                    "location": random.choice(locations),
                    "quantity": random.randint(1, 100),
                    "item_count": random.randint(1, 25),
                    "processing_time": random.randint(30, 1800),  # seconds
                    "accuracy_rate": round(random.uniform(95.0, 99.9), 2)
                }
            })

    # Enhanced purchase orders with slot allocations and variances
    purchase_orders = {}
    suppliers = [
        "Acme Industrial Supply", "TechCorp Components", "Global Parts LLC", 
        "Premium Manufacturing", "Elite Components Inc", "Industrial Solutions Co"
    ]

    def generate_po_items(company_id, item_count):
        """Generate PO line items with slot allocations and variances"""
        items = []
        all_locations = [
            "A1-B01-L1", "A1-B02-L2", "A1-B03-L3", "A2-B01-L1", "A2-B02-L2", 
            "A2-B03-L3", "A3-B01-L1", "A3-B02-L2", "A4-B01-L1", "A4-B02-L2",
            "A5-B01-L1", "A5-B02-L2", "B1-C01-L1", "B1-C02-L2", "B2-C01-L1",
            "C1-D01-L1", "C1-D02-L2", "C2-D01-L1", "D1-E01-L1", "D2-E02-L2"
        ]
        
        # Select appropriate products based on company
        if company_id == "demo-company-1":
            products = tech_products
            prefix = "TF"
        elif company_id == "demo-company-3":
            products = auto_products
            prefix = "PA"
        else:
            products = tech_products + auto_products  # Mixed for Global Supply
            prefix = "GS"

        for i in range(item_count):
            product = random.choice(products)
            ordered_qty = random.randint(5, 100)
            
            # Determine if there will be variances (30% chance)
            has_variance = random.random() < 0.3
            variance_type = None
            received_qty = ordered_qty
            
            if has_variance:
                variance_options = ["short", "overage", "damaged"]
                variance_type = random.choice(variance_options)
                
                if variance_type == "short":
                    received_qty = ordered_qty - random.randint(1, min(5, ordered_qty))
                elif variance_type == "overage":
                    received_qty = ordered_qty + random.randint(1, 10)
                elif variance_type == "damaged":
                    damaged_qty = random.randint(1, min(3, ordered_qty))
                    received_qty = ordered_qty - damaged_qty

            item = {
                "line_number": i + 1,
                "item_number": f"{product['sku']}-{random.randint(1, 99):02d}",
                "description": product["name"],
                "ordered_quantity": ordered_qty,
                "received_quantity": received_qty if random.random() < 0.7 else 0,  # 70% chance already received
                "unit_price": product["price"],
                "total_price": round(product["price"] * ordered_qty, 2),
                "uom": "EA",
                "allocated_slot": random.choice(all_locations),
                "backup_slot": random.choice([slot for slot in all_locations if slot != random.choice(all_locations)]),
                "variance_type": variance_type,
                "variance_notes": self.get_variance_notes(variance_type) if variance_type else None,
                "receiving_status": random.choice(["pending", "partial", "complete", "exception"]),
                "quality_check_required": random.choice([True, False]),
                "putaway_priority": random.choice(["standard", "expedite", "hold"]),
                "expected_delivery_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")
            }
            items.append(item)
        
        return items

    def get_variance_notes(variance_type):
        """Get realistic variance notes"""
        notes_map = {
            "short": [
                "Supplier shipped partial quantity - backorder expected",
                "Damaged units removed during inspection",
                "Shipping container shortage - investigating",
                "Manufacturing delay - partial shipment sent"
            ],
            "overage": [
                "Supplier sent extra units as promotion",
                "Rounding error in supplier system",
                "Bonus units included with order",
                "Supplier correction for previous shortage"
            ],
            "damaged": [
                "Transit damage - shipping claim filed",
                "Packaging defect - items unusable",
                "Forklift damage during unloading",
                "Quality control rejection - cosmetic damage"
            ]
        }
        return random.choice(notes_map.get(variance_type, ["Variance noted"]))

    # Create purchase orders with enhanced data
    for company_id in companies.keys():
        for i in range(random.randint(15, 25)):
            po_id = f"PO-{datetime.now().year}-{random.randint(1000, 9999)}"
            item_count = random.randint(3, 15)
            
            # Generate items for this PO
            po_items = []
            all_locations = [
                "A1-B01-L1", "A1-B02-L2", "A1-B03-L3", "A2-B01-L1", "A2-B02-L2", 
                "A2-B03-L3", "A3-B01-L1", "A3-B02-L2", "A4-B01-L1", "A4-B02-L2",
                "A5-B01-L1", "A5-B02-L2", "B1-C01-L1", "B1-C02-L2", "B2-C01-L1"
            ]
            
            # Select appropriate products based on company
            if company_id == "demo-company-1":
                products = tech_products
            elif company_id == "demo-company-3":
                products = auto_products
            else:
                products = tech_products + auto_products

            total_value = 0
            for j in range(item_count):
                product = random.choice(products)
                ordered_qty = random.randint(5, 100)
                
                # Determine variances
                has_variance = random.random() < 0.3
                variance_type = None
                received_qty = ordered_qty
                variance_notes = None
                
                if has_variance:
                    variance_options = ["short", "overage", "damaged"]
                    variance_type = random.choice(variance_options)
                    
                    if variance_type == "short":
                        received_qty = ordered_qty - random.randint(1, min(5, ordered_qty))
                        variance_notes = random.choice([
                            "Supplier shipped partial quantity - backorder expected",
                            "Damaged units removed during inspection",
                            "Manufacturing delay - partial shipment sent"
                        ])
                    elif variance_type == "overage":
                        received_qty = ordered_qty + random.randint(1, 10)
                        variance_notes = random.choice([
                            "Supplier sent extra units as promotion",
                            "Supplier correction for previous shortage",
                            "Rounding error in supplier system"
                        ])
                    elif variance_type == "damaged":
                        damaged_qty = random.randint(1, min(3, ordered_qty))
                        received_qty = ordered_qty - damaged_qty
                        variance_notes = random.choice([
                            "Transit damage - shipping claim filed",
                            "Packaging defect - items unusable",
                            "Quality control rejection - cosmetic damage"
                        ])

                item_total = round(product["price"] * ordered_qty, 2)
                total_value += item_total

                po_item = {
                    "line_number": j + 1,
                    "item_number": f"{product['sku']}-{random.randint(1, 99):02d}",
                    "description": product["name"],
                    "ordered_quantity": ordered_qty,
                    "received_quantity": received_qty if random.random() < 0.6 else 0,
                    "unit_price": product["price"],
                    "total_price": item_total,
                    "uom": "EA",
                    "allocated_slot": random.choice(all_locations),
                    "backup_slot": random.choice([slot for slot in all_locations]),
                    "variance_type": variance_type,
                    "variance_notes": variance_notes,
                    "receiving_status": random.choice(["pending", "partial", "complete", "exception"]) if received_qty > 0 else "pending",
                    "quality_check_required": random.choice([True, False]),
                    "putaway_priority": random.choice(["standard", "expedite", "hold"]),
                    "expected_delivery_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                    "category": product["category"]
                }
                po_items.append(po_item)

            # Create the purchase order
            purchase_orders[po_id] = {
                "id": po_id,
                "company_id": company_id,
                "supplier": random.choice(suppliers),
                "status": random.choice(["pending", "approved", "shipped", "received", "closed"]),
                "order_date": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                "expected_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "total_value": round(total_value, 2),
                "item_count": item_count,
                "priority": random.choice(["low", "medium", "high", "urgent"]),
                "freight_terms": random.choice(["FOB Origin", "FOB Destination", "CIF", "DDP"]),
                "created_by": random.choice([emp["uuid"] for emp in employees.values() if emp["company_id"] == company_id]),
                "items": po_items,
                "receiving_notes": random.choice([
                    "Standard receiving - no special instructions",
                    "Fragile items - handle with care",
                    "Expedite putaway - production priority",
                    "Quality inspection required before putaway",
                    "Temperature sensitive - refrigerated storage"
                ]) if random.random() < 0.4 else None,
                "dock_door": random.choice(["DOCK-A", "DOCK-B", "DOCK-C", "DOCK-D"]),
                "carrier": random.choice(["FedEx Freight", "UPS Freight", "Old Dominion", "XPO Logistics", "SAIA"])
            }

    # Enhanced subscriptions with realistic billing
    subscriptions = {
        "demo-company-1": {
            "company_id": "demo-company-1",
            "plan": "unlimited_warehouse",
            "price": 4999.00,
            "billing_cycle": "monthly",
            "status": "active",
            "is_trial": False,
            "users": 6,
            "start_date": "2025-01-15T10:00:00.000000",
            "next_billing_date": "2025-03-01T10:00:00.000000",
            "created_at": "2025-01-15T10:00:00.000000",
            "features_enabled": ["erp", "analytics", "multi_location", "api_access"],
            "monthly_scans": 15750,
            "monthly_limit": 25000
        },
        "demo-company-2": {
            "company_id": "demo-company-2",
            "plan": "large_warehouse",
            "price": 3999.00,
            "billing_cycle": "monthly", 
            "status": "active",
            "is_trial": False,
            "users": 1,
            "start_date": "2025-02-01T14:30:00.000000",
            "next_billing_date": "2025-03-01T14:30:00.000000",
            "created_at": "2025-02-01T14:30:00.000000",
            "features_enabled": ["analytics", "multi_location"],
            "monthly_scans": 8950,
            "monthly_limit": 15000
        },
        "demo-company-3": {
            "company_id": "demo-company-3",
            "plan": "medium_warehouse",
            "price": 2999.00,
            "billing_cycle": "monthly",
            "status": "active", 
            "is_trial": False,
            "users": 1,
            "start_date": "2025-02-15T09:30:00.000000",
            "next_billing_date": "2025-03-15T09:30:00.000000",
            "created_at": "2025-02-15T09:30:00.000000",
            "features_enabled": ["analytics"],
            "monthly_scans": 4250,
            "monthly_limit": 8000
        }
    }

    # Performance metrics for presentation
    performance_metrics = {
        "demo-company-1": {
            "daily_throughput": 1250,
            "accuracy_rate": 99.2,
            "cycle_time_minutes": 4.5,
            "pick_rate_per_hour": 185,
            "receiving_rate_per_hour": 95,
            "inventory_turns": 8.3,
            "space_utilization": 87.5,
            "labor_efficiency": 94.2,
            "order_fill_rate": 98.7,
            "damage_rate": 0.3
        },
        "demo-company-2": {
            "daily_throughput": 850,
            "accuracy_rate": 97.8,
            "cycle_time_minutes": 6.2,
            "pick_rate_per_hour": 165,
            "receiving_rate_per_hour": 78,
            "inventory_turns": 6.1,
            "space_utilization": 82.3,
            "labor_efficiency": 89.7,
            "order_fill_rate": 96.4,
            "damage_rate": 0.7
        },
        "demo-company-3": {
            "daily_throughput": 450,
            "accuracy_rate": 98.9,
            "cycle_time_minutes": 5.1,
            "pick_rate_per_hour": 145,
            "receiving_rate_per_hour": 65,
            "inventory_turns": 12.7,
            "space_utilization": 91.2,
            "labor_efficiency": 92.3,
            "order_fill_rate": 99.1,
            "damage_rate": 0.2
        }
    }

    # Save all enhanced data
    data_files = {
        "companies.json": companies,
        "employees.json": employees,
        "inventory_items.json": inventory_items,
        "containers.json": containers,
        "activity_logs.json": activity_logs,
        "subscriptions.json": subscriptions,
        "purchase_orders.json": purchase_orders,
        "performance_metrics.json": performance_metrics
    }

    for filename, data in data_files.items():
        with open(f"data/{filename}", "w") as f:
            json.dump(data, f, indent=2)

    print("✅ Comprehensive demo data generated successfully!")
    print(f"📊 Created for presentation:")
    print(f"   • 3 Demo Companies (TechFlow, Global Supply, Premier Auto)")
    print(f"   • 8 Employees across different roles and shifts") 
    print(f"   • {len(inventory_items)} Inventory items (tech & automotive)")
    print(f"   • 75 Containers with realistic capacity data")
    print(f"   • 300+ Activity log entries across all operations")
    print(f"   • Purchase orders with slot allocations and variance tracking")
    print(f"   • Performance metrics for KPI dashboards")
    print(f"   • Realistic receiving variances (shorts, overages, damages)")
    print("\n🎬 Perfect for comprehensive presentations!")

if __name__ == "__main__":
    generate_comprehensive_demo_data()
