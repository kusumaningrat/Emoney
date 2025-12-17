import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.db.repositories.scan_repository import ScanRepository
from app.db.models import ScanStatus, ScanEntityResult

logger = logging.getLogger(__name__)

class ScanStatusService:
    """Service for polling and updating scan statuses"""
    
    def __init__(self, scan_repository: ScanRepository):
        self.scan_repository = scan_repository
        self._init_connectors()
        self.polling_interval = 10  # seconds between polling
        self.active_polls = {}  # Track active polling tasks by entity result ID
    
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
    
    async def start_entity_polling(self, entity_result: ScanEntityResult, scan_type: str, max_duration: int = 3600):
        """
        Start polling for an individual entity result status
        
        Args:
            entity_result: ScanEntityResult to poll
            scan_type: Type of scan (client, opportunity, identity, activity, auth)
            max_duration: Maximum polling duration in seconds (default: 1 hour)
        """
        entity_id = entity_result.id
        
        if entity_id in self.active_polls:
            logger.info(f"Polling already active for entity {entity_id}")
            return
            
        try:
            connector = self._get_connector(scan_type)
        except ValueError as e:
            logger.error(f"Cannot poll entity {entity_id}: {str(e)}")
            return
            
        # Create polling task
        task = asyncio.create_task(
            self._poll_entity_status(
                entity_result=entity_result,
                connector=connector,
                max_duration=max_duration
            )
        )
        
        self.active_polls[entity_id] = task
        
        # Setup cleanup when done
        task.add_done_callback(lambda t: self._cleanup_polling_task(entity_id, t))
        
        logger.info(f"Started polling for entity {entity_id}")
    
    def stop_entity_polling(self, entity_id: str):
        """
        Stop polling for a specific entity result
        
        Args:
            entity_id: ID of the entity result to stop polling
        """
        if entity_id in self.active_polls:
            self.active_polls[entity_id].cancel()
            logger.info(f"Stopped polling for entity {entity_id}")
    
    def _cleanup_polling_task(self, entity_id: str, task):
        """Remove task from active polls when complete"""
        if entity_id in self.active_polls:
            del self.active_polls[entity_id]
        
        # Handle any exceptions
        if task.cancelled():
            logger.info(f"Polling for entity {entity_id} was cancelled")
        elif task.exception():
            logger.error(f"Error polling entity {entity_id}: {task.exception()}")
    
    async def _poll_entity_status(self, entity_result: ScanEntityResult, connector: Any, max_duration: int):
        """
        Poll for entity status updates until complete or max duration reached
        
        Args:
            entity_result: ScanEntityResult to poll
            connector: Service connector to use for API calls
            max_duration: Maximum polling duration in seconds
        """
        from app.db.database import AsyncSessionFactory  # Import at function level
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=max_duration)
        
        entity_id = entity_result.id
        scan_id = entity_result.scan_id
        entity_type = entity_result.entity_type
        
        # Continue polling until status is final or timeout reached
        while entity_result.status not in ["completed", "failed", "cancelled"] and datetime.utcnow() < end_time:
            try:
                # Poll status from the API using the entity result's ID
                status_response = await connector.get_scan_status(entity_id)
                logger.debug(f"Status response for entity {entity_id}: {status_response}")
                
                # Process response
                if "data" in status_response and status_response["data"] is not None:
                    api_data = status_response["data"]
                    
                    if "status" in api_data:
                        api_status = api_data["status"]
                        
                        # Map API status to our status
                        new_entity_status = api_status
                        
                        # Update entity result
                        update_data = {"status": new_entity_status}
                        
                        # Extract records processed from checkpoint data if available
                        if "checkpointInfo" in api_data and api_data["checkpointInfo"] is not None:
                            checkpoint_info = api_data["checkpointInfo"]
                            if "latestCheckpoint" in checkpoint_info and checkpoint_info["latestCheckpoint"] is not None:
                                latest_checkpoint = checkpoint_info["latestCheckpoint"]
                                if "recordsProcessed" in latest_checkpoint:
                                    records_processed = latest_checkpoint["recordsProcessed"]
                                    update_data["record_count"] = records_processed
                                    logger.info(f"Found {records_processed} records processed in checkpoint for entity {entity_id}")
                        
                        # If no checkpoint data, use recordsExtracted from api_data
                        if "record_count" not in update_data and "recordsExtracted" in api_data:
                            update_data["record_count"] = api_data["recordsExtracted"]
                            
                        # Calculate success/error counts if available
                        if "metadata" in api_data and api_data["metadata"] is not None:
                            metadata = api_data["metadata"]
                            if "extraction_summary" in metadata and metadata["extraction_summary"] is not None:
                                summary = metadata["extraction_summary"]
                                update_data["success_count"] = summary.get("success_count", 0)
                                update_data["error_count"] = summary.get("error_count", 0)
                                update_data["warning_count"] = summary.get("warning_count", 0)
                        
                        # Set timestamps
                        if api_status in ["completed", "failed", "cancelled"]:
                            current_time = datetime.utcnow()
                            update_data["end_time"] = current_time
                            
                            if "endTime" in api_data and api_data["endTime"]:
                                try:
                                    # Parse the API end time, ensuring it's timezone-aware
                                    api_end_time = datetime.fromisoformat(
                                        api_data["endTime"].replace("Z", "+00:00")
                                    )
                                    # Store as UTC time without timezone info
                                    update_data["end_time"] = api_end_time.replace(tzinfo=None)
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Error parsing endTime for entity {entity_id}: {str(e)}")
                            
                            # Calculate processing time - ensure both times are timezone-naive
                            if entity_result.start_time and update_data.get("end_time"):
                                # Convert start_time to timezone-naive if it's timezone-aware
                                start_time_naive = entity_result.start_time
                                if hasattr(start_time_naive, 'tzinfo') and start_time_naive.tzinfo:
                                    start_time_naive = start_time_naive.replace(tzinfo=None)
                                    
                                # Convert end_time to timezone-naive if it's timezone-aware
                                end_time_naive = update_data["end_time"]
                                if hasattr(end_time_naive, 'tzinfo') and end_time_naive.tzinfo:
                                    end_time_naive = end_time_naive.replace(tzinfo=None)
                                
                                update_data["processing_time"] = (end_time_naive - start_time_naive).total_seconds()
                                
                            # If duration is available directly, use it
                            if "duration" in api_data and api_data["duration"] is not None:
                                update_data["processing_time"] = api_data["duration"]
                        
                        # Create a new session for database updates
                        async with AsyncSessionFactory() as session:
                            from app.db.repositories.scan_repository import ScanRepository
                            repo = ScanRepository(session)
                            
                            # Update entity result in database
                            updated_entity = await repo.update_entity_result(
                                entity_id=entity_id,
                                **update_data
                            )
                            
                            # Update entity_result local object for loop condition
                            for key, value in update_data.items():
                                setattr(entity_result, key, value)
                            
                            logger.info(f"Updated status for entity {entity_id} to {new_entity_status}")
                            
                            # Update parent scan status with a separate query in the same session
                            entity_results = await repo.get_entity_results(scan_id)
                            
                            # Count statuses
                            entity_status_counts = {}
                            for result in entity_results:
                                entity_status_counts[result.status] = entity_status_counts.get(result.status, 0) + 1
                                
                            total_entities = len(entity_results)
                            
                            # Determine overall status
                            new_scan_status = None
                            
                            if entity_status_counts.get("failed", 0) > 0:
                                new_scan_status = ScanStatus.FAILED
                            elif entity_status_counts.get("completed", 0) == total_entities:
                                new_scan_status = ScanStatus.COMPLETED
                            elif entity_status_counts.get("processing", 0) > 0:
                                new_scan_status = ScanStatus.RUNNING
                            elif entity_status_counts.get("cancelled", 0) > 0 and entity_status_counts.get("processing", 0) == 0:
                                new_scan_status = ScanStatus.CANCELLED
                            elif entity_status_counts.get("paused", 0) > 0 and entity_status_counts.get("processing", 0) == 0:
                                new_scan_status = ScanStatus.PAUSED
                                    
                            # Update scan status if needed
                            if new_scan_status:
                                await repo.update_status(scan_id, new_scan_status)
                                logger.info(f"Updated scan {scan_id} status to {new_scan_status.value}")
                        
                        # If status is final, break out of loop
                        if api_status in ["completed", "failed", "cancelled"]:
                            logger.info(f"Entity {entity_id} reached final status: {api_status}")
                            break
                    else:
                        logger.warning(f"Status field missing in API response for entity {entity_id}")
                else:
                    logger.warning(f"Invalid API response structure for entity {entity_id}")
                
            except Exception as e:
                logger.error(f"Error polling entity {entity_id}: {str(e)}", exc_info=True)
            
            # Sleep before polling again
            await asyncio.sleep(self.polling_interval)
        
        # Log if we hit the timeout
        if datetime.utcnow() >= end_time and entity_result.status not in ["completed", "failed", "cancelled"]:
            logger.warning(f"Polling timeout for entity {entity_id} after {max_duration} seconds")
    
    async def _update_parent_scan_status(self, scan_id: str):
        """Update parent scan status based on all its entity results"""
        # Get entity results
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Count statuses
        entity_status_counts = {}
        for result in entity_results:
            entity_status_counts[result.status] = entity_status_counts.get(result.status, 0) + 1
            
        total_entities = len(entity_results)
        
        # Determine overall status
        new_scan_status = None
        
        if entity_status_counts.get("failed", 0) > 0:
            # If any entity failed, mark scan as failed
            new_scan_status = ScanStatus.FAILED
        elif entity_status_counts.get("completed", 0) == total_entities:
            # If all entities completed, mark scan as completed
            new_scan_status = ScanStatus.COMPLETED
        elif entity_status_counts.get("cancelled", 0) > 0:
            # If any entity was cancelled and none are processing, mark scan as cancelled
            if entity_status_counts.get("processing", 0) == 0:
                new_scan_status = ScanStatus.CANCELLED
        elif entity_status_counts.get("processing", 0) > 0:
            # If any entity is processing, mark scan as running
            new_scan_status = ScanStatus.RUNNING
        elif entity_status_counts.get("paused", 0) > 0:
            # If any entity is paused and none are processing, mark scan as paused
            if entity_status_counts.get("processing", 0) == 0:
                new_scan_status = ScanStatus.PAUSED
            
        # Update scan status if needed
        if new_scan_status:
            await self.scan_repository.update_status(scan_id, new_scan_status)
            logger.info(f"Updated scan {scan_id} status to {new_scan_status.value}")
            
    async def stop_all_polling(self, scan_id: str):
        """
        Stop polling for all entity results associated with a scan
        
        Args:
            scan_id: ID of the parent scan
        """
        # Get entity results for this scan
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Stop polling for each entity result
        for entity_result in entity_results:
            self.stop_entity_polling(entity_result.id)
            
        logger.info(f"Stopped all polling for scan {scan_id}")
    
    async def pause_all_polling(self, scan_id: str):
        """
        Pause polling for all entity results associated with a scan
        
        Args:
            scan_id: ID of the parent scan
        """
        # Get entity results for this scan
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Temporarily stop polling for each entity result
        for entity_result in entity_results:
            if entity_result.id in self.active_polls and entity_result.status == "processing":
                self.stop_entity_polling(entity_result.id)
                
        logger.info(f"Paused all polling for scan {scan_id}")
    
    async def resume_all_polling(self, scan_id: str):
        """
        Resume polling for all paused entity results associated with a scan
        
        Args:
            scan_id: ID of the parent scan
        """
        # Get entity results for this scan
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Get scan type
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            logger.error(f"Cannot resume polling: Scan {scan_id} not found")
            return
            
        scan_type = scan.scan_type
        
        # Restart polling for each paused entity result
        for entity_result in entity_results:
            if entity_result.status == "processing" and entity_result.id not in self.active_polls:
                await self.start_entity_polling(entity_result, scan_type)
                
        logger.info(f"Resumed all polling for scan {scan_id}")