import logging
import time
from typing import Dict, Any, Iterator, Optional
import json
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
    Extract SharingRule records from eMoney Identity API

    Yields sharingrule records with normalized field names,
    with extraction metadata added.
    """
    logger = logging.getLogger(__name__)

    job_id = extraction_metadata.get("_scan_id", "unknown")
    organization_id = extraction_metadata.get("_tenant_id", "unknown")

    config = get_config()
    SHARING_RULE_CHECKPOINT_FREQUENCY = config.SHARING_RULE_CHECKPOINT_FREQUENCY
    SHARING_RULE_PAUSE_CHECK_FREQUENCY = config.SHARING_RULE_PAUSE_CHECK_FREQUENCY
    SHARING_RULE_CANCEL_CHECK_FREQUENCY = config.SHARING_RULE_CANCEL_CHECK_FREQUENCY
    SHARING_RULE_MAX_BATCHES = config.SHARING_RULE_MAX_BATCHES
    
    test_mode = getattr(config, 'TESTING', False)
    test_batch_delay = getattr(config, 'TEST_BATCH_DELAY_SECONDS', 5)
    test_record_delay = getattr(config, 'TEST_RECORD_DELAY_SECONDS', 0.1)

    logger.info("=" * 60)
    logger.info(f"Extracting SharingRules for org: {organization_id}")
    logger.info("=" * 60)

    page = 1
    limit = filters.get("batch_size", 100) if filters else 100
    total_records = 0
    entity = "sharingrule"
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
        return batch_counter % SHARING_RULE_CANCEL_CHECK_FREQUENCY == 0

    def should_check_paused():
        return batch_counter % SHARING_RULE_PAUSE_CHECK_FREQUENCY == 0
    
    def should_save_checkpoint():
        return batch_counter % SHARING_RULE_CHECKPOINT_FREQUENCY == 0

    sharingrules_data = []
    
    while True:
        batch_counter += 1
        
        if test_mode and test_batch_delay > 0:
            time.sleep(test_batch_delay)
        
        if batch_counter > SHARING_RULE_MAX_BATCHES:
            logger.warning(f"Extraction reached maximum batch limit ({SHARING_RULE_MAX_BATCHES})")
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
            logger.info(f"Fetching sharingrules (page: {page}, limit: {limit}) - batch {batch_counter}")

            response = api_service.get_sharingrules(page=page, limit=limit)

            if isinstance(response, dict):
                if "sharingrules" in response:
                    sharingrules = response.get("sharingrules", [])
                elif "sharingRules" in response:
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
                    
                try:
                    # Handle eMoney SharingRule format (flat JSON structure)
                    rule_record = {
                        "id": rule.get("SharingRuleID") or rule.get("sharingRuleId") or rule.get("RuleID") or rule.get("ruleId") or rule.get("id"),
                        "user_id": rule.get("UserID") or rule.get("userId"),
                        "client_id": rule.get("ClientID") or rule.get("clientId"),
                        "household_id": rule.get("HouseholdID") or rule.get("householdId"),
                        "access_level": rule.get("AccessLevel") or rule.get("accessLevel"),
                        "can_view": rule.get("CanView") or rule.get("canView"),
                        "can_edit": rule.get("CanEdit") or rule.get("canEdit"),
                        "can_delete": rule.get("CanDelete") or rule.get("canDelete"),
                        "start_date": rule.get("StartDate") or rule.get("startDate") or rule.get("EffectiveDate") or rule.get("effectiveDate"),
                        "end_date": rule.get("EndDate") or rule.get("endDate") or rule.get("ExpirationDate") or rule.get("expirationDate"),
                        "status": rule.get("Status") or rule.get("status"),
                        "created_by": rule.get("CreatedBy") or rule.get("createdBy"),
                        "created_date": rule.get("CreatedDate") or rule.get("createdDate"),
                        "modified_date": rule.get("ModifiedDate") or rule.get("modifiedDate"),
                    }

                    # Add extraction metadata
                    for meta_key, meta_value in extraction_metadata.items():
                        rule_record[meta_key] = meta_value

                    sharingrules_data.append(rule_record)
                    total_records += 1
                    batch_size += 1

                except Exception as record_err:
                    logger.error(f"Error processing sharingrule record: {record_err}")
                    logger.error(f"SharingRule data: {rule}")
                    continue

            for rule_record in sharingrules_data:
                yield rule_record
                
            logger.info(f"Processed {batch_size} sharingrules (total: {total_records})")

            if should_save_checkpoint():
                save_checkpoint()

            if len(sharingrules) < limit:
                break

            page += 1

        except Exception as e:
            logger.error(f"Error extracting sharingrules at page {page}: {e}")
            save_checkpoint(status="error")
            for rule_record in sharingrules_data:
                yield rule_record
            raise

    logger.info(f"✓ SharingRules extraction complete: {total_records} records")
    save_checkpoint(status="completed")