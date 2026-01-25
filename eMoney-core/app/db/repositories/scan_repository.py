# db/repositories/scan_repository.py

import logging
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db.models import Scan, ScanStatus, ScanEntityResult
logger = logging.getLogger(__name__)

class ScanRepository:
    """Repository for Scan entity operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self,
                    scan_type: str,
                    entity_types: List[str],
                    organization_id: Optional[str] = None,
                    scan_config: Optional[Dict[str, Any]] = None) -> tuple[Scan, List[ScanEntityResult]]:
        """
        Create a new scan with entity results.
        
        Args:
            scan_type: Type of scan (auth, contact, etc.)
            entity_types: List of entity types to scan
            organization_id: Organization ID (optional)
            scan_config: Complete scan configuration (optional)
            
        Returns:
            tuple[Scan, List[ScanEntityResult]]: Created scan and its entity results
        """
        scan = Scan(
            scan_type=scan_type,
            entity_types=entity_types,
            organization_id=organization_id,
            scan_config=scan_config,
            status=ScanStatus.PENDING
        )
        self.session.add(scan)
        await self.session.flush()
        
        # Create entity results for each entity type
        entity_results = []
        for entity_type in entity_types:
            entity_result = ScanEntityResult(
                scan_id=scan.id,
                entity_type=entity_type,
                status="pending"
            )
            self.session.add(entity_result)
            entity_results.append(entity_result)
            
        await self.session.flush()
        await self.session.commit()
        
        return scan, entity_results
    
    async def get_by_id(self, scan_id: str) -> Optional[Scan]:
        """
        Get a scan by ID.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            Optional[Scan]: Scan if found, None otherwise
        """
        query = select(Scan).where(Scan.id == scan_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_entity_results(self, scan_id: str) -> List[ScanEntityResult]:
        """
        Get all entity results for a scan.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            List[ScanEntityResult]: List of entity results
        """
        query = select(ScanEntityResult).where(ScanEntityResult.scan_id == scan_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_status(self, 
                           scan_id: str, 
                           scan_status: ScanStatus) -> Optional[Scan]:
        """
        Update scan status.
        
        Args:
            scan_id: Scan ID
            scan_status: New scan status
            
        Returns:
            Optional[Scan]: Updated scan if found, None otherwise
        """
        try:
            update_values = {"status": scan_status}
            
            # Set timestamps based on status
            if scan_status == ScanStatus.RUNNING:
                update_values["started_at"] = datetime.utcnow()
            
            if scan_status in (ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED):
                update_values["completed_at"] = datetime.utcnow()
            
            # Add timestamp for PAUSED status
            if scan_status == ScanStatus.PAUSED:
                update_values["updated_at"] = datetime.utcnow()
                
            query = update(Scan).where(Scan.id == scan_id).values(**update_values).returning(Scan)
            result = await self.session.execute(query)
            updated_scan = result.scalar_one_or_none()
            
            if updated_scan:
                await self.session.commit()
                logger.info(f"Updated scan {scan_id} status to {scan_status.value}, completed_at: {update_values.get('completed_at')}")
                return updated_scan
            else:
                logger.warning(f"Scan {scan_id} not found for status update")
                return None
                
        except Exception as e:
            logger.error(f"Error updating scan {scan_id} status: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise
    
    async def update_entity_result(self, entity_id: str, **update_values) -> Optional[ScanEntityResult]:
        """
        Update an entity result by ID.
        
        Args:
            entity_id: ID of the entity result to update
            **update_values: Values to update
            
        Returns:
            Optional[ScanEntityResult]: Updated entity result if found, None otherwise
        """
        try:
            # Print update values for debugging
            logger.debug(f"Updating entity {entity_id} with values: {update_values}")
            
            # Perform the update
            query = update(ScanEntityResult).where(ScanEntityResult.id == entity_id).values(**update_values).returning(ScanEntityResult)
            result = await self.session.execute(query)
            updated_entity = result.scalar_one_or_none()
            
            # Log the result
            if updated_entity:
                logger.debug(f"Updated entity {entity_id} - record_count is now {updated_entity.record_count}")
                await self.session.commit()
                return updated_entity
            else:
                logger.warning(f"Entity {entity_id} not found for update")
                return None
        except Exception as e:
            logger.error(f"Error updating entity {entity_id}: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise

    async def get_filtered(self,
                       limit: int = 20,
                       offset: int = 0,
                       scan_type: Optional[str] = None,
                       scan_status: Optional[str] = None,
                       organization_id: Optional[str] = None) -> List[Scan]:
        """
        Get filtered scans with pagination.
        
        Args:
            limit: Maximum number of scans to return
            offset: Offset for pagination
            scan_type: Filter by scan type
            scan_status: Filter by scan status
            organization_id: Filter by organization ID
            
        Returns:
            List[Scan]: List of scans matching the filters
        """
        query = select(Scan)
        
        # Apply filters if provided
        if scan_type:
            query = query.where(Scan.scan_type == scan_type)
        if scan_status:
            # Handle the case when scan_status is a string instead of ScanStatus enum
            if isinstance(scan_status, str):
                try:
                    status_enum = ScanStatus[scan_status.upper()]
                    query = query.where(Scan.status == status_enum)
                except (KeyError, ValueError):
                    logger.warning(f"Invalid status filter: {scan_status}")
            else:
                query = query.where(Scan.status == scan_status)
        if organization_id:
            query = query.where(Scan.organization_id == organization_id)
        
        # Apply pagination
        query = query.order_by(Scan.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_filtered(self,
                            scan_type: Optional[str] = None,
                            scan_status: Optional[str] = None,
                            organization_id: Optional[str] = None) -> int:
        """
        Count filtered scans.
        
        Args:
            scan_type: Filter by scan type
            scan_status: Filter by scan status
            organization_id: Filter by organization ID
            
        Returns:
            int: Count of scans matching the filters
        """
        from sqlalchemy.sql import func
        
        query = select(func.count()).select_from(Scan)
        
        # Apply filters if provided
        if scan_type:
            query = query.where(Scan.scan_type == scan_type)
        if scan_status:
            # Handle the case when scan_status is a string instead of ScanStatus enum
            if isinstance(scan_status, str):
                try:
                    status_enum = ScanStatus[scan_status.upper()]
                    query = query.where(Scan.status == status_enum)
                except (KeyError, ValueError):
                    logger.warning(f"Invalid status filter: {scan_status}")
            else:
                query = query.where(Scan.status == scan_status)
        if organization_id:
            query = query.where(Scan.organization_id == organization_id)
        
        result = await self.session.execute(query)
        return result.scalar_one() or 0
    
    async def delete_scan(self, scan_id: str) -> bool:
        """
        Delete a scan by ID along with its associated entity results.
        
        Args:
            scan_id: ID of the scan to delete
            
        Returns:
            bool: True if the scan was deleted, False otherwise
        """
        try:
            # First verify the scan exists
            scan = await self.get_by_id(scan_id)
            if not scan:
                logger.warning(f"Scan {scan_id} not found for deletion")
                return False
            
            # The relationship has cascade="all, delete-orphan", so deleting the
            # scan should automatically delete all associated entity results.
            # However, we'll explicitly delete entity results first for clarity.
            entity_delete_query = delete(ScanEntityResult).where(ScanEntityResult.scan_id == scan_id)
            await self.session.execute(entity_delete_query)
            
            # Then delete the scan
            scan_delete_query = delete(Scan).where(Scan.id == scan_id)
            await self.session.execute(scan_delete_query)
            
            # Commit the transaction
            await self.session.commit()
            logger.info(f"Successfully deleted scan {scan_id} and its entity results")
            return True
        except Exception as e:
            logger.error(f"Error deleting scan {scan_id}: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise
    
    async def update_entity_results_status(self, scan_id: str, entity_status: str) -> List[ScanEntityResult]:
        """
        Update the status of all entity results for a scan.
        
        Args:
            scan_id: ID of the scan
            entity_status: New status for entity results
            
        Returns:
            List[ScanEntityResult]: Updated entity results
        """
        try:
            # Update all entity results for the scan
            query = update(ScanEntityResult).where(
                ScanEntityResult.scan_id == scan_id
            ).values(
                status=entity_status, 
                updated_at=datetime.utcnow()
            ).returning(ScanEntityResult)
            
            result = await self.session.execute(query)
            updated_entities = result.scalars().all()
            
            if updated_entities:
                logger.info(f"Updated status to '{entity_status}' for {len(updated_entities)} entity results of scan {scan_id}")
                await self.session.commit()
                return updated_entities
            else:
                logger.warning(f"No entity results found for scan {scan_id}")
                return []
        except Exception as e:
            logger.error(f"Error updating entity results status for scan {scan_id}: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise