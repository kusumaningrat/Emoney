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
        from app.connectors.account_connector import EMoneyAccountConnector
        from app.connectors.financial_planning_connector import EMoneyFinancialPlanningConnector
        from app.connectors.identity_connector import EMoneyIdentityConnector
        from app.connectors.auth_connector import AuthConnector
        
        # Initialize all EMoney connectors
        self.connectors = {
            "account": EMoneyAccountConnector(),
            "financial_planning": EMoneyFinancialPlanningConnector(),
            "identity": EMoneyIdentityConnector(),
            "auth": AuthConnector()
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
            scan_type: Type of EMoney scan (account, financial_planning, identity, auth)
            max_duration: Maximum polling duration in seconds (default 1 hour)
        """
        entity_id = entity_result.id
        scan_id = entity_result.scan_id
        
        if entity_id in self.active_polls:
            logger.warning(f"Polling already active for entity result {entity_id}")
            return
        
        logger.info(f"Starting polling for EMoney {scan_type} entity result {entity_id} (type: {entity_result.entity_type})")
        
        # Create polling task
        task = asyncio.create_task(
            self._poll_entity_status(entity_result, scan_type, max_duration)
        )
        self.active_polls[entity_id] = task
        
        logger.info(f"Started polling for EMoney entity {entity_id}")
        
        # Don't await here - let it run in background
        return task
    
    async def _poll_entity_status(self, entity_result: ScanEntityResult, scan_type: str, max_duration: int):
        """
        Poll the status of a single EMoney entity result until completion or timeout
        
        Args:
            entity_result: ScanEntityResult to poll
            scan_type: Type of EMoney scan
            max_duration: Maximum polling duration in seconds
        """
        entity_id = entity_result.id
        scan_id = entity_result.scan_id
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=max_duration)
        
        logger.info(f"Starting poll loop for entity {entity_id}")
        
        try:
            connector = self._get_connector(scan_type)
            poll_count = 0
            
            while datetime.utcnow() < end_time:
                poll_count += 1
                
                try:
                    # Check current status from EMoney API
                    status_response = await connector.get_scan_status(entity_id)
                    
                    if status_response and isinstance(status_response, dict):
                        # Get status from nested 'data' object
                        api_status = status_response.get('data', {}).get('status', '').lower()
                        
                        logger.info(f"Entity {entity_id} API status: '{api_status}'")
                        
                        # Map EMoney API status to our internal status
                        if api_status in ['completed', 'done', 'finished', 'success', 'complete']:
                            logger.info(f"Entity {entity_id} completed with status '{api_status}'")
                            # Entity completed successfully
                            await self._handle_entity_completion(entity_result, status_response)
                            break
                        elif api_status in ['failed', 'error', 'failure']:
                            logger.error(f"Entity {entity_id} failed with status '{api_status}'")
                            # Entity failed
                            await self._handle_entity_failure(entity_result, status_response)
                            break
                        elif api_status in ['cancelled', 'canceled']:
                            logger.info(f"Entity {entity_id} cancelled with status '{api_status}'")
                            # Entity was cancelled
                            await self._handle_entity_cancellation(entity_result)
                            break
                        else:
                            # Still running, continue polling
                            logger.debug(f"EMoney entity result {entity_id} still {api_status}")
                    else:
                        logger.warning(f"Invalid response for entity {entity_id}: {status_response}")
                    
                    # Wait before next poll
                    await asyncio.sleep(self.polling_interval)
                    
                except Exception as e:
                    logger.error(f"Error polling EMoney entity result {entity_id}: {str(e)}")
                    await asyncio.sleep(self.polling_interval)
            
            else:
                # Timeout reached
                logger.warning(f"Polling timeout reached for EMoney entity result {entity_id}")
                await self._handle_entity_timeout(entity_result)
        
        except Exception as e:
            logger.error(f"Critical error in polling for EMoney entity result {entity_id}: {str(e)}", exc_info=True)
        
        finally:
            # Clean up polling task
            if entity_id in self.active_polls:
                del self.active_polls[entity_id]
            
            # Check if parent scan should be completed
            await self._check_scan_completion(scan_id)
    
    async def _handle_entity_completion(self, entity_result: ScanEntityResult, status_response: Dict[str, Any]):
        """Handle successful completion of an entity result"""
        entity_id = entity_result.id
        
        # Extract metrics from the nested 'data' object
        data = status_response.get('data', {})
        record_count = data.get('recordsExtracted', 0)
        
        # Try to get from checkpoint info if recordsExtracted is not available
        if record_count == 0 and 'checkpointInfo' in data:
            checkpoint_info = data.get('checkpointInfo', {})
            latest_checkpoint = checkpoint_info.get('latestCheckpoint', {})
            record_count = latest_checkpoint.get('recordsProcessed', 0)
        
        # Try to get from metadata if still no records found
        if record_count == 0 and 'metadata' in data:
            metadata = data.get('metadata', {})
            extraction_summary = metadata.get('extraction_summary', {})
            record_count = extraction_summary.get('total_records', 0)
        
        success_count = record_count  # Assuming all extracted records are successful
        error_count = 0  # EMoney API doesn't seem to provide this separately
        warning_count = 0
        
        # Calculate processing time
        processing_time = None
        if entity_result.start_time:
            processing_time = (datetime.utcnow() - entity_result.start_time).total_seconds()
        
        # Try to get duration from API response if available
        if 'duration' in data and data['duration'] is not None:
            processing_time = data['duration']
        
        # Update entity result
        await self.scan_repository.update_entity_result(
            entity_id,
            status="completed",
            end_time=datetime.utcnow(),
            record_count=record_count,
            success_count=success_count,
            error_count=error_count,
            warning_count=warning_count,
            processing_time=processing_time
        )
        
        logger.info(f"EMoney entity result {entity_id} completed with {record_count} records")
    
    async def _handle_entity_failure(self, entity_result: ScanEntityResult, status_response: Dict[str, Any]):
        """Handle failure of an entity result"""
        entity_id = entity_result.id
        
        # Extract error information
        error_message = status_response.get('error_message', 'Unknown error')
        error_count = status_response.get('error_count', 1)
        
        # Calculate processing time
        processing_time = None
        if entity_result.start_time:
            processing_time = (datetime.utcnow() - entity_result.start_time).total_seconds()
        
        # Update entity result
        await self.scan_repository.update_entity_result(
            entity_id,
            status="failed",
            end_time=datetime.utcnow(),
            error_count=error_count,
            processing_time=processing_time
        )
        
        logger.error(f"EMoney entity result {entity_id} failed: {error_message}")
    
    async def _handle_entity_cancellation(self, entity_result: ScanEntityResult):
        """Handle cancellation of an entity result"""
        entity_id = entity_result.id
        
        # Calculate processing time
        processing_time = None
        if entity_result.start_time:
            processing_time = (datetime.utcnow() - entity_result.start_time).total_seconds()
        
        # Update entity result
        await self.scan_repository.update_entity_result(
            entity_id,
            status="cancelled",
            end_time=datetime.utcnow(),
            processing_time=processing_time
        )
        
        logger.info(f"EMoney entity result {entity_id} was cancelled")
    
    async def _handle_entity_timeout(self, entity_result: ScanEntityResult):
        """Handle timeout of an entity result"""
        entity_id = entity_result.id
        
        # Calculate processing time
        processing_time = None
        if entity_result.start_time:
            processing_time = (datetime.utcnow() - entity_result.start_time).total_seconds()
        
        # Update entity result
        await self.scan_repository.update_entity_result(
            entity_id,
            status="timeout",
            end_time=datetime.utcnow(),
            processing_time=processing_time
        )
        
        logger.warning(f"EMoney entity result {entity_id} timed out")
    
    async def _check_scan_completion(self, scan_id: str):
        """
        Check if all entity results for a scan are complete and update parent scan status
        """
        try:
            logger.info(f"Checking completion for scan {scan_id}")
            
            # Get the parent scan
            scan = await self.scan_repository.get_by_id(scan_id)
            if not scan:
                logger.warning(f"Scan {scan_id} not found during completion check")
                return
            
            # Skip if scan is already in a final state
            if scan.status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]:
                logger.debug(f"Scan {scan_id} already in final state: {scan.status.value}")
                return
            
            # Get all entity results for this scan
            entity_results = await self.scan_repository.get_entity_results(scan_id)
            if not entity_results:
                logger.warning(f"No entity results found for scan {scan_id}")
                return
            
            # Check the status of all entity results
            completed_count = 0
            failed_count = 0
            cancelled_count = 0
            timeout_count = 0
            running_count = 0
            
            for entity_result in entity_results:
                status = entity_result.status
                
                if status == "completed":
                    completed_count += 1
                elif status in ["failed", "error"]:
                    failed_count += 1
                elif status in ["cancelled", "canceled"]:
                    cancelled_count += 1
                elif status == "timeout":
                    timeout_count += 1
                else:
                    running_count += 1
            
            total_entities = len(entity_results)
            
            logger.info(f"Scan {scan_id} completion check: {completed_count}/{total_entities} completed, "
                       f"{failed_count} failed, {cancelled_count} cancelled, {timeout_count} timeout, "
                       f"{running_count} still running")
            
            # Determine final scan status
            if running_count == 0:  # All entities are in final states
                if completed_count == total_entities:
                    # All entities completed successfully
                    await self.scan_repository.update_status(scan_id, ScanStatus.COMPLETED)
                    logger.info(f"Scan {scan_id} marked as COMPLETED - all {total_entities} entities finished successfully")
                
                elif failed_count > 0 or timeout_count > 0:
                    # Some entities failed or timed out
                    await self.scan_repository.update_status(scan_id, ScanStatus.FAILED)
                    logger.warning(f"Scan {scan_id} marked as FAILED - {failed_count} failed, {timeout_count} timeout")
                
                elif cancelled_count == total_entities:
                    # All entities were cancelled
                    await self.scan_repository.update_status(scan_id, ScanStatus.CANCELLED)
                    logger.info(f"Scan {scan_id} marked as CANCELLED - all entities cancelled")
                
                else:
                    # Mixed final states - mark as completed with warnings
                    await self.scan_repository.update_status(scan_id, ScanStatus.COMPLETED)
                    logger.warning(f"Scan {scan_id} marked as COMPLETED with mixed results: "
                                  f"{completed_count} completed, {failed_count} failed, "
                                  f"{cancelled_count} cancelled, {timeout_count} timeout")
            
            else:
                logger.debug(f"Scan {scan_id} still has {running_count} entities running, keeping status as running")
        
        except Exception as e:
            logger.error(f"Error checking completion for scan {scan_id}: {str(e)}", exc_info=True)
    
    async def stop_all_polling(self, scan_id: str):
        """Stop all active polling tasks for a scan"""
        try:
            entity_results = await self.scan_repository.get_entity_results(scan_id)
            stopped_count = 0
            
            for entity_result in entity_results:
                entity_id = entity_result.id
                if entity_id in self.active_polls:
                    task = self.active_polls[entity_id]
                    task.cancel()
                    del self.active_polls[entity_id]
                    stopped_count += 1
                    logger.info(f"Stopped polling for entity result {entity_id}")
            
            logger.info(f"Stopped {stopped_count} polling tasks for scan {scan_id}")
        
        except Exception as e:
            logger.error(f"Error stopping polling for scan {scan_id}: {str(e)}", exc_info=True)
    
    async def pause_all_polling(self, scan_id: str):
        """Pause all active polling tasks for a scan"""
        try:
            entity_results = await self.scan_repository.get_entity_results(scan_id)
            paused_count = 0
            
            for entity_result in entity_results:
                entity_id = entity_result.id
                if entity_id in self.active_polls:
                    # For now, we just stop the polling task when paused
                    # In a more sophisticated implementation, we might store
                    # the task state and resume it later
                    task = self.active_polls[entity_id]
                    task.cancel()
                    del self.active_polls[entity_id]
                    paused_count += 1
                    logger.info(f"Paused polling for entity result {entity_id}")
            
            logger.info(f"Paused {paused_count} polling tasks for scan {scan_id}")
        
        except Exception as e:
            logger.error(f"Error pausing polling for scan {scan_id}: {str(e)}", exc_info=True)
    
    async def resume_all_polling(self, scan_id: str):
        """Resume all paused polling tasks for a scan"""
        try:
            # Get entity results that are in 'paused' or 'processing' state
            entity_results = await self.scan_repository.get_entity_results(scan_id)
            resumed_count = 0
            
            # Get the scan to determine scan_type
            scan = await self.scan_repository.get_by_id(scan_id)
            if not scan:
                logger.error(f"Scan {scan_id} not found for resume polling")
                return
            
            scan_type = scan.scan_type
            logger.info(f"Resuming polling for scan {scan_id} (type: {scan_type})")
            
            for entity_result in entity_results:
                if entity_result.status in ['paused', 'processing']:
                    # Restart polling for this entity
                    await self.start_entity_polling(entity_result, scan_type)
                    resumed_count += 1
                    logger.info(f"Resumed polling for entity result {entity_result.id}")
            
            logger.info(f"Resumed {resumed_count} polling tasks for scan {scan_id}")
        
        except Exception as e:
            logger.error(f"Error resuming polling for scan {scan_id}: {str(e)}", exc_info=True)
    
    async def get_polling_status(self) -> Dict[str, Any]:
        """Get status of all active polling tasks"""
        active_entity_ids = list(self.active_polls.keys())
        
        # Get additional info about active polls if possible
        poll_info = []
        for entity_id in active_entity_ids:
            try:
                task = self.active_polls[entity_id]
                poll_info.append({
                    "entity_id": entity_id,
                    "task_done": task.done(),
                    "task_cancelled": task.cancelled()
                })
            except Exception:
                poll_info.append({
                    "entity_id": entity_id,
                    "task_done": None,
                    "task_cancelled": None
                })
        
        return {
            "active_polls": active_entity_ids,
            "count": len(active_entity_ids),
            "poll_details": poll_info,
            "polling_interval": self.polling_interval
        }
    
    async def force_completion_check(self, scan_id: str) -> Dict[str, Any]:
        """
        Force a completion check for a specific scan
        Useful for debugging stuck scans
        """
        try:
            logger.info(f"Force checking completion for scan {scan_id}")
            await self._check_scan_completion(scan_id)
            
            # Get updated scan status
            scan = await self.scan_repository.get_by_id(scan_id)
            if scan:
                return {
                    "scan_id": scan_id,
                    "status": scan.status.value,
                    "message": f"Completion check completed for scan {scan_id}"
                }
            else:
                return {
                    "scan_id": scan_id,
                    "status": "not_found",
                    "message": f"Scan {scan_id} not found"
                }
        
        except Exception as e:
            logger.error(f"Error in force completion check for scan {scan_id}: {str(e)}", exc_info=True)
            return {
                "scan_id": scan_id,
                "status": "error",
                "message": f"Error checking completion: {str(e)}"
            }
    
    async def cleanup_completed_polls(self):
        """Clean up completed or cancelled polling tasks"""
        cleanup_count = 0
        entity_ids_to_remove = []
        
        for entity_id, task in self.active_polls.items():
            if task.done() or task.cancelled():
                entity_ids_to_remove.append(entity_id)
        
        for entity_id in entity_ids_to_remove:
            del self.active_polls[entity_id]
            cleanup_count += 1
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} completed polling tasks")
        
        return cleanup_count