from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.documents import VaultDocument, Note, Task, Alert, FileType, Attachment
from services.service_base import BaseService
from datetime import datetime
import uuid
import base64
import hashlib

class FileTypeService(BaseService[FileType]):
    """
    Service for managing file type definitions
    Handles CRUD operations and validation for supported file types
    """
    
    def __init__(self, db: Session):
        super().__init__(db, FileType)
    
    def get_all_file_types(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all file types
        
        Args:
            include_inactive: Whether to include inactive file types
            
        Returns:
            List of file type dictionaries
        """
        query = self.db.query(FileType)
        if not include_inactive:
            query = query.filter(FileType.is_active == True)
        
        file_types = query.all()
        return [self._file_type_to_dict(file_type) for file_type in file_types]
    
    def get_file_type_by_id(self, file_type_id: str) -> Optional[Dict[str, Any]]:
        """Get a file type by ID"""
        file_type = self.db.query(FileType).filter(FileType.id == file_type_id).first()
        if not file_type:
            return None
        return self._file_type_to_dict(file_type)
    
    def get_file_type_by_extension(self, extension: str) -> Optional[Dict[str, Any]]:
        """
        Get a file type by extension
        
        Args:
            extension: File extension (e.g., ".pdf", "pdf")
            
        Returns:
            File type dictionary or None
        """
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        file_type = self.db.query(FileType).filter(FileType.extension == extension).first()
        if not file_type:
            return None
        return self._file_type_to_dict(file_type)
    
    def get_file_types_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all file types in a specific category"""
        file_types = self.db.query(FileType).filter(
            FileType.category == category,
            FileType.is_active == True
        ).all()
        return [self._file_type_to_dict(file_type) for file_type in file_types]
    
    def validate_file_type(self, extension: str, file_size: int) -> Dict[str, Any]:
        """
        Validate if a file type is supported and within size limits
        
        Args:
            extension: File extension
            file_size: File size in bytes
            
        Returns:
            Dictionary with validation result and file type info
        """
        file_type = self.get_file_type_by_extension(extension)
        
        if not file_type:
            return {
                "valid": False,
                "error": f"File type '{extension}' is not supported"
            }
        
        if not file_type.get('is_active'):
            return {
                "valid": False,
                "error": f"File type '{extension}' is currently not accepted"
            }
        
        max_size = file_type.get('max_size')
        if max_size and file_size > max_size:
            return {
                "valid": False,
                "error": f"File size exceeds maximum allowed size of {max_size} bytes"
            }
        
        return {
            "valid": True,
            "file_type": file_type
        }
    
    def create_file_type(self, file_type_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Create a new file type"""
        if 'id' not in file_type_data:
            file_type_data['id'] = str(uuid.uuid4())
        
        # Ensure extension starts with dot
        if 'extension' in file_type_data and not file_type_data['extension'].startswith('.'):
            file_type_data['extension'] = f".{file_type_data['extension']}"
        
        if 'created_at' not in file_type_data:
            file_type_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in file_type_data:
            file_type_data['updated_at'] = datetime.utcnow()
        
        file_type = FileType(**file_type_data)
        self.db.add(file_type)
        self.db.commit()
        self.db.refresh(file_type)
        
        return self._file_type_to_dict(file_type)
    
    def update_file_type(self, file_type_id: str, file_type_data: Dict[str, Any], user_id: str = None) -> Optional[Dict[str, Any]]:
        """Update an existing file type"""
        file_type = self.db.query(FileType).filter(FileType.id == file_type_id).first()
        if not file_type:
            return None
        
        # Ensure extension starts with dot if being updated
        if 'extension' in file_type_data and not file_type_data['extension'].startswith('.'):
            file_type_data['extension'] = f".{file_type_data['extension']}"
            
        for key, value in file_type_data.items():
            if hasattr(file_type, key):
                setattr(file_type, key, value)
                
        file_type.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(file_type)
        
        return self._file_type_to_dict(file_type)
    
    def delete_file_type(self, file_type_id: str) -> bool:
        """Delete a file type (soft delete by marking inactive)"""
        file_type = self.db.query(FileType).filter(FileType.id == file_type_id).first()
        if not file_type:
            return False
        
        # Soft delete - mark as inactive instead of removing
        file_type.is_active = False
        file_type.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def _file_type_to_dict(self, file_type: FileType) -> Dict[str, Any]:
        """Helper method to convert FileType model to dictionary"""
        return {
            "id": file_type.id,
            "name": file_type.name,
            "description": file_type.description,
            "extension": file_type.extension,
            "mime_type": file_type.mime_type,
            "category": file_type.category,
            "icon": file_type.icon,
            "max_size": file_type.max_size,
            "is_active": file_type.is_active,
            "created_at": file_type.created_at.isoformat() if file_type.created_at else None,
            "updated_at": file_type.updated_at.isoformat() if file_type.updated_at else None
        }

class AttachmentService(BaseService[Attachment]):
    """
    Service for managing file attachments to various entities
    Handles attachment CRUD operations with content management
    """
    
    def __init__(self, db: Session):
        super().__init__(db, Attachment)
        self.file_type_service = FileTypeService(db)
    
    def get_attachments_by_entity(self, entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all attachments for a specific entity
        
        Args:
            entity_type: Type of entity (e.g., "note", "task")
            entity_id: ID of the entity
            
        Returns:
            List of attachment dictionaries
        """
        attachments = self.db.query(Attachment).filter(
            Attachment.entity_type == entity_type,
            Attachment.entity_id == entity_id
        ).order_by(Attachment.created_at.desc()).all()
        
        return [self._attachment_to_dict(attachment, include_content=False) for attachment in attachments]
    
    def get_attachment_by_id(self, attachment_id: str, include_content: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get an attachment by ID
        
        Args:
            attachment_id: Attachment ID
            include_content: Whether to include binary content
            
        Returns:
            Attachment dictionary or None
        """
        attachment = self.db.query(Attachment).filter(Attachment.id == attachment_id).first()
        if not attachment:
            return None
        return self._attachment_to_dict(attachment, include_content)
    
    def get_attachments_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all attachments created by a specific user"""
        attachments = self.db.query(Attachment).filter(
            Attachment.created_by == user_id
        ).order_by(Attachment.created_at.desc()).limit(limit).all()
        
        return [self._attachment_to_dict(attachment, include_content=False) for attachment in attachments]
    
    def search_attachments(self, search_term: str, entity_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search attachments by name or description
        
        Args:
            search_term: Search string
            entity_type: Optional entity type filter
            limit: Maximum results to return
            
        Returns:
            List of matching attachments
        """
        query = self.db.query(Attachment).filter(
            or_(
                Attachment.name.ilike(f'%{search_term}%'),
                Attachment.description.ilike(f'%{search_term}%'),
                Attachment.file_name.ilike(f'%{search_term}%')
            )
        )
        
        if entity_type:
            query = query.filter(Attachment.entity_type == entity_type)
        
        attachments = query.order_by(Attachment.created_at.desc()).limit(limit).all()
        return [self._attachment_to_dict(attachment, include_content=False) for attachment in attachments]
    
    def create_attachment(self, attachment_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """
        Create a new attachment with validation
        
        Args:
            attachment_data: Attachment data including content
            user_id: ID of user creating attachment
            
        Returns:
            Created attachment dictionary
        """
        if 'id' not in attachment_data:
            attachment_data['id'] = str(uuid.uuid4())
        
        # Validate file type
        file_type = attachment_data.get('file_type')
        file_size = attachment_data.get('file_size', 0)
        
        if file_type:
            validation = self.file_type_service.validate_file_type(file_type, file_size)
            if not validation['valid']:
                raise ValueError(validation['error'])
        
        # Calculate checksum if content provided
        if 'content' in attachment_data and attachment_data['content']:
            if isinstance(attachment_data['content'], str):
                # Assume base64 encoded
                content_bytes = base64.b64decode(attachment_data['content'])
                attachment_data['content'] = content_bytes
            else:
                content_bytes = attachment_data['content']
            
            attachment_data['checksum'] = hashlib.sha256(content_bytes).hexdigest()
        
        if 'created_at' not in attachment_data:
            attachment_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in attachment_data:
            attachment_data['updated_at'] = datetime.utcnow()
            
        if user_id and 'created_by' not in attachment_data:
            attachment_data['created_by'] = user_id
        
        attachment = Attachment(**attachment_data)
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        
        return self._attachment_to_dict(attachment, include_content=False)
    
    def update_attachment(self, attachment_id: str, attachment_data: Dict[str, Any], user_id: str = None) -> Optional[Dict[str, Any]]:
        """Update an existing attachment"""
        attachment = self.db.query(Attachment).filter(Attachment.id == attachment_id).first()
        if not attachment:
            return None
        
        # Recalculate checksum if content updated
        if 'content' in attachment_data and attachment_data['content']:
            if isinstance(attachment_data['content'], str):
                content_bytes = base64.b64decode(attachment_data['content'])
                attachment_data['content'] = content_bytes
            else:
                content_bytes = attachment_data['content']
            
            attachment_data['checksum'] = hashlib.sha256(content_bytes).hexdigest()
            
        for key, value in attachment_data.items():
            if hasattr(attachment, key):
                setattr(attachment, key, value)
                
        attachment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(attachment)
        
        return self._attachment_to_dict(attachment, include_content=False)
    
    def delete_attachment(self, attachment_id: str) -> bool:
        """Delete an attachment"""
        attachment = self.db.query(Attachment).filter(Attachment.id == attachment_id).first()
        if not attachment:
            return False
        
        self.db.delete(attachment)
        self.db.commit()
        
        return True
    
    def get_attachment_statistics(self, entity_type: str = None) -> Dict[str, Any]:
        """
        Get statistics about attachments
        
        Args:
            entity_type: Optional entity type filter
            
        Returns:
            Dictionary with statistics
        """
        query = self.db.query(Attachment)
        
        if entity_type:
            query = query.filter(Attachment.entity_type == entity_type)
        
        total_count = query.count()
        total_size = self.db.query(func.sum(Attachment.file_size)).filter(
            Attachment.entity_type == entity_type if entity_type else True
        ).scalar() or 0
        
        return {
            "total_attachments": total_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    def _attachment_to_dict(self, attachment: Attachment, include_content: bool = False) -> Dict[str, Any]:
        """Helper method to convert Attachment model to dictionary"""
        result = {
            "id": attachment.id,
            "entity_type": attachment.entity_type,
            "entity_id": attachment.entity_id,
            "name": attachment.name,
            "description": attachment.description,
            "file_name": attachment.file_name,
            "file_type": attachment.file_type,
            "file_size": attachment.file_size,
            "mime_type": attachment.mime_type,
            "storage_path": attachment.storage_path,
            "checksum": attachment.checksum,
            "is_public": attachment.is_public,
            "created_by": attachment.created_by,
            "created_at": attachment.created_at.isoformat() if attachment.created_at else None,
            "updated_at": attachment.updated_at.isoformat() if attachment.updated_at else None
        }
        
        if include_content and attachment.content:
            result["content"] = base64.b64encode(attachment.content).decode('utf-8')
        
        return result

class DocumentService(BaseService[VaultDocument]):
    """
    Service for managing vault documents
    Handles document storage, retrieval, and versioning
    """
    
    def __init__(self, db: Session):
        super().__init__(db, VaultDocument)
        self.file_type_service = FileTypeService(db)
    
    def get_client_documents(self, client_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        """
        Get all documents for a client
        
        Args:
            client_id: Client ID
            include_archived: Whether to include archived documents
            
        Returns:
            List of document dictionaries
        """
        query = self.db.query(VaultDocument).filter(VaultDocument.client_id == client_id)
        
        if not include_archived:
            query = query.filter(VaultDocument.is_archived == False)
        
        documents = query.order_by(VaultDocument.created_at.desc()).all()
        return [self._document_to_dict(document, include_content=False) for document in documents]
    
    def get_document_by_id(self, document_id: str, include_content: bool = False) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        document = self.db.query(VaultDocument).filter(VaultDocument.id == document_id).first()
        if not document:
            return None
        return self._document_to_dict(document, include_content)
    
    def get_documents_by_type(self, client_id: str, file_type: str) -> List[Dict[str, Any]]:
        """Get all documents of a specific type for a client"""
        documents = self.db.query(VaultDocument).filter(
            VaultDocument.client_id == client_id,
            VaultDocument.file_type == file_type,
            VaultDocument.is_archived == False
        ).order_by(VaultDocument.created_at.desc()).all()
        
        return [self._document_to_dict(document, include_content=False) for document in documents]
    
    def search_documents(self, client_id: str, search_term: str, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search documents by name, description, or tags
        
        Args:
            client_id: Client ID
            search_term: Search string
            tags: Optional list of tags to filter by
            
        Returns:
            List of matching documents
        """
        query = self.db.query(VaultDocument).filter(
            VaultDocument.client_id == client_id,
            VaultDocument.is_archived == False,
            or_(
                VaultDocument.name.ilike(f'%{search_term}%'),
                VaultDocument.description.ilike(f'%{search_term}%'),
                VaultDocument.file_name.ilike(f'%{search_term}%')
            )
        )
        
        if tags:
            # Filter by tags (assuming comma-separated storage)
            for tag in tags:
                query = query.filter(VaultDocument.tags.ilike(f'%{tag}%'))
        
        documents = query.order_by(VaultDocument.created_at.desc()).all()
        return [self._document_to_dict(document, include_content=False) for document in documents]
    
    def create_document(self, document_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Create a new document with validation"""
        if 'id' not in document_data:
            document_data['id'] = str(uuid.uuid4())
        
        # Validate file type
        file_type = document_data.get('file_type')
        file_size = document_data.get('file_size', 0)
        
        if file_type:
            validation = self.file_type_service.validate_file_type(file_type, file_size)
            if not validation['valid']:
                raise ValueError(validation['error'])
        
        # Calculate checksum if content provided
        if 'content' in document_data and document_data['content']:
            if isinstance(document_data['content'], str):
                content_bytes = base64.b64decode(document_data['content'])
                document_data['content'] = content_bytes
            else:
                content_bytes = document_data['content']
            
            document_data['checksum'] = hashlib.sha256(content_bytes).hexdigest()
        
        if 'created_at' not in document_data:
            document_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in document_data:
            document_data['updated_at'] = datetime.utcnow()
            
        if user_id and 'created_by' not in document_data:
            document_data['created_by'] = user_id
        
        document = VaultDocument(**document_data)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return self._document_to_dict(document, include_content=False)
    
    def update_document(self, document_id: str, document_data: Dict[str, Any], user_id: str = None) -> Optional[Dict[str, Any]]:
        """Update an existing document"""
        document = self.db.query(VaultDocument).filter(VaultDocument.id == document_id).first()
        if not document:
            return None
        
        # Increment version if content is updated
        if 'content' in document_data:
            document.version += 1
            
            if isinstance(document_data['content'], str):
                content_bytes = base64.b64decode(document_data['content'])
                document_data['content'] = content_bytes
            else:
                content_bytes = document_data['content']
            
            document_data['checksum'] = hashlib.sha256(content_bytes).hexdigest()
            
        for key, value in document_data.items():
            if hasattr(document, key):
                setattr(document, key, value)
                
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(document)
        
        return self._document_to_dict(document, include_content=False)
    
    def archive_document(self, document_id: str) -> bool:
        """Archive a document (soft delete)"""
        document = self.db.query(VaultDocument).filter(VaultDocument.id == document_id).first()
        if not document:
            return False
        
        document.is_archived = True
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document (hard delete)"""
        document = self.db.query(VaultDocument).filter(VaultDocument.id == document_id).first()
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        
        return True
    
    def _document_to_dict(self, document: VaultDocument, include_content: bool = False) -> Dict[str, Any]:
        """Helper method to convert VaultDocument model to dictionary"""
        result = {
            "id": document.id,
            "client_id": document.client_id,
            "name": document.name,
            "description": document.description,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "storage_path": document.storage_path,
            "checksum": document.checksum,
            "version": document.version,
            "is_archived": document.is_archived,
            "tags": document.tags.split(',') if document.tags else [],
            "created_by": document.created_by,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
        
        if include_content and document.content:
            result["content"] = base64.b64encode(document.content).decode('utf-8')
        
        return result

class NoteService(BaseService[Note]):
    """Service for managing client notes"""
    
    def __init__(self, db: Session):
        super().__init__(db, Note)
    
    def get_client_notes(self, client_id: str, include_private: bool = True, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get all notes for a client
        
        Args:
            client_id: Client ID
            include_private: Whether to include private notes
            user_id: Current user ID (for private note filtering)
            
        Returns:
            List of note dictionaries
        """
        query = self.db.query(Note).filter(Note.client_id == client_id)
        
        if not include_private or user_id:
            query = query.filter(
                or_(
                    Note.is_private == False,
                    Note.created_by == user_id
                )
            )
        
        notes = query.order_by(Note.is_pinned.desc(), Note.created_at.desc()).all()
        return [self._note_to_dict(note) for note in notes]
    
    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a note by ID"""
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None
        return self._note_to_dict(note)
    
    def get_pinned_notes(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all pinned notes for a client"""
        notes = self.db.query(Note).filter(
            Note.client_id == client_id,
            Note.is_pinned == True
        ).order_by(Note.created_at.desc()).all()
        
        return [self._note_to_dict(note) for note in notes]
    
    def search_notes(self, client_id: str, search_term: str, category: str = None) -> List[Dict[str, Any]]:
        """Search notes by title or content"""
        query = self.db.query(Note).filter(
            Note.client_id == client_id,
            or_(
                Note.title.ilike(f'%{search_term}%'),
                Note.content.ilike(f'%{search_term}%')
            )
        )
        
        if category:
            query = query.filter(Note.category == category)
        
        notes = query.order_by(Note.created_at.desc()).all()
        return [self._note_to_dict(note) for note in notes]
    
    def create_note(self, note_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Create a new note"""
        if 'id' not in note_data:
            note_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in note_data:
            note_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in note_data:
            note_data['updated_at'] = datetime.utcnow()
            
        if user_id and 'created_by' not in note_data:
            note_data['created_by'] = user_id
        
        note = Note(**note_data)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return self._note_to_dict(note)
    
    def update_note(self, note_id: str, note_data: Dict[str, Any], user_id: str = None) -> Optional[Dict[str, Any]]:
        """Update an existing note"""
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None
            
        for key, value in note_data.items():
            if hasattr(note, key):
                setattr(note, key, value)
                
        note.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(note)
        
        return self._note_to_dict(note)
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        note = self.db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return False
        
        self.db.delete(note)
        self.db.commit()
        
        return True
    
    def _note_to_dict(self, note: Note) -> Dict[str, Any]:
        """Helper method to convert Note model to dictionary"""
        return {
            "id": note.id,
            "client_id": note.client_id,
            "title": note.title,
            "content": note.content,
            "category": note.category,
            "is_pinned": note.is_pinned,
            "is_private": note.is_private,
            "created_by": note.created_by,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None
        }

class TaskService(BaseService[Task]):
    """Service for managing client tasks"""
    
    def __init__(self, db: Session):
        super().__init__(db, Task)
    
    def get_client_tasks(self, client_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get all tasks for a client, optionally filtered by status"""
        query = self.db.query(Task).filter(Task.client_id == client_id)
        
        if status:
            query = query.filter(Task.status == status)
        
        tasks = query.order_by(Task.due_date.asc(), Task.priority.desc()).all()
        return [self._task_to_dict(task) for task in tasks]
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        return self._task_to_dict(task)
    
    def get_user_tasks(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get all tasks assigned to a user"""
        query = self.db.query(Task).filter(Task.assigned_to == user_id)
        
        if status:
            query = query.filter(Task.status == status)
        
        tasks = query.order_by(Task.due_date.asc(), Task.priority.desc()).all()
        return [self._task_to_dict(task) for task in tasks]
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all tasks with a specific status"""
        tasks = self.db.query(Task).filter(Task.status == status).order_by(
            Task.due_date.asc(), Task.priority.desc()
        ).all()
        return [self._task_to_dict(task) for task in tasks]
    
    def get_overdue_tasks(self, client_id: str = None) -> List[Dict[str, Any]]:
        """Get all overdue tasks"""
        query = self.db.query(Task).filter(
            Task.due_date < datetime.utcnow().date(),
            Task.status.notin_(['completed', 'cancelled'])
        )
        
        if client_id:
            query = query.filter(Task.client_id == client_id)
        
        tasks = query.order_by(Task.due_date.asc()).all()
        return [self._task_to_dict(task) for task in tasks]
    
    def get_tasks_by_priority(self, priority: str, client_id: str = None) -> List[Dict[str, Any]]:
        """Get tasks by priority level"""
        query = self.db.query(Task).filter(Task.priority == priority)
        
        if client_id:
            query = query.filter(Task.client_id == client_id)
        
        tasks = query.order_by(Task.due_date.asc()).all()
        return [self._task_to_dict(task) for task in tasks]
    
    def create_task(self, task_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Create a new task"""
        if 'id' not in task_data:
            task_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in task_data:
            task_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in task_data:
            task_data['updated_at'] = datetime.utcnow()
            
        if user_id and 'created_by' not in task_data:
            task_data['created_by'] = user_id
        
        task = Task(**task_data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return self._task_to_dict(task)
    
    def update_task(self, task_id: str, task_data: Dict[str, Any], user_id: str = None) -> Optional[Dict[str, Any]]:
        """Update an existing task"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Set completion date if status changed to completed
        if 'status' in task_data and task_data['status'] == 'completed' and task.status != 'completed':
            task_data['completion_date'] = datetime.utcnow()
            
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
                
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        return self._task_to_dict(task)
    
    def complete_task(self, task_id: str, actual_hours: float = None) -> Optional[Dict[str, Any]]:
        """Mark a task as completed"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        task.status = 'completed'
        task.completion_date = datetime.utcnow()
        if actual_hours is not None:
            task.actual_hours = actual_hours
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        return self._task_to_dict(task)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        
        return True
    
    def get_task_statistics(self, client_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """Get task statistics"""
        query = self.db.query(Task)
        
        if client_id:
            query = query.filter(Task.client_id == client_id)
        if user_id:
            query = query.filter(Task.assigned_to == user_id)
        
        all_tasks = query.all()
        
        stats = {
            "total": len(all_tasks),
            "by_status": {},
            "by_priority": {},
            "overdue": 0,
            "completed": 0,
            "pending": 0
        }
        
        for task in all_tasks:
            # Count by status
            stats["by_status"][task.status] = stats["by_status"].get(task.status, 0) + 1
            
            # Count by priority
            stats["by_priority"][task.priority] = stats["by_priority"].get(task.priority, 0) + 1
            
            # Count special categories
            if task.status == 'completed':
                stats["completed"] += 1
            elif task.status in ['pending', 'in_progress']:
                stats["pending"] += 1
                if task.due_date and task.due_date < datetime.utcnow().date():
                    stats["overdue"] += 1
        
        return stats
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Helper method to convert Task model to dictionary"""
        return {
            "id": task.id,
            "client_id": task.client_id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
            "status": task.status,
            "category": task.category,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "completion_date": task.completion_date.isoformat() if task.completion_date else None,
            "assigned_to": task.assigned_to,
            "created_by": task.created_by,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }

class AlertService(BaseService[Alert]):
    """Service for managing system alerts and notifications"""
    
    def __init__(self, db: Session):
        super().__init__(db, Alert)
    
    def get_client_alerts(self, client_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get all alerts for a client"""
        query = self.db.query(Alert).filter(Alert.client_id == client_id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        alerts = query.order_by(Alert.severity.desc(), Alert.created_at.desc()).all()
        return [self._alert_to_dict(alert) for alert in alerts]
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get an alert by ID"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        return self._alert_to_dict(alert)
    
    def get_alerts_by_type(self, alert_type: str, status: str = None) -> List[Dict[str, Any]]:
        """Get all alerts with a specific type"""
        query = self.db.query(Alert).filter(Alert.type == alert_type)
        
        if status:
            query = query.filter(Alert.status == status)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        return [self._alert_to_dict(alert) for alert in alerts]
    
    def get_alerts_by_severity(self, severity: str, status: str = None) -> List[Dict[str, Any]]:
        """Get all alerts with a specific severity"""
        query = self.db.query(Alert).filter(Alert.severity == severity)
        
        if status:
            query = query.filter(Alert.status == status)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        return [self._alert_to_dict(alert) for alert in alerts]
    
    def get_active_alerts(self, client_id: str = None) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        query = self.db.query(Alert).filter(Alert.status == 'active')
        
        if client_id:
            query = query.filter(Alert.client_id == client_id)
        
        alerts = query.order_by(Alert.severity.desc(), Alert.created_at.desc()).all()
        return [self._alert_to_dict(alert) for alert in alerts]
    
    def get_critical_alerts(self, client_id: str = None) -> List[Dict[str, Any]]:
        """Get all critical severity alerts that are active"""
        query = self.db.query(Alert).filter(
            Alert.severity == 'critical',
            Alert.status == 'active'
        )
        
        if client_id:
            query = query.filter(Alert.client_id == client_id)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        return [self._alert_to_dict(alert) for alert in alerts]
    
    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert"""
        if 'id' not in alert_data:
            alert_data['id'] = str(uuid.uuid4())
        
        if 'created_at' not in alert_data:
            alert_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in alert_data:
            alert_data['updated_at'] = datetime.utcnow()
        
        alert = Alert(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return self._alert_to_dict(alert)
    
    def update_alert(self, alert_id: str, alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
            
        for key, value in alert_data.items():
            if hasattr(alert, key):
                setattr(alert, key, value)
                
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return self._alert_to_dict(alert)
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Acknowledge an alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = 'acknowledged'
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return self._alert_to_dict(alert)
    
    def resolve_alert(self, alert_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Resolve an alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = 'resolved'
        alert.resolved_by = user_id
        alert.resolved_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return self._alert_to_dict(alert)
    
    def dismiss_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Dismiss an alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = 'dismissed'
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return self._alert_to_dict(alert)
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        self.db.delete(alert)
        self.db.commit()
        
        return True
    
    def cleanup_expired_alerts(self) -> int:
        """Remove alerts that have passed their expiration date"""
        current_time = datetime.utcnow()
        
        expired_alerts = self.db.query(Alert).filter(
            Alert.expires_at.isnot(None),
            Alert.expires_at < current_time,
            Alert.status.in_(['active', 'acknowledged'])
        ).all()
        
        count = len(expired_alerts)
        
        for alert in expired_alerts:
            alert.status = 'dismissed'
            alert.updated_at = current_time
        
        self.db.commit()
        
        return count
    
    def get_alert_statistics(self, client_id: str = None) -> Dict[str, Any]:
        """Get alert statistics"""
        query = self.db.query(Alert)
        
        if client_id:
            query = query.filter(Alert.client_id == client_id)
        
        all_alerts = query.all()
        
        stats = {
            "total": len(all_alerts),
            "by_status": {},
            "by_severity": {},
            "by_type": {},
            "active": 0,
            "critical_active": 0,
            "action_required": 0
        }
        
        for alert in all_alerts:
            # Count by status
            stats["by_status"][alert.status] = stats["by_status"].get(alert.status, 0) + 1
            
            # Count by severity
            stats["by_severity"][alert.severity] = stats["by_severity"].get(alert.severity, 0) + 1
            
            # Count by type
            stats["by_type"][alert.type] = stats["by_type"].get(alert.type, 0) + 1
            
            # Count special categories
            if alert.status == 'active':
                stats["active"] += 1
                if alert.severity == 'critical':
                    stats["critical_active"] += 1
            
            if alert.action_required:
                stats["action_required"] += 1
        
        return stats
    
    def _alert_to_dict(self, alert: Alert) -> Dict[str, Any]:
        """Helper method to convert Alert model to dictionary"""
        return {
            "id": alert.id,
            "client_id": alert.client_id,
            "title": alert.title,
            "description": alert.description,
            "type": alert.type,
            "severity": alert.severity,
            "status": alert.status,
            "action_required": alert.action_required,
            "action_url": alert.action_url,
            "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "resolved_by": alert.resolved_by,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "updated_at": alert.updated_at.isoformat() if alert.updated_at else None
        }