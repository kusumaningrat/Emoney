import logging
import time
from typing import Dict, Any, Iterator, Optional
from datetime import datetime, timezone
from config import get_config


def extract_sharingrules(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract SharingRule records from eMoney Service API

    Yields sharingrule records with lowercase underscore field names for PostgreSQL,
    with extraction metadata added.

    Args:
        api_service: API service client instance
        extraction_metadata: Metadata to attach to all records
        checkpoint_callback: Function to call for saving extraction progress
        filters: Extraction filters and configuration
        resume_from: Resume state from previous extraction checkpoint
        check_cancelled_callback: Function to check if job was cancelled
        check_paused_callback: Function to check if job was paused
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    SHARINGRULE_CHECKPOINT_FREQUENCY = config.SHARINGRULE_CHECKPOINT_FREQUENCY
    SHARINGRULE_PAUSE_CHECK_FREQUENCY = config.SHARINGRULE_PAUSE_CHECK_FREQUENCY
    SHARINGRULE_CANCEL_CHECK_FREQUENCY = config.SHARINGRULE_CANCEL_CHECK_FREQUENCY
    SHARINGRULE_MAX_BATCHES = config.SHARINGRULE_MAX_BATCHES
    
    # Check if we're in test mode and get test delay settings
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting SharingRules for org: {organization_id}")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"Running in TEST MODE with batch delay={test_batch_delay}s, record delay={test_record_delay}s")

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "sharingrule"
    batch_counter = 0

    # Check if resuming from a previous state
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
                logger.info(f"Resuming {entity} extraction from page {page} (batch {batch_counter})")

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
                logger.info(f"Checkpoint saved: {total_records} {entity} with status '{status}' at batch {batch_counter}")
            except Exception as e:
                logger.warning(f"Failed to save checkpoint: {e}")

    def should_check_cancelled():
        return batch_counter % SHARINGRULE_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % SHARINGRULE_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % SHARINGRULE_CHECKPOINT_FREQUENCY == 0

    sharingrules_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > SHARINGRULE_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({SHARINGRULE_MAX_BATCHES})")
            save_checkpoint(status="max_batches_reached")
            break
        
        if should_check_cancelled() and check_cancelled_callback and check_cancelled_callback():
            logger.info(f"Extraction of {entity} cancelled by user at batch {batch_counter}")
            save_checkpoint(status="cancelled")
            break
            
        if should_check_paused() and check_paused_callback and check_paused_callback():
            logger.info(f"Extraction of {entity} paused by user at batch {batch_counter}")
            save_checkpoint(status="paused")
            break
        
        try:
            logger.info(f"Fetching sharingrules (page: {page}, limit: {limit}) - batch {batch_counter}/{SHARINGRULE_MAX_BATCHES}...")

            response = api_service.get_sharingrules(page=page, page_size=limit)

            # Handle different response formats
            if isinstance(response, dict):
                if "sharingrules" in response:
                    sharingrules = response.get("sharingrules", [])
                elif "sharingRules" in response:  # Handle camelCase variant
                    sharingrules = response.get("sharingRules", [])
                elif "Data" in response:
                    sharingrules = response.get("Data", [])
                else:
                    sharingrules = []
            else:
                sharingrules = response if isinstance(response, list) else []

            if not sharingrules:
                logger.info("No more sharingrules found")
                break

            batch_size = 0
            sharingrules_data = []
            
            for rule in sharingrules:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for sharingrule_record in sharingrules_data:
                            yield sharingrule_record
                        return
                    
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for sharingrule_record in sharingrules_data:
                            yield sharingrule_record
                        return
                    
                try:
                    # Use lowercase field names to match PostgreSQL schema
                    rule_id = rule.get("SharingRuleID") or rule.get("id")
                    if not rule_id:
                        logger.warning(f"Skipping sharingrule record without SharingRuleID: {rule}")
                        continue
                    
                    # Validate required fields - UserID and ClientID are critical
                    user_id = rule.get("UserID")
                    client_id = rule.get("ClientID")
                    if not user_id or not client_id:
                        logger.warning(f"Skipping sharingrule {rule_id} - missing UserID or ClientID: {rule}")
                        continue
                    
                    # Create record with lowercase underscore field names for PostgreSQL
                    # FIXED: Changed sharingrule_id to sharing_rule_id to match database schema
                    sharingrule_record = {
                        # Primary identifier - FIXED: added underscore between sharing and rule
                        "sharing_rule_id": rule_id,
                        
                        # User and client relationship (REQUIRED)
                        "user_id": user_id,
                        "client_id": client_id,
                        
                        # Access control permissions
                        "access_level": rule.get("AccessLevel"),
                        "can_view": rule.get("CanView"),
                        "can_edit": rule.get("CanEdit"),
                        "can_delete": rule.get("CanDelete"),
                        
                        # Date range for rule validity
                        "start_date": rule.get("StartDate"),
                        "end_date": rule.get("EndDate"),
                        
                        # Status and metadata
                        "status": rule.get("Status"),
                        "created_by": rule.get("CreatedBy"),
                        "created_date": rule.get("CreatedDate"),
                        "modified_date": rule.get("ModifiedDate"),
                    }

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        sharingrule_record[meta_key] = meta_value

                    sharingrules_data.append(sharingrule_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing sharingrule record: {record_err}")
                    logger.error(f"SharingRule data: {rule}")
                    continue

            if test_mode and test_batch_delay > 0:
                logger.info(f"TEST MODE: Adding {test_batch_delay/2}s delay after processing batch {batch_counter}")
                time.sleep(test_batch_delay/2)
                
                if check_cancelled_callback and check_cancelled_callback():
                    logger.info(f"TEST MODE: Extraction cancelled after batch processing at batch {batch_counter}")
                    save_checkpoint(status="cancelled")
                    break
                    
                if check_paused_callback and check_paused_callback():
                    logger.info(f"TEST MODE: Extraction paused after batch processing at batch {batch_counter}")
                    save_checkpoint(status="paused")
                    break

            for sharingrule_record in sharingrules_data:
                yield sharingrule_record
                
            logger.info(f"Processed {batch_size} sharingrules (total: {total_records}) - batch {batch_counter}/{SHARINGRULE_MAX_BATCHES}")

            if should_save_checkpoint():
                save_checkpoint()

            if len(sharingrules) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting sharingrules at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for sharingrule_record in sharingrules_data:
                yield sharingrule_record
            raise

    logger.info(f"✓ SharingRules extraction complete: {total_records} records in {batch_counter} batches")
    save_checkpoint(status="completed")