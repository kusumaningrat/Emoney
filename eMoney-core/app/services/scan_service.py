import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.db.repositories.scan_repository import ScanRepository
from app.db.models import ScanStatus
from app.services.scan_status_service import ScanStatusService
from app.service_config import WEALTHBOX_SERVICES

logger = logging.getLogger(__name__)

class ScanService:
    """Service for scan operations"""
    
    def __init__(self, scan_repository: ScanRepository):
        self.scan_repository = scan_repository
        self._init_connectors()
        self.status_service = ScanStatusService(scan_repository)
    
    def _init_connectors(self):
        """Initialize connectors for different service types"""
        from app.connectors.client_connector import WealthboxClientConnector
        from app.connectors.opportunity_connector import WealthboxOpportunityConnector
        from app.connectors.identity_connector import WealthboxIdentityConnector
        from app.connectors.activity_connector import WealthboxActivityConnector
        from app.connectors.auth_connector import WealthboxAuthConnector

        # Initialize all connectors
        self.connectors = {
            "client": WealthboxClientConnector(),
            "opportunity": WealthboxOpportunityConnector(),
            "identity": WealthboxIdentityConnector(),
            "activity": WealthboxActivityConnector(),
            "auth": WealthboxAuthConnector()
        }
    
    def _get_connector(self, scan_type: str):
        """Get the appropriate connector for the scan type"""
        connector = self.connectors.get(scan_type)
        if not connector:
            raise ValueError(f"No connector available for scan type: {scan_type}")
        return connector
    
    def _validate_entity_types(self, scan_type: str, entity_types: List[str]) -> List[str]:
        """
        Validate entity types against available types for the service.
        Filters out any entity types that don't exist.
        
        Args:
            scan_type: Type of scan (client, opportunity, identity, activity, auth)
            entity_types: List of entity types to validate
            
        Returns:
            List[str]: List of valid entity types
        """
        # Get the service configuration
        service_config = WEALTHBOX_SERVICES.get(scan_type)
        if not service_config:
            raise ValueError(f"Invalid scan type: {scan_type}")
            
        # Get available entity types for this service
        available_types = service_config.get("entity_types", [])
        
        # Filter to include only valid entity types
        valid_types = [et for et in entity_types if et in available_types]
        
        # Log any invalid types that were removed
        invalid_types = [et for et in entity_types if et not in available_types]
        if invalid_types:
            logger.warning(f"Removed invalid entity types for {scan_type} service: {invalid_types}")
            
        if not valid_types:
            raise ValueError(f"No valid entity types provided for {scan_type} service. Available types: {available_types}")
            
        return valid_types
    
    async def start_scan(self, scan_request: Dict[str, Any], scan_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new scan for specified service with separate API calls for each entity type.
        
        Args:
            scan_request: Scan configuration with scan_type and entity_types
            scan_type: Optional override for scan type (if not provided in request)
            
        Returns:
            Dict[str, Any]: Created scan details
        """
        # Use scan_type from request if not provided as parameter
        if scan_type is None:
            scan_type = scan_request.get("scan_type")
            
        if not scan_type:
            raise ValueError("scan_type must be specified")
            
        # Get entity_types from request
        entity_types = scan_request.get("entity_types", [])
        if not entity_types:
            raise ValueError("entity_types must be specified with at least one value")
            
        # Validate and filter entity types
        valid_entity_types = self._validate_entity_types(scan_type, entity_types)
        
        # Get organization ID
        organization_id = scan_request.get("organizationId")
        
        # Get auth and filters
        auth = scan_request.get("auth", {})
        filters = scan_request.get("filters", {})
        
        # Validate scan type and get connector
        try:
            connector = self._get_connector(scan_type)
            logger.debug(f"Using connector {connector.__class__.__name__} for scan type {scan_type}")
        except ValueError as e:
            raise ValueError(f"Invalid scan type: {scan_type}. {str(e)}")
        
        # Create scan in database
        scan, entity_results = await self.scan_repository.create(
            scan_type=scan_type,
            entity_types=valid_entity_types,  # Use validated entity types
            organization_id=organization_id,
            scan_config=scan_request
        )
        
        logger.info(f"Scan created with ID {scan.id}, with {len(entity_results)} entity results")
        
        try:
            # Update scan status to RUNNING
            scan = await self.scan_repository.update_status(scan.id, ScanStatus.RUNNING)
            
            logger.info(f"Starting {scan_type} scan with ID {scan.id} for entity types: {valid_entity_types}")
            
            # Start a scan for each entity type separately using the entity result IDs
            for entity_result in entity_results:
                # Create a config for this entity type in the format expected by the connector
                entity_scan_config = {
                    "config": {     
                        "scanId": entity_result.id,  # Use the entity result ID from the database
                        "organizationId": organization_id,
                        "type": [entity_result.entity_type],  # Only this entity type
                        "auth": auth,
                        "filters": filters
                    }
                }
                
                logger.info(f"Starting {scan_type} scan for entity type {entity_result.entity_type} with ID {entity_result.id}")
                logger.info(f"Entity scan config: {entity_scan_config}")

                try:
                    # Make the API call for this entity type using the appropriate connector
                    response = await connector.start_scan(entity_scan_config)
                    logger.info(f"Connector response for {entity_result.entity_type}: {response}")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Error starting scan for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                    continue
                
                # Update the entity result status
                entity_result.status = "processing"
                entity_result.start_time = datetime.utcnow()
                self.scan_repository.session.add(entity_result)
                
                try:
                    # Start polling for THIS entity result
                    await self.status_service.start_entity_polling(entity_result, scan_type)
                    logger.info(f"Started polling for entity result {entity_result.id}")
                except Exception as e:
                    logger.error(f"Error starting polling for entity result {entity_result.id}: {str(e)}", exc_info=True)
            
            # Commit the changes to entity results
            await self.scan_repository.session.commit()
            
            # Format the response
            return {
                "id": scan.id,
                "scan_type": scan.scan_type,
                "status": scan.status.value,
                "entity_types": scan.entity_types,
                "organization_id": scan.organization_id,
                "created_at": scan.created_at,
                "started_at": scan.started_at
            }
        except Exception as e:
            # Update scan status to FAILED in case of error
            await self.scan_repository.update_status(scan.id, ScanStatus.FAILED)
            logger.error(f"Failed to start {scan_type} scan: {str(e)}", exc_info=True)
            raise
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """
        Get the status of a scan with entity results.
        
        Args:
            scan_id: ID of the scan
            
        Returns:
            Dict[str, Any]: Scan status with entity results
        """
        # Get the scan
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found")
        
        # Get entity results
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Format entity results
        formatted_results = []
        for result in entity_results:
            formatted_results.append({
                "id": result.id,
                "entity_type": result.entity_type,
                "status": result.status,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "record_count": result.record_count,
                "success_count": result.success_count,
                "error_count": result.error_count,
                "warning_count": result.warning_count,
                "processing_time": result.processing_time
            })
        
        # Return combined response
        return {
            "id": scan.id,
            "scan_type": scan.scan_type,
            "status": scan.status.value,
            "entity_types": scan.entity_types,
            "organization_id": scan.organization_id,
            "created_at": scan.created_at,
            "started_at": scan.started_at,
            "completed_at": scan.completed_at,
            "entity_results": formatted_results
        }
        
    async def list_scans(self,
                         scan_type: Optional[str] = None,
                         scan_status: Optional[str] = None,
                         organization_id: Optional[str] = None,
                         page: int = 1,
                         limit: int = 20) -> Dict[str, Any]:
        """
        List scans with filtering and pagination.
        
        Args:
            scan_type: Filter by scan type (optional)
            scan_status: Filter by scan status (optional)
            organization_id: Filter by organization ID (optional)
            page: Page number for pagination
            limit: Items per page
            
        Returns:
            Dict[str, Any]: Paginated list of scans
        """
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Get filtered scans
        scans = await self.scan_repository.get_filtered(
            limit=limit,
            offset=offset,
            scan_type=scan_type,
            scan_status=scan_status,
            organization_id=organization_id
        )
        
        # Get total count for pagination
        total_count = await self.scan_repository.count_filtered(
            scan_type=scan_type,
            scan_status=scan_status,
            organization_id=organization_id
        )
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        # Format response
        items = []
        for scan in scans:
            items.append({
                "id": scan.id,
                "scan_type": scan.scan_type,
                "status": scan.status.value,
                "entity_types": scan.entity_types,
                "organization_id": scan.organization_id,
                "created_at": scan.created_at,
                "started_at": scan.started_at,
                "completed_at": scan.completed_at
            })
        
        return {
            "items": items,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": total_pages
        }

    async def cancel_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Cancel a running or paused scan.
        
        Args:
            scan_id: ID of the scan to cancel
            
        Returns:
            Dict[str, Any]: Updated scan details
        """
        # Get the scan
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found")
        
        # Check if scan is in a cancellable state
        if scan.status not in [ScanStatus.RUNNING, ScanStatus.PAUSED, ScanStatus.PENDING]:
            raise ValueError(f"Cannot cancel scan with status {scan.status.value}. Only running, paused, or pending scans can be cancelled.")
        
        # Get scan type and entity results
        scan_type = scan.scan_type
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        try:
            logger.info(f"Cancelling {scan_type} scan with ID {scan_id}")
            
            # Get the appropriate connector for this scan type
            connector = self._get_connector(scan_type)
            
            # Update scan status to CANCELLED
            scan = await self.scan_repository.update_status(scan.id, ScanStatus.CANCELLED)
            
            # Cancel all active entity results
            active_entities = [er for er in entity_results if er.status in ('processing', 'pending', 'paused')]
            for entity_result in active_entities:
                try:
                    # Make the API call to cancel the entity scan
                    logger.info(f"Cancelling {scan_type} scan for entity type {entity_result.entity_type} with ID {entity_result.id}")
                    await connector.cancel_scan(entity_result.id)
                    
                    # Update entity result status
                    await self.scan_repository.update_entity_result(
                        entity_result.id,
                        status="cancelled",
                        end_time=datetime.utcnow()
                    )
                except Exception as e:
                    logger.error(f"Error cancelling scan for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                    continue
            
            # Stop status polling if available
            if hasattr(self.status_service, 'stop_all_polling'):
                await self.status_service.stop_all_polling(scan_id)
            
            # Get updated scan status to return
            return await self.get_scan_status(scan_id)
        except Exception as e:
            logger.error(f"Failed to cancel {scan_type} scan: {str(e)}", exc_info=True)
            raise

    async def remove_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Remove a scan and its associated data.
        
        Args:
            scan_id: ID of the scan to remove
            
        Returns:
            Dict[str, Any]: Removal confirmation response
        """
        # Get the scan
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found")
        
        # Get scan type and entity results
        scan_type = scan.scan_type
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        entity_count = len(entity_results)
        
        try:
            logger.info(f"Removing {scan_type} scan with ID {scan_id}")
            
            # Get the appropriate connector for this scan type
            connector = self._get_connector(scan_type)
            
            # First cancel each entity scan if it's running
            for entity_result in entity_results:
                if entity_result.status in ('pending', 'processing', 'paused'):
                    try:
                        # Make the API call to cancel the entity scan
                        logger.info(f"Cancelling {scan_type} scan for entity type {entity_result.entity_type} with ID {entity_result.id}")
                        await connector.cancel_scan(entity_result.id)
                    except Exception as e:
                        logger.error(f"Error cancelling scan for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                        continue
                
                # Then remove the scan data
                try:
                    logger.info(f"Removing {scan_type} scan data for entity type {entity_result.entity_type} with ID {entity_result.id}")
                    await connector.remove_scan(entity_result.id)
                except Exception as e:
                    logger.error(f"Error removing scan data for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                    continue
            
            # Stop status polling
            if hasattr(self.status_service, 'stop_all_polling'):
                await self.status_service.stop_all_polling(scan_id)
            
            # Update scan status to CANCELLED
            await self.scan_repository.update_status(scan.id, ScanStatus.CANCELLED)
            
            # Delete the scan and its entity results from the database
            await self.scan_repository.delete_scan(scan_id)
            
            # Return removal confirmation
            return {
                "id": scan_id,
                "scan_type": scan_type,
                "status": "removed",
                "removed_at": datetime.utcnow().isoformat(),
                "entity_count": entity_count
            }
        except Exception as e:
            logger.error(f"Failed to remove {scan_type} scan: {str(e)}", exc_info=True)
            raise
    
    async def pause_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Pause a running scan.
        
        Args:
            scan_id: ID of the scan to pause
            
        Returns:
            Dict[str, Any]: Updated scan details
        """
        # Get the scan
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found")
        
        # Check if scan is in a pausable state
        if scan.status != ScanStatus.RUNNING:
            raise ValueError(f"Cannot pause scan with status {scan.status.value}. Only running scans can be paused.")
        
        # Get scan type and entity results
        scan_type = scan.scan_type
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        try:
            logger.info(f"Pausing {scan_type} scan with ID {scan_id}")
            
            # Get the appropriate connector for this scan type
            connector = self._get_connector(scan_type)
            
            # Update scan status to PAUSED
            scan = await self.scan_repository.update_status(scan.id, ScanStatus.PAUSED)
            
            # Update all entity results to 'paused' status for active ones
            processing_entities = [er for er in entity_results if er.status in ('processing', 'pending')]
            for entity_result in processing_entities:
                try:
                    # Make the API call to pause the entity scan
                    logger.info(f"Pausing {scan_type} scan for entity type {entity_result.entity_type} with ID {entity_result.id}")
                    await connector.pause_scan(entity_result.id)
                    
                    # Update entity result status
                    await self.scan_repository.update_entity_result(
                        entity_result.id,
                        status="paused"
                    )
                except Exception as e:
                    logger.error(f"Error pausing scan for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                    continue
            
            # Pause status polling if available
            if hasattr(self.status_service, 'pause_all_polling'):
                await self.status_service.pause_all_polling(scan_id)
            
            # Get updated scan status to return
            return await self.get_scan_status(scan_id)
        except Exception as e:
            # Try to restore the running state
            try:
                await self.scan_repository.update_status(scan.id, ScanStatus.RUNNING)
            except Exception:
                pass
                
            logger.error(f"Failed to pause {scan_type} scan: {str(e)}", exc_info=True)
            raise
    
    async def resume_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Resume a paused scan.
        
        Args:
            scan_id: ID of the scan to resume
            
        Returns:
            Dict[str, Any]: Updated scan details
        """
        # Get the scan
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found")
        
        # Check if scan is in a resumable state
        if scan.status != ScanStatus.PAUSED:
            raise ValueError(f"Cannot resume scan with status {scan.status.value}. Only paused scans can be resumed.")
        
        # Get scan type and entity results
        scan_type = scan.scan_type
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        try:
            logger.info(f"Resuming {scan_type} scan with ID {scan_id}")
            
            # Get the appropriate connector for this scan type
            connector = self._get_connector(scan_type)
            
            # Update scan status to RUNNING
            scan = await self.scan_repository.update_status(scan.id, ScanStatus.RUNNING)
            
            # Update all paused entity results to 'processing'
            paused_entities = [er for er in entity_results if er.status == 'paused']
            for entity_result in paused_entities:
                try:
                    # Make the API call to resume the entity scan
                    logger.info(f"Resuming {scan_type} scan for entity type {entity_result.entity_type} with ID {entity_result.id}")
                    await connector.resume_scan(entity_result.id)
                    
                    # Update entity result status
                    await self.scan_repository.update_entity_result(
                        entity_result.id,
                        status="processing"
                    )
                except Exception as e:
                    logger.error(f"Error resuming scan for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                    continue
            
            # Resume status polling if available
            if hasattr(self.status_service, 'resume_all_polling'):
                await self.status_service.resume_all_polling(scan_id)
            
            # Get updated scan status to return
            return await self.get_scan_status(scan_id)
        except Exception as e:
            # Try to restore the paused state
            try:
                await self.scan_repository.update_status(scan.id, ScanStatus.PAUSED)
            except Exception:
                pass
                
            logger.error(f"Failed to resume {scan_type} scan: {str(e)}", exc_info=True)
            raise

    async def stream_scan_data(self, 
                          scan_id: str, 
                          offset: int = 0, 
                          limit: int = 100) -> Dict[str, Any]:
        """
        Stream data from a completed scan with pagination.
        
        Args:
            scan_id: ID of the scan to stream data from
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dict[str, Any]: Stream response with data statistics
        """
        # Get the scan
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found")
        
        # Check if scan is in a completed or at least running state
        if scan.status not in [ScanStatus.COMPLETED, ScanStatus.RUNNING]:
            raise ValueError(f"Cannot stream data from scan with status {scan.status.value}. Scan must be completed or running.")
        
        # Get scan type and entity results
        scan_type = scan.scan_type
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Check if any entities are completed
        completed_entities = [er for er in entity_results if er.status == 'completed']
        if not completed_entities:
            raise ValueError(f"No completed entity results available for streaming in scan {scan_id}")
        
        try:
            logger.info(f"Streaming data for {scan_type} scan with ID {scan_id}")
            
            # Get the appropriate connector for this scan type
            connector = self._get_connector(scan_type)
            
            # Initialize counters for total records and batches
            total_count = 0
            total_batches = 0
            stream_results = []
            
            # Process each completed entity result separately
            for entity_result in completed_entities:
                try:
                    # Make the API call to stream data for this entity
                    logger.info(f"Streaming {scan_type} data for entity type {entity_result.entity_type} with ID {entity_result.id}")
                    
                    # Stream data for this specific entity result
                    response = await connector.stream_data(
                        entity_result.id,  # Use entity result ID
                        offset=offset,
                        limit=limit
                    )
                    
                    # Extract data from the response
                    if response and isinstance(response, dict) and 'data' in response:
                        entity_data = response['data']
                        # Accumulate counts
                        entity_count = entity_data.get('total_count', 0)
                        entity_batches = entity_data.get('total_batches', 0)
                        total_count += entity_count
                        total_batches += entity_batches
                        
                        # Store topic and entity_type
                        stream_results.append({
                            'topic': entity_data.get('topic', ''),
                            'entity_type': entity_result.entity_type,
                            'count': entity_count,
                            'batches': entity_batches
                        })
                        
                        logger.info(f"Streamed {entity_count} records in {entity_batches} batches for {entity_result.entity_type}")
                    
                except Exception as e:
                    logger.error(f"Error streaming data for entity type {entity_result.entity_type}: {str(e)}", exc_info=True)
                    continue
            
            # Compile the final response
            return {
                "success": True,
                "message": f"Streamed {total_count} {scan_type} records in {total_batches} batches",
                "data": {
                    "total_count": total_count,
                    "total_batches": total_batches,
                    "entity_results": stream_results,
                    "organization_id": scan.organization_id,
                    "scan_id": scan_id
                }
            }
        except Exception as e:
            logger.error(f"Failed to stream data for {scan_type} scan: {str(e)}", exc_info=True)
            raise