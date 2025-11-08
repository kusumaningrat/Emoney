# seeders/document_seeder.py

from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid
import json
import base64
import hashlib

from database import SessionLocal
from models.documents import FileType, Attachment, VaultDocument, Note, Task, Alert
from models.clients import Client
from models.users import User

# Initialize Faker
fake = Faker()

# Main function to seed all document management data
def seed_document_data(db: Session = None):
    """Main function to seed all document management data in correct order."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_file_types = db.query(FileType).count()
        if existing_file_types > 0:
            print("Document management data already seeded, skipping...")
            return
        
        # Ensure clients exist
        clients = db.query(Client).all()
        if not clients:
            print("No clients found, seeding clients first required.")
            return
            
        # Get users
        users = db.query(User).all()
        if not users:
            print("No users found, seeding users first required.")
            return
            
        # 1. Create file types
        file_types = seed_file_types(db)
        db.commit()
            
        # 2. Create vault documents
        vault_documents = seed_vault_documents(db, clients, file_types, users)
        db.commit()
            
        # 3. Create attachments
        attachments = seed_attachments(db, clients, file_types, users)
        db.commit()
            
        # 4. Create notes
        notes = seed_notes(db, clients, users)
        db.commit()
            
        # 5. Create tasks
        tasks = seed_tasks(db, clients, users)
        db.commit()
            
        # 6. Create alerts
        alerts = seed_alerts(db, clients, users)
        db.commit()
        
        print("Document management seeding complete!")
        return True
        
    except Exception as e:
        print(f"Error seeding document management data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def generate_mock_file_content(file_type, kb_size=10):
    """Generate mock file content of appropriate size."""
    # Generate random bytes for the file content
    # Limit size to prevent database bloat in development
    bytes_size = min(kb_size * 1024, 100 * 1024)  # Max 100KB for demo purposes
    content = b'x' * bytes_size
    return content

def calculate_checksum(content):
    """Calculate SHA-256 checksum for file content."""
    if content:
        return hashlib.sha256(content).hexdigest()
    return None

def seed_file_types(db: Session):
    """Create common file types."""
    print("Creating file types...")
    
    file_types_data = [
        {
            "id": generate_id("filetype"),
            "name": "PDF Document",
            "description": "Adobe Portable Document Format",
            "extension": ".pdf",
            "mime_type": "application/pdf",
            "category": "document",
            "icon": "fa-file-pdf",
            "max_size": 10 * 1024 * 1024,  # 10MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "Word Document",
            "description": "Microsoft Word Document",
            "extension": ".docx",
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "category": "document",
            "icon": "fa-file-word",
            "max_size": 10 * 1024 * 1024,  # 10MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "Excel Spreadsheet",
            "description": "Microsoft Excel Spreadsheet",
            "extension": ".xlsx",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "category": "spreadsheet",
            "icon": "fa-file-excel",
            "max_size": 10 * 1024 * 1024,  # 10MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "Text Document",
            "description": "Plain Text Document",
            "extension": ".txt",
            "mime_type": "text/plain",
            "category": "document",
            "icon": "fa-file-alt",
            "max_size": 5 * 1024 * 1024,  # 5MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "JPEG Image",
            "description": "JPEG Image Format",
            "extension": ".jpg",
            "mime_type": "image/jpeg",
            "category": "image",
            "icon": "fa-file-image",
            "max_size": 5 * 1024 * 1024,  # 5MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "PNG Image",
            "description": "PNG Image Format",
            "extension": ".png",
            "mime_type": "image/png",
            "category": "image",
            "icon": "fa-file-image",
            "max_size": 5 * 1024 * 1024,  # 5MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "CSV Document",
            "description": "Comma-Separated Values Document",
            "extension": ".csv",
            "mime_type": "text/csv",
            "category": "spreadsheet",
            "icon": "fa-file-csv",
            "max_size": 5 * 1024 * 1024,  # 5MB
            "is_active": True
        },
        {
            "id": generate_id("filetype"),
            "name": "ZIP Archive",
            "description": "ZIP Compressed Archive",
            "extension": ".zip",
            "mime_type": "application/zip",
            "category": "archive",
            "icon": "fa-file-archive",
            "max_size": 20 * 1024 * 1024,  # 20MB
            "is_active": True
        }
    ]
    
    file_types = []
    
    for file_type_data in file_types_data:
        file_type = FileType(**file_type_data)
        db.add(file_type)
        file_types.append(file_type)
    
    db.commit()
    print(f"Created {len(file_types)} file types!")
    return file_types

def seed_vault_documents(db: Session, clients: list, file_types: list, users: list):
    """Create vault documents for clients."""
    print("Creating vault documents...")
    
    vault_documents = []
    
    # Document categories and templates by file type
    document_templates = {
        ".pdf": [
            {"name": "Tax Return", "description": "Annual tax filing documents", "tags": "tax,financial,annual"},
            {"name": "Financial Statement", "description": "Bank or investment account statement", "tags": "financial,statement,account"},
            {"name": "Insurance Policy", "description": "Insurance policy documentation", "tags": "insurance,policy,legal"},
            {"name": "Estate Plan", "description": "Estate planning documents", "tags": "estate,legal,planning"},
            {"name": "Investment Prospectus", "description": "Investment opportunity details", "tags": "investment,financial,opportunity"}
        ],
        ".docx": [
            {"name": "Client Agreement", "description": "Signed client agreement", "tags": "legal,agreement,client"},
            {"name": "Meeting Notes", "description": "Notes from client meeting", "tags": "meeting,notes,summary"},
            {"name": "Financial Plan Draft", "description": "Draft financial planning document", "tags": "planning,draft,financial"}
        ],
        ".xlsx": [
            {"name": "Budget Worksheet", "description": "Client budget planning spreadsheet", "tags": "budget,planning,financial"},
            {"name": "Investment Analysis", "description": "Analysis of investment options", "tags": "investment,analysis,financial"},
            {"name": "Retirement Projections", "description": "Retirement scenario calculations", "tags": "retirement,projections,planning"}
        ],
        ".jpg": [
            {"name": "Property Photo", "description": "Photo of client property", "tags": "property,photo,asset"},
            {"name": "ID Document", "description": "Identification document scan", "tags": "identification,legal,document"}
        ],
        ".png": [
            {"name": "Signature", "description": "Client signature", "tags": "signature,legal,document"},
            {"name": "Business Logo", "description": "Client business logo", "tags": "business,logo,branding"}
        ],
        ".csv": [
            {"name": "Transaction History", "description": "Account transaction history", "tags": "transactions,financial,history"},
            {"name": "Asset Inventory", "description": "Detailed asset inventory list", "tags": "assets,inventory,financial"}
        ],
        ".txt": [
            {"name": "Client Instructions", "description": "Instructions from client", "tags": "instructions,client,notes"},
            {"name": "Account Information", "description": "Account details and information", "tags": "account,information,details"}
        ]
    }
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.8:
            continue
            
        # Select random user as creator
        creator = random.choice(users)
        
        # Determine number of documents (2-8)
        num_documents = random.randint(2, 8)
        
        for _ in range(num_documents):
            # Select random file type
            file_type = random.choice(file_types)
            
            # Get appropriate templates for this file type
            templates = document_templates.get(file_type.extension, [])
            if not templates:
                continue
                
            # Select random template
            template = random.choice(templates)
            
            # Generate file name
            year = random.randint(2020, 2025)
            month = random.randint(1, 12)
            file_name = f"{template['name'].replace(' ', '_')}_{year}-{month:02d}{file_type.extension}"
            
            # Generate random file size (10KB to 5MB)
            file_size = random.randint(10 * 1024, min(5 * 1024 * 1024, file_type.max_size))
            
            # Generate mock content
            content_size_kb = min(file_size // 1024, 10)  # Limit to 10KB for demo
            content = generate_mock_file_content(file_type.extension, content_size_kb)
            
            # Calculate checksum
            checksum = calculate_checksum(content)
            
            # Create vault document
            document = VaultDocument(
                id=generate_id("doc"),
                client_id=client.id,
                name=template["name"],
                description=template["description"],
                file_name=file_name,
                file_type=file_type.extension,
                file_size=file_size,
                mime_type=file_type.mime_type,
                content=content,  # In a real app, this might be stored separately
                storage_path=f"/storage/documents/{client.id}/{file_name}",
                checksum=checksum,
                version=random.randint(1, 3) if random.random() < 0.3 else 1,
                is_archived=random.random() < 0.2,  # 20% chance of being archived
                tags=template["tags"],
                created_by=creator.id,
                created_at=fake.date_time_between(start_date='-2y', end_date='now'),
                updated_at=fake.date_time_between(start_date='-1y', end_date='now')
            )
            
            db.add(document)
            vault_documents.append(document)
    
    db.commit()
    print(f"Created {len(vault_documents)} vault documents!")
    return vault_documents

def seed_attachments(db: Session, clients: list, file_types: list, users: list):
    """Create attachments for various entities."""
    print("Creating attachments...")
    
    attachments = []
    
    # Entity types and their count
    entity_types = {
        "note": db.query(Note).count(),
        "task": db.query(Task).count(),
        "client": len(clients)
    }
    
    # Skip if no entities found yet
    if all(count == 0 for count in entity_types.values()):
        # We'll create some attachments tied to clients for now
        entity_types = {"client": len(clients)}
    
    # Attachment templates by file type
    attachment_templates = {
        ".pdf": [
            {"name": "Statement", "description": "Financial statement"},
            {"name": "Report", "description": "Analysis report"}
        ],
        ".docx": [
            {"name": "Letter", "description": "Client communication"},
            {"name": "Memo", "description": "Internal memo"}
        ],
        ".jpg": [
            {"name": "Receipt", "description": "Expense receipt"},
            {"name": "Image", "description": "Supporting image"}
        ],
        ".xlsx": [
            {"name": "Calculation", "description": "Financial calculation"},
            {"name": "Spreadsheet", "description": "Data spreadsheet"}
        ]
    }
    
    # Create 10-30 attachments
    num_attachments = random.randint(10, 30)
    
    for _ in range(num_attachments):
        # Select random entity type
        entity_type = random.choice(list(entity_types.keys()))
        
        # Select random entity ID
        if entity_type == "client" and clients:
            entity = random.choice(clients)
            entity_id = entity.id
        elif entity_type == "note" and entity_types["note"] > 0:
            note_id = db.query(Note.id).order_by(func.random()).first()[0]
            entity_id = note_id
        elif entity_type == "task" and entity_types["task"] > 0:
            task_id = db.query(Task.id).order_by(func.random()).first()[0]
            entity_id = task_id
        else:
            if clients:
                entity = random.choice(clients)
                entity_type = "client"
                entity_id = entity.id
            else:
                continue
        
        # Select random file type
        file_type = random.choice(file_types)
        
        # Get appropriate templates for this file type
        templates = attachment_templates.get(file_type.extension, [])
        if not templates:
            templates = [{"name": "File", "description": "Attached file"}]
        
        # Select random template
        template = random.choice(templates)
        
        # Generate file name
        timestamp = datetime.now().strftime("%Y%m%d")
        file_name = f"{template['name'].replace(' ', '_')}_{timestamp}{file_type.extension}"
        
        # Generate random file size (5KB to 1MB)
        file_size = random.randint(5 * 1024, min(1 * 1024 * 1024, file_type.max_size))
        
        # Generate mock content
        content_size_kb = min(file_size // 1024, 5)  # Limit to 5KB for demo
        content = generate_mock_file_content(file_type.extension, content_size_kb)
        
        # Calculate checksum
        checksum = calculate_checksum(content)
        
        # Select random creator
        creator = random.choice(users)
        
        # Create attachment
        attachment = Attachment(
            id=generate_id("attach"),
            entity_type=entity_type,
            entity_id=entity_id,
            name=f"{template['name']} - {timestamp}",
            description=template["description"],
            file_name=file_name,
            file_type=file_type.extension,
            file_size=file_size,
            mime_type=file_type.mime_type,
            content=content,  # In a real app, this might be stored separately
            storage_path=f"/storage/attachments/{entity_type}/{entity_id}/{file_name}",
            checksum=checksum,
            is_public=random.random() < 0.1,  # 10% chance of being public
            created_by=creator.id,
            created_at=fake.date_time_between(start_date='-1y', end_date='now'),
            updated_at=fake.date_time_between(start_date='-6m', end_date='now')
        )
        
        db.add(attachment)
        attachments.append(attachment)
    
    db.commit()
    print(f"Created {len(attachments)} attachments!")
    return attachments

def seed_notes(db: Session, clients: list, users: list):
    """Create notes for clients."""
    print("Creating client notes...")
    
    notes = []
    
    # Note categories and templates
    note_categories = ["meeting", "phone_call", "email", "observation", "planning", "internal"]
    
    note_templates = {
        "meeting": [
            {"title": "Initial Consultation", "content": "Met with client to discuss financial goals and current situation. {{details}}"},
            {"title": "Annual Review", "content": "Conducted annual portfolio review with client. {{details}}"},
            {"title": "Estate Planning", "content": "Discussed estate planning options and next steps. {{details}}"},
            {"title": "Retirement Planning", "content": "Reviewed retirement projections and made adjustments. {{details}}"}
        ],
        "phone_call": [
            {"title": "Client Check-in", "content": "Called client to check on recent life changes. {{details}}"},
            {"title": "Investment Discussion", "content": "Discussed market volatility and investment strategy. {{details}}"},
            {"title": "Follow-up", "content": "Follow-up call regarding previous meeting action items. {{details}}"}
        ],
        "email": [
            {"title": "Document Request", "content": "Requested additional documents for financial planning. {{details}}"},
            {"title": "Information Update", "content": "Client provided updates to financial situation via email. {{details}}"},
            {"title": "Portfolio Changes", "content": "Communicated portfolio adjustments to client. {{details}}"}
        ],
        "observation": [
            {"title": "Client Risk Tolerance", "content": "Observations regarding client's risk tolerance and investment behavior. {{details}}"},
            {"title": "Financial Concerns", "content": "Noted client's primary financial concerns and priorities. {{details}}"},
            {"title": "Life Changes", "content": "Observed significant life changes that may impact financial planning. {{details}}"}
        ],
        "planning": [
            {"title": "Tax Planning", "content": "Notes on tax planning strategies for client. {{details}}"},
            {"title": "Education Planning", "content": "Planning for children's education expenses. {{details}}"},
            {"title": "Charitable Giving", "content": "Charitable giving strategy and opportunities. {{details}}"}
        ],
        "internal": [
            {"title": "Action Required", "content": "Internal note regarding actions needed for client. {{details}}"},
            {"title": "Account Review", "content": "Internal review of client accounts and performance. {{details}}"},
            {"title": "Compliance Note", "content": "Compliance considerations for client situation. {{details}}"}
        ]
    }
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.9:
            continue
            
        # Determine number of notes (2-10)
        num_notes = random.randint(2, 10)
        
        for _ in range(num_notes):
            # Select random creator
            creator = random.choice(users)
            
            # Select random category and template
            category = random.choice(note_categories)
            template = random.choice(note_templates.get(category, [{"title": "Note", "content": "Client note. {{details}}"}]))
            
            # Generate content
            details = "\n\n" + fake.paragraph(nb_sentences=random.randint(2, 5))
            content = template["content"].replace("{{details}}", details)
            
            # Create note
            note = Note(
                id=generate_id("note"),
                client_id=client.id,
                title=template["title"],
                content=content,
                category=category,
                is_pinned=random.random() < 0.2,  # 20% chance of being pinned
                is_private=random.random() < 0.1,  # 10% chance of being private
                created_by=creator.id,
                created_at=fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=fake.date_time_between(start_date='-6m', end_date='now')
            )
            
            db.add(note)
            notes.append(note)
    
    db.commit()
    print(f"Created {len(notes)} client notes!")
    return notes

def seed_tasks(db: Session, clients: list, users: list):
    """Create tasks for clients."""
    print("Creating client tasks...")
    
    tasks = []
    
    # Task categories, priorities, and status options
    task_categories = ["follow_up", "document", "planning", "meeting", "review", "administrative"]
    task_priorities = ["low", "medium", "high", "urgent"]
    task_statuses = ["pending", "in_progress", "completed", "cancelled"]
    
    # Task templates by category
    task_templates = {
        "follow_up": [
            {"title": "Follow up on investment questions", "description": "Contact client about investment questions from last meeting"},
            {"title": "Check on document submission", "description": "Verify if client has submitted requested documents"},
            {"title": "Follow up on action items", "description": "Ensure client has completed their action items"}
        ],
        "document": [
            {"title": "Collect tax returns", "description": "Request last year's tax returns from client"},
            {"title": "Update client agreement", "description": "Have client sign updated client agreement"},
            {"title": "Process new account forms", "description": "Complete paperwork for new account opening"}
        ],
        "planning": [
            {"title": "Create retirement projection", "description": "Develop retirement projection based on client data"},
            {"title": "Update financial plan", "description": "Incorporate recent changes into financial plan"},
            {"title": "Research college funding options", "description": "Research options for client's children's education"}
        ],
        "meeting": [
            {"title": "Schedule quarterly review", "description": "Set up next quarterly review meeting with client"},
            {"title": "Prepare for annual review", "description": "Gather materials for comprehensive annual review"},
            {"title": "Book estate planning meeting", "description": "Schedule meeting with estate attorney and client"}
        ],
        "review": [
            {"title": "Review investment performance", "description": "Analyze client portfolio performance and prepare report"},
            {"title": "Review insurance coverage", "description": "Assess current insurance coverage for adequacy"},
            {"title": "Review tax planning strategies", "description": "Identify tax optimization opportunities"}
        ],
        "administrative": [
            {"title": "Update CRM data", "description": "Ensure client information is current in CRM system"},
            {"title": "Process account transfer", "description": "Handle paperwork for account consolidation"},
            {"title": "Update beneficiary information", "description": "Ensure beneficiary designations are current"}
        ]
    }
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.9:
            continue
            
        # Determine number of tasks (1-5)
        num_tasks = random.randint(1, 5)
        
        for _ in range(num_tasks):
            # Select random creator and assignee
            creator = random.choice(users)
            assignee = random.choice(users) if random.random() < 0.8 else creator
            
            # Select random category
            category = random.choice(task_categories)
            
            # Select random priority (weighted towards medium)
            priority_weights = [0.2, 0.5, 0.2, 0.1]  # low, medium, high, urgent
            priority = random.choices(task_priorities, weights=priority_weights, k=1)[0]
            
            # Select random status (weighted towards pending/in progress)
            status_weights = [0.4, 0.3, 0.2, 0.1]  # pending, in_progress, completed, cancelled
            status = random.choices(task_statuses, weights=status_weights, k=1)[0]
            
            # Get template based on category
            templates = task_templates.get(category, [{"title": "Client task", "description": "Task related to client"}])
            template = random.choice(templates)
            
            # Determine dates
            created_at = fake.date_time_between(start_date='-3m', end_date='now')
            updated_at = fake.date_time_between(start_date=created_at, end_date='now')
            
            # Due date (between creation and 2 months from now)
            due_date = fake.date_between(start_date=created_at, end_date='+2m')
            
            # Completion date (if completed)
            completion_date = None
            if status == "completed":
                completion_date = fake.date_time_between(start_date=created_at, end_date=due_date if random.random() < 0.7 else updated_at)
            
            # Estimated and actual hours
            estimated_hours = round(random.uniform(0.5, 5.0), 1) if random.random() < 0.7 else None
            actual_hours = round(random.uniform(0.3, estimated_hours * 1.5), 1) if estimated_hours and status == "completed" else None
            
            # Create task
            task = Task(
                id=generate_id("task"),
                client_id=client.id,
                title=template["title"],
                description=template["description"],
                due_date=due_date,
                priority=priority,
                status=status,
                category=category,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours,
                completion_date=completion_date,
                assigned_to=assignee.id,
                created_by=creator.id,
                created_at=created_at,
                updated_at=updated_at
            )
            
            db.add(task)
            tasks.append(task)
    
    db.commit()
    print(f"Created {len(tasks)} client tasks!")
    return tasks

def seed_alerts(db: Session, clients: list, users: list):
    """Create system and client alerts."""
    print("Creating alerts...")
    
    alerts = []
    
    # Alert types, severities, and statuses
    alert_types = ["deadline", "compliance", "review", "milestone", "system"]
    alert_severities = ["info", "warning", "error", "critical"]
    alert_statuses = ["active", "acknowledged", "resolved", "dismissed"]
    
    # Alert templates by type
    alert_templates = {
        "deadline": [
            {"title": "Tax filing deadline approaching", "description": "Client's tax filing deadline is within 30 days"},
            {"title": "Required minimum distribution deadline", "description": "RMD deadline approaching for retirement accounts"}
        ],
        "compliance": [
            {"title": "Compliance review required", "description": "Annual compliance review due for client account"},
            {"title": "Missing required documentation", "description": "Client file missing required documentation for compliance"}
        ],
        "review": [
            {"title": "Annual review due", "description": "Client annual review is due within 30 days"},
            {"title": "Portfolio rebalance needed", "description": "Client portfolio requires rebalancing"}
        ],
        "milestone": [
            {"title": "Client birthday", "description": "Client birthday approaching - consider card/gift"},
            {"title": "Client retirement date", "description": "Client's planned retirement date is approaching"}
        ],
        "system": [
            {"title": "System maintenance", "description": "Scheduled system maintenance may affect availability"},
            {"title": "Data update completed", "description": "Automated data update for client accounts completed"}
        ]
    }
    
    # Create 15-25 alerts
    num_alerts = random.randint(15, 25)
    
    for _ in range(num_alerts):
        # Determine if this is a client-specific or system alert
        is_client_alert = random.random() < 0.8  # 80% chance of being client-specific
        
        # Select random client if client alert
        client = random.choice(clients) if is_client_alert and clients else None
        client_id = client.id if client else None
        
        # Select random alert type
        alert_type = random.choice(alert_types)
        
        # Select random severity (weighted)
        severity_weights = [0.5, 0.3, 0.15, 0.05]  # info, warning, error, critical
        severity = random.choices(alert_severities, weights=severity_weights, k=1)[0]
        
        # Select random status (weighted towards active)
        status_weights = [0.6, 0.2, 0.15, 0.05]  # active, acknowledged, resolved, dismissed
        status = random.choices(alert_statuses, weights=status_weights, k=1)[0]
        
        # Get template based on type
        templates = alert_templates.get(alert_type, [{"title": "Alert", "description": "System alert"}])
        template = random.choice(templates)
        
        # Create dates
        created_at = fake.date_time_between(start_date='-1m', end_date='now')
        
        # Handle acknowledgement and resolution
        acknowledged_by = None
        acknowledged_at = None
        resolved_by = None
        resolved_at = None
        
        if status == "acknowledged" or status == "resolved":
            acknowledger = random.choice(users)
            acknowledged_by = acknowledger.id
            acknowledged_at = fake.date_time_between(start_date=created_at, end_date='now')
        
        if status == "resolved":
            resolver = random.choice(users)
            resolved_by = resolver.id
            resolved_at = fake.date_time_between(start_date=acknowledged_at or created_at, end_date='now')
        
        # Set expiration date
        expires_at = fake.date_time_between(start_date='+1d', end_date='+30d') if random.random() < 0.7 else None
        
        # Create alert
        alert = Alert(
            id=generate_id("alert"),
            client_id=client_id,
            title=template["title"],
            description=template["description"] + (f" for {client.first_name} {client.last_name}" if client else ""),
            type=alert_type,
            severity=severity,
            status=status,
            action_required=(severity in ["warning", "error", "critical"] and random.random() < 0.7),
            action_url=f"/clients/{client_id}/profile" if client_id and random.random() < 0.5 else None,
            expires_at=expires_at,
            acknowledged_by=acknowledged_by,
            acknowledged_at=acknowledged_at,
            resolved_by=resolved_by,
            resolved_at=resolved_at,
            created_at=created_at,
            updated_at=fake.date_time_between(start_date=created_at, end_date='now')
        )
        
        db.add(alert)
        alerts.append(alert)
    
    db.commit()
    print(f"Created {len(alerts)} alerts!")
    return alerts

if __name__ == "__main__":
    seed_document_data()