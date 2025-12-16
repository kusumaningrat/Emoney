import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config


def extract_permissions(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract Permission records from eMoney Identity API

    Yields permission records with normalized field names,
    with extraction metadata added.
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    PERMISSION_CHECKPOINT_FREQUENCY = config.PERMISSION_CHECKPOINT_FREQUENCY
    PERMISSION_PAUSE_CHECK_FREQUENCY = config.PERMISSION_PAUSE_CHECK_FREQUENCY
    PERMISSION_CANCEL_CHECK_FREQUENCY = config.PERMISSION_CANCEL_CHECK_FREQUENCY
    PERMISSION_MAX_BATCHES = config.PERMISSION_MAX_BATCHES
    
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Permissions for org: {organization_id}")
    logger.info("=" * 60)

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "permission"
    batch_counter = 0

    if resume_from and isinstance(resume_from, dict):
        entity_checkpoint = resume_from.get(entity)
        if entity_checkpoint:
            checkpoint_data = entity_checkpoint.get("checkpoint_data", {})
            
            if checkpoint_data and checkpoint_data.get("status") == "completed":
                logger.info(f"Entity '{entity}' was already completed in previous run")
                return
                
            if checkpoint_data and checkpoint_data.get("status") == "paused":
                logger.info(f"Resuming {entity} extraction from paused state")
                
            if checkpoint_data and "page" in checkpoint_data:
                page = checkpoint_data["page"]
                total_records = entity_checkpoint.get("records_processed", 0)
                batch_counter = checkpoint_data.get("batch_counter", 0)
                logger.info(f"Resuming {entity} extraction from page {page}")

    def save_checkpoint(status="in_progress"):
        if checkpoint_callback:
            try:
                checkpoint_data = {
                    "entity": entity,
                    "records_processed": total_records,
                    "checkpoint_data": {
                        "page": page, 
                        "status": status,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "batch_counter": batch_counter
                    },
                }
                checkpoint_callback(job_id, checkpoint_data)
                logger.info(f"Checkpoint saved: {total_records} {entity}")
            except Exception as e:
                logger.warning(f"Failed to save checkpoint: {e}")

    def should_check_cancelled():
        return batch_counter % PERMISSION_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % PERMISSION_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % PERMISSION_CHECKPOINT_FREQUENCY == 0

    permissions_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            time.sleep(test_batch_delay)
        
        if batch_counter > PERMISSION_MAX_BATCHES:
            logger.warning(f"Extraction reached maximum batch limit ({PERMISSION_MAX_BATCHES})")
            save_checkpoint(status="max_batches_reached")
            break
        
        if should_check_cancelled() and check_cancelled_callback and check_cancelled_callback():
            logger.info(f"Extraction cancelled at batch {batch_counter}")
            save_checkpoint(status="cancelled")
            break
            
        if should_check_paused() and check_paused_callback and check_paused_callback():
            logger.info(f"Extraction paused at batch {batch_counter}")
            save_checkpoint(status="paused")
            break
        
        try:
            logger.info(f"Fetching permissions (page: {page}, limit: {limit}) - batch {batch_counter}")

            response = api_service.get_permissions(page=page, limit=limit)

            if isinstance(response, dict):
                if "permissions" in response:
                    permissions = response.get("permissions", [])
                elif "Data" in response:
                    permissions = response.get("Data", [])
                else:
                    permissions = []
            else:
                permissions = response if isinstance(response, list) else []

            if not permissions:
                logger.info("No more permissions found")
                break

            batch_size = 0
            permissions_data = []
            
            for permission in permissions:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                try:
                    # Handle eMoney Permission format (flat JSON structure)
                    permission_record = {
                        "id": permission.get("PermissionID") or permission.get("permissionId") or permission.get("id"),
                        "name": permission.get("PermissionName") or permission.get("permissionName") or permission.get("name"),
                        "code": permission.get("PermissionCode") or permission.get("permissionCode") or permission.get("code"),
                        "description": permission.get("Description") or permission.get("description"),
                        "category": permission.get("Category") or permission.get("category"),
                        "resource": permission.get("Resource") or permission.get("resource"),
                        "action": permission.get("Action") or permission.get("action"),
                        "scope": permission.get("Scope") or permission.get("scope"),
                        "status": permission.get("Status") or permission.get("status"),
                        "is_system_permission": permission.get("IsSystemPermission") or permission.get("isSystemPermission"),
                        "created_date": permission.get("CreatedDate") or permission.get("createdDate"),
                        "modified_date": permission.get("ModifiedDate") or permission.get("modifiedDate"),
                    }

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        permission_record[meta_key] = meta_value

                    permissions_data.append(permission_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing permission record: {record_err}")
                    logger.error(f"Permission data: {permission}")
                    continue

            for permission_record in permissions_data:
                yield permission_record
                
            logger.info(f"Processed {batch_size} permissions (total: {total_records})")

            if should_save_checkpoint():
                save_checkpoint()

            if len(permissions) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting permissions at page {page}: {e}")
            save_checkpoint(status="error")
            for permission_record in permissions_data:
                yield permission_record
            raise

    logger.info(f"✓ Permissions extraction complete: {total_records} records")
    save_checkpoint(status="completed")