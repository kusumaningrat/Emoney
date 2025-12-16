import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config


def extract_roles(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract Role records from eMoney Identity API

    Yields role records with normalized field names,
    with extraction metadata added.
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    ROLE_CHECKPOINT_FREQUENCY = config.ROLE_CHECKPOINT_FREQUENCY
    ROLE_PAUSE_CHECK_FREQUENCY = config.ROLE_PAUSE_CHECK_FREQUENCY
    ROLE_CANCEL_CHECK_FREQUENCY = config.ROLE_CANCEL_CHECK_FREQUENCY
    ROLE_MAX_BATCHES = config.ROLE_MAX_BATCHES
    
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Roles for org: {organization_id}")
    logger.info("=" * 60)

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "role"
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
        return batch_counter % ROLE_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % ROLE_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % ROLE_CHECKPOINT_FREQUENCY == 0

    roles_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            time.sleep(test_batch_delay)
        
        if batch_counter > ROLE_MAX_BATCHES:
            logger.warning(f"Extraction reached maximum batch limit ({ROLE_MAX_BATCHES})")
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
            logger.info(f"Fetching roles (page: {page}, limit: {limit}) - batch {batch_counter}")

            response = api_service.get_roles(page=page, limit=limit)

            if isinstance(response, dict):
                if "roles" in response:
                    roles = response.get("roles", [])
                elif "Data" in response:
                    roles = response.get("Data", [])
                else:
                    roles = []
            else:
                roles = response if isinstance(response, list) else []

            if not roles:
                logger.info("No more roles found")
                break

            batch_size = 0
            roles_data = []
            
            for role in roles:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                try:
                    # Handle eMoney Role format (flat JSON structure)
                    role_record = {
                        "id": role.get("RoleID") or role.get("roleId") or role.get("id"),
                        "name": role.get("RoleName") or role.get("roleName") or role.get("name"),
                        "description": role.get("Description") or role.get("description"),
                        "role_type": role.get("RoleType") or role.get("roleType"),
                        "status": role.get("Status") or role.get("status"),
                        "is_system_role": role.get("IsSystemRole") or role.get("isSystemRole"),
                        "created_date": role.get("CreatedDate") or role.get("createdDate"),
                        "modified_date": role.get("ModifiedDate") or role.get("modifiedDate"),
                    }

                    # Handle permissions if present
                    if role.get("Permissions") or role.get("permissions"):
                        permissions = role.get("Permissions") or role.get("permissions")
                        if isinstance(permissions, list):
                            role_record["permissions"] = json.dumps(permissions)
                        elif isinstance(permissions, str):
                            role_record["permissions"] = permissions

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        role_record[meta_key] = meta_value

                    roles_data.append(role_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing role record: {record_err}")
                    logger.error(f"Role data: {role}")
                    continue

            for role_record in roles_data:
                yield role_record
                
            logger.info(f"Processed {batch_size} roles (total: {total_records})")

            if should_save_checkpoint():
                save_checkpoint()

            if len(roles) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting roles at page {page}: {e}")
            save_checkpoint(status="error")
            for role_record in roles_data:
                yield role_record
            raise

    logger.info(f"✓ Roles extraction complete: {total_records} records")
    save_checkpoint(status="completed")