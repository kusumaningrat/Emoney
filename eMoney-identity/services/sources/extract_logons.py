import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
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
    Extract Logon records from eMoney Identity API

    Yields logon records with normalized field names,
    with extraction metadata added.
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    LOGON_CHECKPOINT_FREQUENCY = config.LOGON_CHECKPOINT_FREQUENCY
    LOGON_PAUSE_CHECK_FREQUENCY = config.LOGON_PAUSE_CHECK_FREQUENCY
    LOGON_CANCEL_CHECK_FREQUENCY = config.LOGON_CANCEL_CHECK_FREQUENCY
    LOGON_MAX_BATCHES = config.LOGON_MAX_BATCHES
    
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Logons for org: {organization_id}")
    logger.info("=" * 60)

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "logon"
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
        return batch_counter % LOGON_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % LOGON_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % LOGON_CHECKPOINT_FREQUENCY == 0

    logons_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            time.sleep(test_batch_delay)
        
        if batch_counter > LOGON_MAX_BATCHES:
            logger.warning(f"Extraction reached maximum batch limit ({LOGON_MAX_BATCHES})")
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
            logger.info(f"Fetching logons (page: {page}, limit: {limit}) - batch {batch_counter}")

            response = api_service.get_logons(page=page, limit=limit)

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
                        save_checkpoint(status="cancelled")
                        for logon_record in logons_data:
                            yield logon_record
                        return
                    
                    if check_paused_callback and check_paused_callback():
                        save_checkpoint(status="paused")
                        for logon_record in logons_data:
                            yield logon_record
                        return
                    
                try:
                    # Handle eMoney Logon format (flat JSON structure)
                    logon_record = {
                        "id": logon.get("LogonID") or logon.get("logonId") or logon.get("id"),
                        "user_id": logon.get("UserID") or logon.get("userId"),
                        "username": logon.get("Username") or logon.get("username"),
                        "logon_timestamp": logon.get("LogonTimestamp") or logon.get("logonTimestamp"),
                        "logoff_timestamp": logon.get("LogoffTimestamp") or logon.get("logoffTimestamp"),
                        "session_duration": logon.get("SessionDuration") or logon.get("sessionDuration"),
                        "ip_address": logon.get("IPAddress") or logon.get("ipAddress"),
                        "user_agent": logon.get("UserAgent") or logon.get("userAgent"),
                        "device_type": logon.get("DeviceType") or logon.get("deviceType"),
                        "location": logon.get("Location") or logon.get("location"),
                        "status": logon.get("Status") or logon.get("status"),
                        "authentication_method": logon.get("AuthenticationMethod") or logon.get("authenticationMethod"),
                        "is_successful": logon.get("IsSuccessful") or logon.get("isSuccessful"),
                        "failure_reason": logon.get("FailureReason") or logon.get("failureReason"),
                        "created_date": logon.get("CreatedDate") or logon.get("createdDate"),
                    }

                    # Handle session metadata if present
                    if logon.get("SessionMetadata") or logon.get("sessionMetadata"):
                        metadata = logon.get("SessionMetadata") or logon.get("sessionMetadata")
                        if isinstance(metadata, dict):
                            logon_record["session_metadata"] = json.dumps(metadata)

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
                time.sleep(test_batch_delay/2)
                
                if check_cancelled_callback and check_cancelled_callback():
                    save_checkpoint(status="cancelled")
                    break
                    
                if check_paused_callback and check_paused_callback():
                    save_checkpoint(status="paused")
                    break

            for logon_record in logons_data:
                yield logon_record
                
            logger.info(f"Processed {batch_size} logons (total: {total_records})")

            if should_save_checkpoint():
                save_checkpoint()

            if len(logons) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting logons at page {page}: {e}")
            save_checkpoint(status="error")
            for logon_record in logons_data:
                yield logon_record
            raise

    logger.info(f"✓ Logons extraction complete: {total_records} records")
    save_checkpoint(status="completed")