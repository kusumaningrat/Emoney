import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.db.repositories.scan_repository import ScanRepository
from app.db.models import ScanStatus, ScanEntityResult

logger = logging.getLogger(__name__)

class ScanStatusService:
    """Service for polling and updating EMoney scan statuses"""
    
    def __init__(self, scan_repository: ScanRepository):
        self.scan_repository = scan_repository
        self._init_connectors()
        self.polling_interval = 10  # seconds between polling
        self.active_polls = {}  # Track active polling tasks by entity result ID
    
    def _init_connectors(self):
        """Initialize connectors for different EMoney service types"""
        from app.connectors.emoney_account_connector import EMoneyAccountConnector
        from app.connectors.emoney_client_connector import EMoneyClientConnector
        from app.connectors.emoney_financial_planning_connector import EMoneyFinancialPlanningConnector
        from app.connectors.emoney_identity_connector import EMoneyIdentityConnector
        
        # Initialize all EMoney connectors
        self.connectors = {
            "account": EMoneyAccountConnector(),
            "client": EMoneyClientConnector(),
            "financial_planning": EMoneyFinancialPlanningConnector(),
            "identity": EMoneyIdentityConnector()
        }
    
    def _get_connector(self, scan_type: str):
        """Get the appropriate connector for the EMoney scan type"""
        connector = self.connectors.get(scan_type)
        if not connector:
            raise ValueError(f"No connector available for EMoney scan type: {scan_type}")
        return connector
    
    async def start_entity_polling(self, entity_result: ScanEntityResult, scan_type: str, max_duration: int = 3600):
        """
        Start polling for an individual EMoney entity result status
        
        Args:
            entity_result: ScanEntityResult to poll
            scan_type: Type of EMoney scan (account, client, financial_planning, identity)
            max_duration: Maximum polling duration in seconds (default: 1 hour)
        """
        entity_id = entity_result.id
        
        if entity_id in self.active_polls:
            logger.info(f"Polling already active for EMoney entity {entity_id}")
            return
            
        try:
            connector = self._get_connector(scan_type)
        except ValueError as e:
            logger.error(f"Cannot poll EMoney entity {entity_id}: {str(e)}")
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
        
        logger.info(f"Started polling for EMoney entity {entity_id}")
    
    def stop_entity_polling(self, entity_id: str):
        """
        Stop polling for a specific EMoney entity result
        
        Args:
            entity_id: ID of the entity result to stop polling
        """
        if entity_id in self.active_polls:
            self.active_polls[entity_id].cancel()
            logger.info(f"Stopped polling for EMoney entity {entity_id}")
    
    def _cleanup_polling_task(self, entity_id: str, task):
        """Remove task from active polls when complete"""
        if entity_id in self.active_polls:
            del self.active_polls[entity_id]
        
        # Handle any exceptions
        if task.cancelled():
            logger.info(f"Polling for EMoney entity {entity_id} was cancelled")
        elif task.exception():
            logger.error(f"Error polling EMoney entity {entity_id}: {task.exception()}")
    
    async def _poll_entity_status(self, entity_result: ScanEntityResult, connector: Any, max_duration: int):
        """
        Poll for EMoney entity status updates until complete or max duration reached
        
        Args:
            entity_result: ScanEntityResult to poll
            connector: EMoney service connector to use for API calls
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
                # Poll status from the EMoney API using the entity result's ID
                status_response = await connector.get_scan_status(entity_id)
                logger.debug(f"EMoney status response for entity {entity_id}: {status_response}")
                
                # Process response
                if "data" in status_response and status_response["data"] is not None:
                    api_data = status_response["data"]
                    
                    if "status" in api_data:
                        api_status = api_data["status"]
                        
                        # Map EMoney API status to our status
                        new_entity_status = api_status
                        
                        # Update entity result
                        update_data = {"status": new_entity_status}
                        
                        # Extract records processed from EMoney checkpoint data if available
                        if "checkpointInfo" in api_data and api_data["checkpointInfo"] is not None:
                            checkpoint_info = api_data["checkpointInfo"]
                            if "latestCheckpoint" in checkpoint_info and checkpoint_info["latestCheckpoint"] is not None:
                                latest_checkpoint = checkpoint_info["latestCheckpoint"]
                                if "recordsProcessed" in latest_checkpoint:
                                    records_processed = latest_checkpoint["recordsProcessed"]
                                    update_data["record_count"] = records_processed
                                    logger.info(f"Found {records_processed} EMoney records processed in checkpoint for entity {entity_id}")
                        
                        # If no checkpoint data, use recordsExtracted from EMoney api_data
                        if "record_count" not in update_data and "recordsExtracted" in api_data:
                            update_data["record_count"] = api_data["recordsExtracted"]
                        
                        # Extract EMoney-specific batch processing info
                        if "batchInfo" in api_data and api_data["batchInfo"] is not None:
                            batch_info = api_data["batchInfo"]
                            if "totalRecords" in batch_info:
                                update_data["record_count"] = batch_info["totalRecords"]
                            if "processedCount" in batch_info:
                                update_data["success_count"] = batch_info["processedCount"]
                            if "errorCount" in batch_info:
                                update_data["error_count"] = batch_info["errorCount"]
                                
                        # Calculate success/error counts if available from EMoney metadata
                        if "metadata" in api_data and api_data["metadata"] is not None:
                            metadata = api_data["metadata"]
                            if "extraction_summary" in metadata and metadata["extraction_summary"] is not None:
                                summary = metadata["extraction_summary"]
                                update_data["success_count"] = summary.get("success_count", 0)
                                update_data["error_count"] = summary.get("error_count", 0)
                                update_data["warning_count"] = summary.get("warning_count", 0)
                            
                            # Handle EMoney-specific JWT authentication status
                            if "auth_status" in metadata:
                                auth_status = metadata["auth_status"]
                                if auth_status.get("jwt_valid") is False:
                                    logger.warning(f"JWT token invalid for EMoney entity {entity_id}")
                                if auth_status.get("firm_access") is False:
                                    logger.warning(f"Firm access denied for EMoney entity {entity_id}")
                        
                        # Set timestamps
                        if api_status in ["completed", "failed", "cancelled"]:
                            current_time = datetime.utcnow()
                            update_data["end_time"] = current_time
                            
                            if "endTime" in api_data and api_data["endTime"]:
                                try:
                                    # Parse the EMoney API end time, ensuring it's timezone-aware
                                    api_end_time = datetime.fromisoformat(
                                        api_data["endTime"].replace("Z", "+00:00")
                                    )
                                    # Store as UTC time without timezone info
                                    update_data["end_time"] = api_end_time.replace(tzinfo=None)
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"Error parsing endTime for EMoney entity {entity_id}: {str(e)}")
                            
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
                                
                            # If duration is available directly from EMoney, use it
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
                            
                            logger.info(f"Updated status for EMoney entity {entity_id} to {new_entity_status}")
                            
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
                                logger.info(f"Updated EMoney scan {scan_id} status to {new_scan_status.value}")
                        
                        # If status is final, break out of loop
                        if api_status in ["completed", "failed", "cancelled"]:
                            logger.info(f"EMoney entity {entity_id} reached final status: {api_status}")
                            break
                    else:
                        logger.warning(f"Status field missing in EMoney API response for entity {entity_id}")
                else:
                    logger.warning(f"Invalid EMoney API response structure for entity {entity_id}")
                
            except Exception as e:
                logger.error(f"Error polling EMoney entity {entity_id}: {str(e)}", exc_info=True)
            
            # Sleep before polling again
            await asyncio.sleep(self.polling_interval)
        
        # Log if we hit the timeout
        if datetime.utcnow() >= end_time and entity_result.status not in ["completed", "failed", "cancelled"]:
            logger.warning(f"Polling timeout for EMoney entity {entity_id} after {max_duration} seconds")
    
    async def _update_parent_scan_status(self, scan_id: str):
        """Update parent EMoney scan status based on all its entity results"""
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
            logger.info(f"Updated EMoney scan {scan_id} status to {new_scan_status.value}")
            
    async def stop_all_polling(self, scan_id: str):
        """
        Stop polling for all entity results associated with an EMoney scan
        
        Args:
            scan_id: ID of the parent EMoney scan
        """
        # Get entity results for this scan
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Stop polling for each entity result
        for entity_result in entity_results:
            self.stop_entity_polling(entity_result.id)
            
        logger.info(f"Stopped all polling for EMoney scan {scan_id}")
    
    async def pause_all_polling(self, scan_id: str):
        """
        Pause polling for all entity results associated with an EMoney scan
        
        Args:
            scan_id: ID of the parent EMoney scan
        """
        # Get entity results for this scan
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Temporarily stop polling for each entity result
        for entity_result in entity_results:
            if entity_result.id in self.active_polls and entity_result.status == "processing":
                self.stop_entity_polling(entity_result.id)
                
        logger.info(f"Paused all polling for EMoney scan {scan_id}")
    
    async def resume_all_polling(self, scan_id: str):
        """
        Resume polling for all paused entity results associated with an EMoney scan
        
        Args:
            scan_id: ID of the parent EMoney scan
        """
        # Get entity results for this scan
        entity_results = await self.scan_repository.get_entity_results(scan_id)
        
        # Get scan type
        scan = await self.scan_repository.get_by_id(scan_id)
        if not scan:
            logger.error(f"Cannot resume polling: EMoney scan {scan_id} not found")
            return
            
        scan_type = scan.scan_type
        
        # Restart polling for each paused entity result
        for entity_result in entity_results:
            if entity_result.status == "processing" and entity_result.id not in self.active_polls:
                await self.start_entity_polling(entity_result, scan_type)
                
        logger.info(f"Resumed all polling for EMoney scan {scan_id}")
    
    async def get_polling_status(self) -> Dict[str, Any]:
        """
        Get current status of all active polling tasks for EMoney entities.
        
        Returns:
            Dict[str, Any]: Polling status information
        """
        active_count = len(self.active_polls)
        active_entities = list(self.active_polls.keys())
        
        return {
            "active_polls_count": active_count,
            "active_entity_ids": active_entities,
            "polling_interval": self.polling_interval
        }
    
    async def update_polling_interval(self, new_interval: int):
        """
        Update the polling interval for EMoney status checks.
        
        Args:
            new_interval: New polling interval in seconds
        """
        if new_interval < 5:
            logger.warning("Polling interval too short, setting minimum of 5 seconds")
            new_interval = 5
        elif new_interval > 300:
            logger.warning("Polling interval too long, setting maximum of 300 seconds")
            new_interval = 300
            
        old_interval = self.polling_interval
        self.polling_interval = new_interval
        
        logger.info(f"Updated EMoney polling interval from {old_interval}s to {new_interval}s")
    
    async def handle_emoney_auth_refresh(self, entity_id: str, new_jwt_token: str):
        """
        Handle JWT token refresh for an EMoney entity during polling.
        
        Args:
            entity_id: ID of the entity result
            new_jwt_token: New JWT token to use
        """
        # This method would be called if JWT token expires during polling
        # Implementation would depend on how JWT refresh is handled in the system
        logger.info(f"JWT token refreshed for EMoney entity {entity_id}")
        # Could update the connector's auth config or restart polling with new token