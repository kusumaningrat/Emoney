import logging
import time
from typing import Dict, Any, Iterator, Optional
from datetime import datetime, timezone
from config import get_config


def extract_logons(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract Logon records from eMoney Service API

    Yields logon records with lowercase underscore field names for PostgreSQL,
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
    LOGON_CHECKPOINT_FREQUENCY = config.LOGON_CHECKPOINT_FREQUENCY
    LOGON_PAUSE_CHECK_FREQUENCY = config.LOGON_PAUSE_CHECK_FREQUENCY
    LOGON_CANCEL_CHECK_FREQUENCY = config.LOGON_CANCEL_CHECK_FREQUENCY
    LOGON_MAX_BATCHES = config.LOGON_MAX_BATCHES
    
    # Check if we're in test mode and get test delay settings
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Logons for org: {organization_id}")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"Running in TEST MODE with batch delay={test_batch_delay}s, record delay={test_record_delay}s")

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "logon"
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
        return batch_counter % LOGON_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % LOGON_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % LOGON_CHECKPOINT_FREQUENCY == 0

    logons_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > LOGON_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({LOGON_MAX_BATCHES})")
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
            logger.info(f"Fetching logons (page: {page}, limit: {limit}) - batch {batch_counter}/{LOGON_MAX_BATCHES}...")

            response = api_service.get_logons(page=page, page_size=limit)

            # Handle different response formats
            if isinstance(response, dict):
                if "logons" in response:
                    logons = response.get("logons", [])
                elif "Data" in response:
                    logons = response.get("Data", [])
                else:
                    logons = []
            else:
                logons = response if isinstance(response, list) else []

            if not logons:
                logger.info("No more logons found")
                break

            batch_size = 0
            logons_data = []
            
            for logon in logons:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for logon_record in logons_data:
                            yield logon_record
                        return
                    
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for logon_record in logons_data:
                            yield logon_record
                        return
                    
                try:
                    # Use lowercase field names to match PostgreSQL schema
                    logon_id = logon.get("LogonID") or logon.get("id")
                    if not logon_id:
                        logger.warning(f"Skipping logon record without LogonID: {logon}")
                        continue
                    
                    # Create record with lowercase underscore field names for PostgreSQL
                    logon_record = {
                        "logon_id": logon_id,
                        "user_id": logon.get("UserID"),
                        "logon_time": logon.get("LogonTime"),
                        "logout_time": logon.get("LogoutTime"),
                        "ip_address": logon.get("IPAddress"),
                        "device_type": logon.get("DeviceType"),
                        "browser": logon.get("Browser"),
                        "location": logon.get("Location"),
                        "session_duration": logon.get("SessionDuration"),
                        "is_successful": logon.get("IsSuccessful"),
                        "created_date": logon.get("CreatedDate"),
                    }

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        logon_record[meta_key] = meta_value

                    logons_data.append(logon_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing logon record: {record_err}")
                    logger.error(f"Logon data: {logon}")
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

            for logon_record in logons_data:
                yield logon_record
                
            logger.info(f"Processed {batch_size} logons (total: {total_records}) - batch {batch_counter}/{LOGON_MAX_BATCHES}")

            if should_save_checkpoint():
                save_checkpoint()

            if len(logons) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting logons at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for logon_record in logons_data:
                yield logon_record
            raise

    logger.info(f"✓ Logons extraction complete: {total_records} records in {batch_counter} batches")
    save_checkpoint(status="completed")