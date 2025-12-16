import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
from datetime import datetime, timezone
from config import get_config


def extract_offices(
    api_service,
    extraction_metadata: Dict[str, Any],
    checkpoint_callback=None,
    filters=None,
    resume_from: Optional[Dict[str, Any]] = None,
    check_cancelled_callback=None,
    check_paused_callback=None,
) -> Iterator[Dict[str, Any]]:
    """
    Extract Office records from eMoney Identity API

    Yields office records with normalized field names,
    with extraction metadata added.
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    OFFICE_CHECKPOINT_FREQUENCY = config.OFFICE_CHECKPOINT_FREQUENCY
    OFFICE_PAUSE_CHECK_FREQUENCY = config.OFFICE_PAUSE_CHECK_FREQUENCY
    OFFICE_CANCEL_CHECK_FREQUENCY = config.OFFICE_CANCEL_CHECK_FREQUENCY
    OFFICE_MAX_BATCHES = config.OFFICE_MAX_BATCHES
    
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting Offices for org: {organization_id}")
    logger.info("=" * 60)
    
    if test_mode:
        logger.info(f"Running in TEST MODE with batch delay={test_batch_delay}s, record delay={test_record_delay}s")

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "office"
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
        return batch_counter % OFFICE_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % OFFICE_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % OFFICE_CHECKPOINT_FREQUENCY == 0

    offices_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            logger.info(f"TEST MODE: Adding {test_batch_delay}s delay before batch {batch_counter}")
            time.sleep(test_batch_delay)
        
        if batch_counter > OFFICE_MAX_BATCHES:
            logger.warning(f"Extraction of {entity} reached maximum batch limit ({OFFICE_MAX_BATCHES})")
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
            logger.info(f"Fetching offices (page: {page}, limit: {limit}) - batch {batch_counter}/{OFFICE_MAX_BATCHES}...")

            response = api_service.get_offices(page=page, limit=limit)

            if isinstance(response, dict):
                if "offices" in response:
                    offices = response.get("offices", [])
                elif "Data" in response:
                    offices = response.get("Data", [])
                else:
                    offices = []
            else:
                offices = response if isinstance(response, list) else []

            if not offices:
                logger.info("No more offices found")
                break

            batch_size = 0
            offices_data = []
            
            for office in offices:
                if test_mode and test_record_delay > 0:
                    time.sleep(test_record_delay)
                    
                if test_mode and batch_size % 5 == 0:
                    if check_cancelled_callback and check_cancelled_callback():
                        logger.info(f"TEST MODE: Extraction cancelled during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="cancelled")
                        for office_record in offices_data:
                            yield office_record
                        return
                    
                    if check_paused_callback and check_paused_callback():
                        logger.info(f"TEST MODE: Extraction paused during record processing at batch {batch_counter}, record {batch_size}")
                        save_checkpoint(status="paused")
                        for office_record in offices_data:
                            yield office_record
                        return
                    
                try:
                    # Handle eMoney Office format (flat JSON structure)
                    office_record = {
                        "id": office.get("OfficeID") or office.get("officeId") or office.get("id"),
                        "name": office.get("OfficeName") or office.get("officeName") or office.get("name"),
                        "code": office.get("OfficeCode") or office.get("officeCode") or office.get("code"),
                        "parent_office_id": office.get("ParentOfficeID") or office.get("parentOfficeId"),
                        "office_path": office.get("OfficePath") or office.get("officePath"),
                        "status": office.get("Status") or office.get("status"),
                        "address": office.get("Address") or office.get("address"),
                        "city": office.get("City") or office.get("city"),
                        "state": office.get("State") or office.get("state"),
                        "zip_code": office.get("ZipCode") or office.get("zipCode"),
                        "country": office.get("Country") or office.get("country"),
                        "phone": office.get("Phone") or office.get("phone"),
                        "email": office.get("Email") or office.get("email"),
                        "created_date": office.get("CreatedDate") or office.get("createdDate"),
                        "modified_date": office.get("ModifiedDate") or office.get("modifiedDate"),
                    }

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        office_record[meta_key] = meta_value

                    offices_data.append(office_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing office record: {record_err}")
                    logger.error(f"Office data: {office}")
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

            for office_record in offices_data:
                yield office_record
                
            logger.info(f"Processed {batch_size} offices (total: {total_records}) - batch {batch_counter}/{OFFICE_MAX_BATCHES}")

            if should_save_checkpoint():
                save_checkpoint()

            if len(offices) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting offices at page {page} - batch {batch_counter}: {e}")
            save_checkpoint(status="error")
            for office_record in offices_data:
                yield office_record
            raise

    logger.info(f"✓ Offices extraction complete: {total_records} records in {batch_counter} batches")
    save_checkpoint(status="completed")